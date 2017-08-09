#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS Module APRS-IS Bindings Tests."""

import unittest  # pylint: disable=R0801

import httpretty

from .context import aprs  # pylint: disable=R0801
from .context import aprs_test_classes  # pylint: disable=R0801

from . import constants  # pylint: disable=R0801

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'  # NOQA pylint: disable=R0801
__copyright__ = 'Copyright 2017 Greg Albrecht and Contributors'  # NOQA pylint: disable=R0801
__license__ = 'Apache License, Version 2.0'  # NOQA pylint: disable=R0801


class APRSTest(aprs_test_classes.APRSTestClass):  # pylint: disable=R0904

    """Tests for Python APRS-IS Bindings."""

    @httpretty.httprettified
    def test_fake_good_auth(self):
        """
        Tests authenticating against APRS-IS using a valid call+pass.
        """
        httpretty.HTTPretty.register_uri(
            httpretty.HTTPretty.POST,
            self.fake_server,
            status=204
        )

        aprs_conn = aprs.HTTP(
            user=self.fake_callsign,
            url=self.fake_server
        )
        aprs_conn.start()

        frame = aprs.parse_frame(
            '>'.join([
                self.fake_callsign,
                'APRS,TCPIP*:=3745.00N/12227.00W-test_fake_good_auth'
            ])
        )
        self._logger.debug('frame="%s"', frame)

        result = aprs_conn.send(frame)

        self.assertTrue(result)

    @httpretty.httprettified
    def test_fake_bad_auth_http(self):
        """
        Tests authenticating against APRS-IS using an invalid call+pass.
        """
        httpretty.HTTPretty.register_uri(
            httpretty.HTTPretty.POST,
            self.fake_server,
            status=401
        )

        aprs_conn = aprs.HTTP(
            user=self.fake_callsign,
            url=self.fake_server
        )
        aprs_conn.start()

        msg = '>'.join([
            self.fake_callsign,
            'APRS,TCPIP*:=3745.00N/12227.00W-Simulated Location'
        ])
        self._logger.debug(locals())

        result = aprs_conn.send(msg)

        self.assertFalse(result)

    @unittest.skip('Test only works with real server.')
    def test_more(self):
        """
        Tests APRS-IS binding against a real APRS-IS server.
        """
        aprs_conn = aprs.HTTP(
            user=self.real_callsign,
            url=self.real_server
        )
        aprs_conn.start()

        msg = '>'.join([
            self.real_callsign,
            'APRS,TCPIP*:=3745.00N/12227.00W-Simulated Location'
        ])
        self._logger.debug(locals())

        result = aprs_conn.send(msg)

        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
