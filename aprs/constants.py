#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Constants for APRS Module.
"""

__author__ = 'Greg Albrecht W2GMD <gba@orionlabs.co>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2015 Orion Labs, Inc.'


import logging


APRSIS_URL = 'http://srvr.aprs-is.net:8080'
APRSIS_HTTP_HEADERS = {
    'content-type': 'application/octet-stream',
    'accept': 'text/plain'
}
APRSIS_SERVER = 'rotate.aprs.net'
APRSIS_FILTER_PORT = 14580
APRSIS_RX_PORT = 8080

RECV_BUFFER = 1024


LOG_LEVEL = logging.INFO
LOG_FORMAT = logging.Formatter(
    ('%(asctime)s %(levelname)s %(name)s.%(funcName)s:%(lineno)d - '
     '%(message)s'))

GPS_WARM_UP = 5
