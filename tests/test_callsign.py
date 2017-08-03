#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS Module APRS Callsign Tests."""

import unittest  # pylint: disable=R0801

from .context import aprs  # pylint: disable=R0801
from .context import aprs_test_classes  # pylint: disable=R0801

from . import constants  # pylint: disable=R0801

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'  # NOQA pylint: disable=R0801
__copyright__ = 'Copyright 2017 Greg Albrecht and Contributors'  # NOQA pylint: disable=R0801
__license__ = 'Apache License, Version 2.0'  # NOQA pylint: disable=R0801


class CallsignTestCase(aprs_test_classes.APRSTestClass):  # NOQA pylint: disable=R0904

    """Tests for Python APRS Callsign."""

    def test_ax25_extract_callsign_source(self):
        """
        Tests extracting the source callsign from a AX.25 Encoded APRS frame
        using `aprs.Callsign`.
        """
        callsign = 'W2GMD'
        ssid = str(6)
        full = '-'.join([callsign, ssid])

        extracted_callsign = aprs.Callsign(self.test_hex_frame[7:])

        self.assertEqual(full, str(extracted_callsign))
        self.assertEqual(callsign, extracted_callsign.callsign)
        self.assertEqual(ssid, extracted_callsign.ssid)

    def test_ax25_extract_callsign_dest(self):
        """
        Tests extracting the destination callsign from a AX.25 Encoded APRS
        frame using `aprs.Callsign`.
        """
        extracted_callsign = aprs.Callsign(self.test_hex_frame)
        self.assertEqual(extracted_callsign.callsign, 'APRX24')

    def test_full_callsign_with_ssid(self):
        """
        Tests creating a full callsign string from a callsign+ssid using
        `aprs.Callsign`.
        """
        callsign = 'W2GMD-1'
        full_callsign = aprs.Callsign(callsign)
        self.assertEqual(str(full_callsign), callsign)

    def test_full_callsign_with_ssid_0(self):
        """
        Tests creating a full callsign string from a callsign using
        `aprs.Callsign`.
        """
        callsign = 'W2GMD-0'
        full_callsign = aprs.Callsign(callsign)
        self.assertEqual(str(full_callsign), callsign.split('-')[0])

    def test_full_callsign_sans_ssid(self):
        """
        Tests creating a full Callsign string from a Callsign sans SSID.
        """
        callsign = 'W2GMD'
        full_callsign = aprs.Callsign(callsign)
        self.assertEqual(str(full_callsign), callsign)

    def test_ax25_encode(self):
        """
        Tests AX.25 Encoding a Digipeated Callsign.
        """
        callsign = 'W2GMD-1'
        callsign_obj = aprs.Callsign(callsign)
        self.assertFalse(callsign_obj.digi)
        self.assertEqual(callsign_obj.callsign, 'W2GMD')
        self.assertEqual(callsign_obj.ssid, '1')

        encoded_callsign = callsign_obj.encode_ax25()
        self.assertEqual(
            encoded_callsign, bytearray(b'\xaed\x8e\x9a\x88\x00b'))

        decoded_callsign = aprs.Callsign(encoded_callsign)
        self.assertEqual(str(decoded_callsign), callsign)
        self.assertFalse(decoded_callsign.digi)
        self.assertEqual(decoded_callsign.callsign, 'W2GMD')
        self.assertEqual(decoded_callsign.ssid, '1')

    def test_ax25_encode_digipeated(self):
        """
        Tests AX.25 Encoding a Digipeated Callsign.
        """
        callsign = 'W2GMD*'
        callsign_obj = aprs.Callsign(callsign)
        self.assertTrue(callsign_obj.digi)
        self.assertEqual(callsign_obj.callsign, 'W2GMD')
        self.assertEqual(callsign_obj.ssid, '0')

        encoded_callsign = callsign_obj.encode_ax25()
        self.assertEqual(
            encoded_callsign, bytearray(b'\xaed\x8e\x9a\x88\x00\xe0'))

        decoded_callsign = aprs.Callsign(encoded_callsign)
        self.assertEqual(str(decoded_callsign), callsign)
        self.assertTrue(decoded_callsign.digi)
        self.assertEqual(decoded_callsign.callsign, 'W2GMD')
        self.assertEqual(decoded_callsign.ssid, '0')

if __name__ == '__main__':
    unittest.main()
