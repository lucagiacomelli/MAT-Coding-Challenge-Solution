# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019
# All rights reserved.
#
#
# Author: luca.giacomelli@gmail.com (Luca Giacomelli)
from data_processor import send_car_status
import paho.mqtt.client as mqttcl


def test_send_position():
    mqtt_client = mqttcl.Client(clean_session=True)
    mqtt_client.connect("127.0.0.1")
    result = send_car_status(mqtt_client, 1541693114862, 3, "POSITION", 2)
    mqtt_client.disconnect()
    assert result[0] == 0


def test_send_negative_var_index():
    mqtt_client = mqttcl.Client(clean_session=True)
    mqtt_client.connect("127.0.0.1")
    result = send_car_status(mqtt_client, 1541693114862, -3, "POSITION", 2)
    mqtt_client.disconnect()
    assert result[0] == -1


def test_send_negative_position():
    mqtt_client = mqttcl.Client(clean_session=True)
    mqtt_client.connect("127.0.0.1")
    result = send_car_status(mqtt_client, 1541693114862, 3, "POSITION", -2)
    mqtt_client.disconnect()
    assert result[0] == -1


def test_send_speed():
    mqtt_client = mqttcl.Client(clean_session=True)
    mqtt_client.connect("127.0.0.1")
    result = send_car_status(mqtt_client, 1541693114862, 3, "SPEED", 222)
    mqtt_client.disconnect()
    assert result[0] == 0


def test_send_negative_speed():
    mqtt_client = mqttcl.Client(clean_session=True)
    mqtt_client.connect("127.0.0.1")
    result = send_car_status(mqtt_client, 1541693114862, 3, "SPEED", -222)
    mqtt_client.disconnect()
    assert result[0] == -1
