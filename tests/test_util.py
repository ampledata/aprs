#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for Python APRS util methods."""

__author__ = 'Greg Albrecht W2GMD <gba@orionlabs.io>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'


import unittest
import logging
import logging.handlers

from .context import aprs

from . import constants


ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
NUMBERS = '0123456789'
POSITIVE_NUMBERS = NUMBERS[1:]
ALPHANUM = ''.join([ALPHABET, NUMBERS])

VALID_CALLSIGNS = ['W2GMD', 'W2GMD-1', 'KF4MKT', 'KF4MKT-1', 'KF4LZA-15']
INVALID_CALLSIGNS = ['xW2GMDx', 'W2GMD-16', 'W2GMD-A', 'W', 'W2GMD-1-0',
                     'W*GMD', 'W2GMD-123']


class APRSUtilTestCase(unittest.TestCase):  # pylint: disable=R0904
    """Tests for Python APRS Utils."""

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprs.constants.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprs.constants.LOG_LEVEL)
        _console_handler.setFormatter(aprs.constants.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def setUp(self):  # pylint: disable=C0103
        """Setup."""
        self.test_frames = open(constants.TEST_FRAMES, 'r')
        self.test_frame = self.test_frames.readlines()[0].strip()

    def tearDown(self):  # pylint: disable=C0103
        """Teardown."""
        self.test_frames.close()

    def test_valid_callsign_valid(self):
        """
        Tests valid callsigns using `aprs.util.valid_callsign()`.
        """
        for i in VALID_CALLSIGNS:
            self.assertTrue(
                aprs.util.valid_callsign(i), "%s is a valid call" % i)

    def test_valid_callsign_invalid(self):
        """
        Tests invalid callsigns using `aprs.util.valid_callsign()`.
        """
        for i in INVALID_CALLSIGNS:
            self.assertFalse(
                aprs.util.valid_callsign(i), "%s is an invalid call" % i)

    def test_extract_callsign_source(self):
        """
        Tests extracting the source callsign from a KISS-encoded APRS frame
        using `aprs.util.extract_callsign()`.
        """
        callsign = {'callsign': 'W2GMD', 'ssid': 6}
        extracted_callsign = aprs.util.extract_callsign(self.test_frame[7:])
        self.assertEqual(callsign, extracted_callsign)

    def test_extract_callsign_dest(self):
        """
        Tests extracting the destination callsign from a KISS-encoded APRS
        frame using `aprs.util.extract_callsign()`.
        """
        extracted_callsign = aprs.util.extract_callsign(self.test_frame)
        self.assertEqual(extracted_callsign['callsign'], 'APRX24')

    def test_full_callsign_with_ssid(self):
        """
        Tests creating a full callsign string from a callsign+ssid dict using
        `aprs.util.full_callsign()`.
        """
        callsign = {
            'callsign': 'W2GMD',
            'ssid': 1
        }
        full_callsign = aprs.util.full_callsign(callsign)
        self.assertEqual(full_callsign, 'W2GMD-1')

    def test_full_callsign_sans_ssid(self):
        """
        Tests creating a full callsign string from a callsign dict using
        `aprs.util.full_callsign()`.
        """
        callsign = {
            'callsign': 'W2GMD',
            'ssid': 0
        }
        full_callsign = aprs.util.full_callsign(callsign)
        self.assertEqual(full_callsign, 'W2GMD')

    def test_format_aprs_frame(self):
        """
        Tests formatting an APRS frame-as-string from an APRS frame-as-dict
        using `aprs.util.format_aprs_frame()`.
        """
        frame = {
            'source': 'W2GMD-1',
            'destination': 'OMG',
            'path': 'WIDE1-1',
            'text': 'test_format_aprs_frame'
        }
        formatted_frame = aprs.util.format_aprs_frame(frame)
        self.assertEqual(
            formatted_frame,
            'W2GMD-1>OMG,WIDE1-1:test_format_aprs_frame'
        )

    def test_decode_aprs_ascii_frame(self):
        """
        Tests creating an APRS frame-as-dict from an APRS frame-as-string
        using `aprs.util.decode_aprs_ascii_frame()`.
        """
        ascii_frame = (
            'W2GMD-9>APOTC1,WIDE1-1,WIDE2-1:!3745.94N/12228.05W>118/010/'
            'A=000269 38C=Temp http://w2gmd.org/ Twitter: @ampledata')
        frame = aprs.util.decode_aprs_ascii_frame(ascii_frame)
        self.assertEqual(
            {
                'source': 'W2GMD-9',
                'destination': 'APOTC1',
                'path': 'APOTC1,WIDE1-1,WIDE2-1',
                'text': ('!3745.94N/12228.05W>118/010/A=000269 38C=Temp '
                         'http://w2gmd.org/ Twitter: @ampledata'),
            },
            frame
        )

    def test_extract_path(self):
        """
        Tests extracting the APRS path from a KISS-encoded frame
        using `aprs.util.extract_path()`.
        """
        extracted_path = aprs.util.extract_path(3, self.test_frame)
        self.assertEqual('WIDE1-1', extracted_path[0])

    def test_format_path(self):
        """
        Tests formatting an APRS path from a KISS-encoded frame
        using `aprs.util.format_path()`.
        """
        extracted_path = aprs.util.format_path(3, self.test_frame)
        self.assertEqual('WIDE1-1', extracted_path)

    def test_encode_frame(self):
        """
        Tests KISS-encoding an APRS frame using
        `aprs.util.encode_frame()`.
        """
        frame = {
            'source': 'W2GMD-1',
            'destination': 'OMG',
            'path': 'WIDE1-1',
            'text': 'test_encode_frame'
        }
        encoded_frame = aprs.util.encode_frame(frame)
        legit = ('\x9e\x9a\x8e@@@`\xaed\x8e\x9a\x88@b'
                 '\xae\x92\x88\x8ab@c\x03\xf0test_encode_frame')
        self.assertEqual(legit, encoded_frame)

    def test_decode_frame_recorded(self):
        """
        Tests decoding a KISS-encoded APRS frame using
        `aprs.util.decode_frame()`.
        """
        frame = {
            'path': 'WIDE1-1',
            'destination': 'APRX24',
            'source': 'W2GMD-6',
            'text': ('!3745.75NI12228.05W#W2GMD-6 Inner Sunset, '
                     'SF iGate/Digipeater http://w2gmd.org')
        }
        self.assertEqual(frame, aprs.util.decode_frame(self.test_frame))

    def test_decode_frame(self):
        """
        Tests decoding a KISS-encoded APRS frame using
        `aprs.util.decode_frame()`.
        """
        frame = {
            'source': 'W2GMD-1',
            'destination': 'OMG',
            'path': 'WIDE1-1,WIDE2-2',
            'text': 'test_encode_frame'
        }
        encoded_frame = aprs.util.encode_frame(frame)
        decoded_frame = aprs.util.decode_frame(encoded_frame)
        self.assertEqual(frame, decoded_frame)

    def test_create_callsign(self):
        """
        Tests creating a callsign string from a callsign dict using
        `aprs.util.create_callsign()`.
        """
        full_callsign = 'W2GMD-1'
        callsign = aprs.util.create_callsign(full_callsign)
        self.assertEqual({'callsign': 'W2GMD', 'ssid': 1}, callsign)

    def test_full_callsign(self):
        """
        Tests converting a callsign dict to a callsing string
        (callsign-ssid) using `aprs.util.full_callsign()`.
        """
        callsign = {'callsign': 'W2GMD', 'ssid': 1}
        full_callsign = aprs.util.full_callsign(callsign)
        self.assertEqual('W2GMD-1', full_callsign)

    def test_encode_callsign_digipeated(self):
        """
        Tests encoding a digipeated callsign with
        `aprs.util.encode_callsign()`.
        """
        callsign = {'callsign': 'W2GMD*', 'ssid': 1}
        encoded_callsign = aprs.util.encode_callsign(callsign)
        self.assertEqual('\xaed\x8e\x9a\x88@\xe2', encoded_callsign)

    def test_encode_callsign(self):
        """
        Tests encoding a non-digipeated callsign with
        `aprs.util.encode_callsign()`.
        """
        callsign = {'callsign': 'W2GMD', 'ssid': 1}
        encoded_callsign = aprs.util.encode_callsign(callsign)
        self.assertEqual('\xaed\x8e\x9a\x88@b', encoded_callsign)


if __name__ == '__main__':
    unittest.main()
