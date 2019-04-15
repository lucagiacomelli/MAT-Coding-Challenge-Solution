# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019
# All rights reserved.
#
# Solution for the MAT-Coding-Challenge.
# This file contains the data processor as a component of the given stack of services.
# This component subscribes to a provided MQTT broker and consumes data from a particular topic.
#
# Author: luca.giacomelli@gmail.com (Luca Giacomelli)

import os
import json
from utilities_geo import hvs_distance

import paho.mqtt.client as mqttcl


# Our data storage. It can be substitute with
# an in-memory store (e.g. Redis) or a Database (e.g. MongoDB)
status_cars = {}

# message in case of car X overtakes
message_up = "Car {} races ahead in a dramatic overtake. Now it's in position {}"

# message in case of car X be overtaken
message_down = "Car {} has been overtaken and now is in position {}"


def send_event(client, timestamp_car, text_event):
    """
    Auxiliary method to send events to the broker.
    :param client: MQTT Client
    :param timestamp_car: long with epoch timestamp in milliseconds
    :param text_event: string with the text of the event to send
    :return:
    """

    if text_event is None:
        return -1, -1

    topic_events = os.getenv("MQTT_TOPIC_events", "events")
    message_events = dict(timestamp=timestamp_car, text=text_event)
    return client.publish(topic_events, json.dumps(message_events).encode("utf-8"))


def send_car_status(client, timestamp_car, car_index, type_status, value_status):
    """
    Auxiliary method to send the car status to the broker.
    :param client: MQTT Client
    :param timestamp_car: long with epoch timestamp in milliseconds
    :param car_index: integer with the car identifier
    :param type_status: "POSITION"| "SPEED"
    :param value_status: value of the status
    :return:
    """

    if car_index < 0 or value_status < 0:
        return -1, -1

    topic_car_status = os.getenv("MQTT_TOPIC_CAR_STATUS", "carStatus")
    message_car_status = dict(
        timestamp=timestamp_car,
        carIndex=car_index,
        type=type_status,
        value=value_status,
    )
    return client.publish(
        topic_car_status, json.dumps(message_car_status).encode("utf-8")
    )


def parse_lat_long(location):
    """
    Auxiliary method to parse a location in a tuple (lat, long)
    :param location: dictionary with the location
    :return: a tuple (double, double)
    """

    return location["lat"], location["long"]


def init_car_data(client, car_index, timestamp_car, location_car):
    """
    Method to initialise the data for each car
    :param client: MQTT client
    :param car_index: integer with the car identifier
    :param timestamp_car: long with epoch timestamp in milliseconds
    :param location_car: dictionary with the location
    :return:
    """

    status_cars[car_index] = dict(
        last_location=location_car,
        last_timestamp=timestamp_car,
        distance=0,
        counter_for_events=0,
        position=0,
        updated=False,
    )
    send_car_status(client, car_index, "SPEED", 0)
    send_car_status(client, timestamp_car, car_index, "POSITION", 0)


def send_position_event(client, timestamp, car_index, old_position, new_position):
    """
    Method to send the event to the broker.
    A new message is generated according to the old and new position.
    :param client: MQTT Client
    :param timestamp: long with epoch timestamp in milliseconds
    :param car_index: integer with the car identifier
    :param old_position: integer in [1, num cars]
    :param new_position: integer in [1, num cars]
    :return:
    """

    if old_position != 0:
        if old_position < new_position:
            send_event(client, timestamp, message_up.format(car_index, new_position))
        else:
            send_event(client, timestamp, message_down.format(car_index, new_position))


def check_send_positions(client, timestamp_car):
    """
    Method to check the positions of the cars in a precise
    timestamp and send new positions, if different from the
    previous ones, to the broker.
    :param client: MQTT client
    :param timestamp_car: long with epoch timestamp in milliseconds
    :return:
    """

    distance_to_sort = []
    for car in status_cars:
        status_cars[car]["updated"] = False
        distance_to_sort.append(
            dict(distance=status_cars[car]["distance"], car_index=car)
        )

    distance_to_sort.sort(key=lambda x: x["distance"])
    for i in range(len(distance_to_sort)):
        car_index = distance_to_sort[i]["car_index"]
        old_position = status_cars[car_index]["position"]
        new_position = len(distance_to_sort) - i

        if old_position != new_position:
            send_car_status(client, timestamp_car, car_index, "POSITION", new_position)
            send_position_event(client, timestamp_car, car_index, old_position, new_position)

    for i in range(len(distance_to_sort)):
        status_cars[distance_to_sort[i]["car_index"]]["position"] = (
            len(distance_to_sort) - i
        )


def on_message_from_broker(client, obj, msg):
    """
    Method to handle the messages from the broker.
    At every message we publish the messages for the other topics
    :param client: MQTT client
    :param obj: object of the connection
    :param msg: message from the broker
    :return:
    """

    message_payload = json.loads(msg.payload.decode("utf-8"))
    # print("\n\n\n", message_payload)

    car_index = message_payload["carIndex"]
    timestamp_car = message_payload["timestamp"]
    location_car = message_payload["location"]

    # We assume that every car is initialise in the same position at the beginning
    if car_index not in status_cars:
        init_car_data(client, car_index, timestamp_car, location_car)
    else:

        # compute the Haversine distance in meters between the locations
        new_distance = hvs_distance(
            parse_lat_long(status_cars[car_index]["last_location"]),
            parse_lat_long(location_car),
        )

        # convert from meters to miles
        miles = new_distance / 1609.34

        # delta time in hours
        delta_time = (timestamp_car - status_cars[car_index]["last_timestamp"]) / (
            1000 * 3600
        )

        new_speed = miles / delta_time

        # we have to handle failures here
        send_car_status(client, timestamp_car, car_index, "SPEED", new_speed)

        # update the storage after successful sending
        status_cars[car_index]["last_location"] = location_car
        status_cars[car_index]["last_timestamp"] = timestamp_car
        status_cars[car_index]["distance"] += new_distance
        status_cars[car_index]["speed"] = new_speed
        status_cars[car_index]["updated"] = True

        # check all cars info have been received.
        # It can be done also in other ways, counters, semaphores...

        # We consider that the stream of data
        # is in a round-robin form: in the stream of events we have the information
        # about all the cars every X milliseconds. We assume that in every interval
        # it is not possible that one car info is missing.
        # Therefore every car index will update the 'updated' field once per interval
        # before resetting it.
        all_updated = True
        for car in status_cars:
            if not status_cars[car]["updated"]:
                all_updated = False
                break

        if all_updated:
            check_send_positions(client, timestamp_car)


def on_connect_to_broker(client, userdata, flags, rc):
    # Start subscribe, with QoS level 0
    client.subscribe(os.getenv("MQTT_TOPIC", "carCoordinates"), 0)


if __name__ == "__main__":
    mqtt_client = mqttcl.Client(clean_session=True)

    mqtt_client.on_message = on_message_from_broker
    mqtt_client.on_connect = on_connect_to_broker

    mqtt_client.connect("127.0.0.1")

    # Continue the network loop, exit when an error occurs
    rc = 0
    while rc == 0:
        rc = mqtt_client.loop()



