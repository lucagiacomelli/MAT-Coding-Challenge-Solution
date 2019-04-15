# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019
# All rights reserved.
#
# File for geo-spatial utilities.
#
# Author: luca.giacomelli@gmail.com (Luca Giacomelli)


def hvs_distance(origin, destination):
    """
    Method to calculate the Haversine formula: it allows to find the distance between two
    locations expressed in (latitude, longitude)
    :param origin: (double, double) of the source location
    :param destination: (double, double) of the end location
    :return: distance in meters
    """
    import math

    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    flat1 = float(lat1)
    flat2 = float(lat2)
    flon1 = float(lon1)
    flon2 = float(lon2)

    dlat = math.radians(flat2 - flat1)
    dlon = math.radians(flon2 - flon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(
        math.radians(flat1)
    ) * math.cos(math.radians(flat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c
    return d*1000
