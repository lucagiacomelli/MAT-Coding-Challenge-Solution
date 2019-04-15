# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019
# All rights reserved.
#
#
# Author: luca.giacomelli@gmail.com (Luca Giacomelli)
from data_processor import send_event
import paho.mqtt.client as mqttcl


def test_send():
    mqtt_client = mqttcl.Client(clean_session=True)
    mqtt_client.connect("127.0.0.1")
    result = send_event(mqtt_client, 1541693114862, "Car 2 races ahead of Car 4 in a dramatic overtake.")
    mqtt_client.disconnect()
    assert result[0] == 0


def test_send_null_event():
    mqtt_client = mqttcl.Client(clean_session=True)
    mqtt_client.connect("127.0.0.1")
    result = send_event(mqtt_client, 1541693114862, None)
    mqtt_client.disconnect()
    assert result[0] == -1
