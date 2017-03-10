#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS Module Constants."""

import logging
import os

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2017 Greg Albrecht and Contributors'
__license__ = 'Apache License, Version 2.0'


if bool(os.environ.get('DEBUG_APRS')) or bool(os.environ.get('DEBUG_ALL')):
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO

LOG_FORMAT = logging.Formatter(
    ('%(asctime)s aprs %(levelname)s %(name)s.%(funcName)s:%(lineno)d - '
     '%(message)s'))

APRSIS_SERVER = 'rotate.aprs.net'
APRSIS_FILTER_PORT = 14580
APRSIS_RX_PORT = 8080

APRSIS_SW_VERSION = 'APRS Python Module'
APRSIS_URL = 'http://srvr.aprs-is.net:8080'

APRSIS_HTTP_HEADERS = {
    'content-type': 'application/octet-stream',
    'accept': 'text/plain'
}

RECV_BUFFER = 1024

UI_PROTOCOL_ID = b'\xF0'
FLAG = b'\x7E'
CONTROL_FIELD = b'\x03'
