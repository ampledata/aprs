#!/usr/bin/env python


import random
import unittest
import logging
import logging.handlers

import httpretty

from .context import aprs


ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
NUMBERS = '0123456789'
POSITIVE_NUMBERS = NUMBERS[1:]
ALPHANUM = ''.join([ALPHABET, NUMBERS])


class APRSTest(unittest.TestCase):
    """Tests for Python APRS Bindings."""

    logger = logging.getLogger('aprs.tests')
    logger.addHandler(logging.StreamHandler())

    def random(self, length=8, alphabet=ALPHANUM):
        return ''.join(random.choice(alphabet) for _ in xrange(length))

    def setUp(self):
        self.fake_server = ''.join([
            'http://localhost:',
            self.random(4, POSITIVE_NUMBERS),
            '/'
        ])

        self.fake_callsign = ''.join([
            self.random(1, 'KWN'),
            self.random(1, NUMBERS),
            self.random(3, ALPHABET),
            '-',
            self.random(1, POSITIVE_NUMBERS)
        ])

        self.real_server = 'http://localhost:14580'
        self.real_callsign = '-'.join(['W2GMD', self.random(1, '123456789')])

        self.logger.debug("fake_server=%s fake_callsign=%s"
                          % (self.fake_server, self.fake_callsign))

    @httpretty.httprettified
    def test_fake_good_auth(self):
        httpretty.HTTPretty.register_uri(
            httpretty.HTTPretty.POST,
            self.fake_server,
            status=204
        )

        aprs_conn = aprs.APRS(
            user=self.fake_callsign,
            input_url=self.fake_server
        )

        msg = '>'.join([
            self.fake_callsign,
            'APRS,TCPIP*:=3745.00N/12227.00W-Simulated Location'
        ])
        self.logger.debug(locals())

        result = aprs_conn.send(msg)

        self.assertTrue(result)

    @httpretty.httprettified
    def test_fake_bad_auth(self):
        httpretty.HTTPretty.register_uri(
            httpretty.HTTPretty.POST,
            self.fake_server,
            status=401
        )

        aprs_conn = aprs.APRS(
            user=self.fake_callsign,
            input_url=self.fake_server
        )

        msg = '>'.join([
            self.fake_callsign,
            'APRS,TCPIP*:=3745.00N/12227.00W-Simulated Location'
        ])
        self.logger.debug(locals())

        result = aprs_conn.send(msg)

        self.assertFalse(result)

    def test_more(self):
        aprs_conn = aprs.APRS(
            user=self.real_callsign,
            input_url=self.real_server
        )

        msg = '>'.join([
            self.real_callsign,
            'APRS,TCPIP*:=3745.00N/12227.00W-Simulated Location'
        ])
        self.logger.debug(locals())

        result = aprs_conn.send(msg)

        self.assertFalse(result)
