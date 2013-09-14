#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Greg Albrecht W2GMD <gba@onbeep.com>'
__copyright__ = 'Copyright 2013 OnBeep, Inc.'
__license__ = 'Apache 2.0'


import logging
import logging.handlers

import requests

import kiss

import aprs.constants


class APRS(object):

    logger = logging.getLogger('aprs')
    logger.addHandler(logging.StreamHandler())

    def __init__(self, user, password='-1', input_url=None):
        self._url = input_url or aprs.constants.APRSIS_URL
        self._auth = ' '.join(['user', user, 'pass', password])

    def send(self, message, headers=None):
        headers = headers or aprs.constants.APRSIS_HTTP_HEADERS
        content = "\n".join([self._auth, message])

        result = requests.post(self._url, data=content, headers=headers)

        return result.status_code == 204


class APRSKISS(kiss.KISS):

    def write(self, frame):
        encoded_frame = aprs.util.encode_frame(frame)
        super(APRSKISS, self).write(encoded_frame)
