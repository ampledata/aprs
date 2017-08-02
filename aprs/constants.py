#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS Module Constants."""

import logging
import os

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'  # NOQA pylint: disable=R0801
__copyright__ = 'Copyright 2017 Greg Albrecht and Contributors'  # NOQA pylint: disable=R0801
__license__ = 'Apache License, Version 2.0'  # NOQA pylint: disable=R0801


if bool(os.environ.get('DEBUG')):
    LOG_LEVEL = logging.DEBUG
    logging.debug('Debugging Enabled via DEBUG Environment Variable.')
else:
    LOG_LEVEL = logging.INFO

LOG_FORMAT = logging.Formatter(
    ('%(asctime)s aprs %(levelname)s %(name)s.%(funcName)s:%(lineno)d - '
     '%(message)s'))

APRSIS_SERVERS = ['rotate.aprs.net', 'noam.aprs2.net']

APRSIS_SW_VERSION = 'APRS Python Module'

APRSIS_HTTP_HEADERS = {
    'content-type': 'application/octet-stream',
    'accept': 'text/plain'
}

APRSIS_FILTER_PORT = int(os.environ.get('APRSIS_FILTER_PORT', 14580))
APRSIS_RX_PORT = int(os.environ.get('APRSIS_RX_PORT', 8080))
APRSIS_URL = os.environ.get('APRSIS_URL', 'http://srvr.aprs-is.net:8080')

RECV_BUFFER = int(os.environ.get('RECV_BUFFER', 1024))

UI_PROTOCOL_ID = b'\xF0'
FLAG = b'\x7E'
CONTROL_FIELD = b'\x03'
