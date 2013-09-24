#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""APRS Class Definitions"""

__author__ = 'Greg Albrecht W2GMD <gba@onbeep.com>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2013 OnBeep, Inc.'


import logging
import logging.handlers

import requests

import kiss

import aprs.constants
import aprs.util


class APRS(object):

    """APRS-IS Object."""

    logger = logging.getLogger(__name__)
    logger.setLevel(aprs.constants.LOG_LEVEL)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(aprs.constants.LOG_LEVEL)
    formatter = logging.Formatter(aprs.constants.LOG_FORMAT)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.propagate = False

    def __init__(self, user, password='-1', input_url=None):
        self._url = input_url or aprs.constants.APRSIS_URL
        self._auth = ' '.join(['user', user, 'pass', password])

    def send(self, message, headers=None):
        """
        Sends message to APRS-IS send-only interface.

        :param message: Message to send to APRS-IS.
        :param headers: Optional headers to post.
        :type message: str
        :type headers: dict

        :return: True on 204 success, False otherwise.
        :rtype: bool
        """
        self.logger.debug('message=%s headers=%s', message, headers)

        headers = headers or aprs.constants.APRSIS_HTTP_HEADERS
        content = "\n".join([self._auth, message])

        result = requests.post(self._url, data=content, headers=headers)

        return result.status_code == 204


class APRSKISS(kiss.KISS):

    """APRS interface for KISS serial devices."""

    def write(self, frame):
        """Writes APRS-encoded frame to KISS device.

        :param frame: APRS frame to write to KISS device.
        :type frame: str
        """
        encoded_frame = aprs.util.encode_frame(frame)
        super(APRSKISS, self).write(encoded_frame)
