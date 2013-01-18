#!/usr/bin/env python


import logging
import logging.handlers

import requests


class APRS(object):

    logger = logging.getLogger('aprs')
    logger.addHandler(logging.StreamHandler())

    def __init__(self, user, password=-1, input_url=None):
        self._url = input_url or 'http://srvr.aprs-is.net:8080'
        self._auth = "user %s pass %s" % (user, password)

    def send(self, message):
        headers = {
            'content-type': 'application/octet-stream',
            'accept': 'text/plain'
        }

        content = "\n".join([self._auth, message])

        result = requests.post(self._url, data=content, headers=headers)

        return result.status_code == 204
