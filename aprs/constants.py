#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Constants for APRS Module.
"""

__author__ = 'Greg Albrecht W2GMD <gba@onbeep.com>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2013 OnBeep, Inc.'


import logging


APRSIS_URL = 'http://srvr.aprs-is.net:8080'
APRSIS_HTTP_HEADERS = {
    'content-type': 'application/octet-stream',
    'accept': 'text/plain'
}
APRSIS_SERVER = 'rotate.aprs.net'
APRSIS_FILTER_PORT = 14580

RECV_BUFFER = 1024


LOG_LEVEL = logging.INFO
LOG_FORMAT = ('%(asctime)s %(levelname)s %(name)s.%(funcName)s:%(lineno)d'
              ' - %(message)s')
