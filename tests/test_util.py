#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Greg Albrecht W2GMD <gba@onbeep.com>'
__copyright__ = 'Copyright 2013 OnBeep, Inc.'
__license__ = 'Apache 2.0'


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


class APRSUtilTestCase(unittest.TestCase):
    """Tests for Python APRS Utils."""

    logger = logging.getLogger(__name__)
    logger.setLevel(aprs.constants.LOG_LEVEL)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(aprs.constants.LOG_LEVEL)
    formatter = logging.Formatter(aprs.constants.LOG_FORMAT)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.propagate = False

    def setUp(self):
        """Setup."""
        self.test_frames = open(constants.TEST_FRAMES, 'r')
        self.test_frame = self.test_frames.readlines()[0].strip()

    def tearDown(self):
        """Teardown."""
        self.test_frames.close()

    def test_latitude(self):
        """Test Decimal to APRS Latitude conversion.

        Spec per ftp://ftp.tapr.org/aprssig/aprsspec/spec/aprs101/APRS101.pdf
        --
        Latitude is expressed as a fixed 8-character field, in degrees and
        decimal minutes (to two decimal places), followed by the letter N for
        north or S for south. Latitude degrees are in the range 00 to 90.
        Latitude minutes are expressed as whole minutes and hundredths of a
        minute, separated by a decimal point.

        For example:

            4903.50N is 49 degrees 3 minutes 30 seconds north.

        In generic format examples, the latitude is shown as the 8-character
        string ddmm.hhN (i.e. degrees, minutes and hundredths of a minute
        north).
        """
        test_lat = 37.7418096
        aprs_lat = aprs.util.dec2dm_lat(test_lat)
        self.logger.debug('aprs_lat=%s', aprs_lat)

        lat_deg = int(aprs_lat.split('.')[0][:1])
        lat_hsec = aprs_lat.split('.')[1]

        self.assertTrue(len(aprs_lat) == 8)
        self.assertTrue(lat_deg >= 00)
        self.assertTrue(lat_deg <= 90)
        self.assertTrue(aprs_lat.endswith('N'))

    def test_longitude(self):
        """Test Decimal to APRS Longitude conversion.

        Spec per ftp://ftp.tapr.org/aprssig/aprsspec/spec/aprs101/APRS101.pdf
        --
        Longitude is expressed as a fixed 9-character field, in degrees and
        decimal minutes (to two decimal places), followed by the letter E for
        east or W for west.

        Longitude degrees are in the range 000 to 180. Longitude minutes are
        expressed as whole minutes and hundredths of a minute, separated by a
        decimal point.
        
        For example:

            07201.75W is 72 degrees 1 minute 45 seconds west.

        In generic format examples, the longitude is shown as the 9-character
        string dddmm.hhW (i.e. degrees, minutes and hundredths of a minute
        west).
        """
        test_lng = -122.38833
        aprs_lng = aprs.util.dec2dm_lng(test_lng)
        self.logger.debug('aprs_lng=%s', aprs_lng)

        lng_deg = int(aprs_lng.split('.')[0][:2])
        lng_hsec = aprs_lng.split('.')[1]

        self.assertTrue(len(aprs_lng) == 9)
        self.assertTrue(lng_deg >= 000)
        self.assertTrue(lng_deg <= 180)
        self.assertTrue(aprs_lng.endswith('W'))

    def test_valid_callsign_valid(self):
        for c in VALID_CALLSIGNS:
            self.assertTrue(aprs.util.valid_callsign(c), "%s is a valid call" % c)

    def test_valid_callsign_invalid(self):
        for c in INVALID_CALLSIGNS:
            self.assertFalse(aprs.util.valid_callsign(c), "%s is an invalid call" % c)

    def test_extract_callsign_source(self):
        callsign = {'callsign': 'W2GMD', 'ssid': 6}
        extracted_callsign = aprs.util.extract_callsign(self.test_frame[7:])
        self.assertEqual(callsign, extracted_callsign)

    def test_extract_callsign_destination(self):
        extracted_callsign = aprs.util.extract_callsign(self.test_frame)
        self.assertEqual(extracted_callsign['callsign'], 'APRX24')

    def test_full_callsign_with_ssid(self):
        callsign = {
            'callsign': 'W2GMD',
            'ssid': 1
        }
        full_callsign = aprs.util.full_callsign(callsign)
        self.assertEqual(full_callsign, 'W2GMD-1')

    def test_full_callsign_sans_ssid(self):
        callsign = {
            'callsign': 'W2GMD',
            'ssid': 0
        }
        full_callsign = aprs.util.full_callsign(callsign)
        self.assertEqual(full_callsign, 'W2GMD')

    def test_format_aprs_frame(self):
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
        ascii_frame = 'W2GMD-9>APOTC1,WIDE1-1,WIDE2-1:!3745.94N/12228.05W>118/010/A=000269 38C=Temp http://w2gmd.org/ Twitter: @ampledata'
        frame = aprs.util.decode_aprs_ascii_frame(ascii_frame)
        self.assertEqual(
            frame,
            {'source': 'W2GMD-9', 'destination': 'APOTC1', 'text': '!3745.94N/12228.05W>118/010/A=000269 38C=Temp http://w2gmd.org/ Twitter: @ampledata', 'path': 'APOTC1,WIDE1-1,WIDE2-1'}
        )

    def test_extract_path(self):
        extracted_path = aprs.util.extract_path(3, self.test_frame)
        self.assertEqual('WIDE1-1', extracted_path[0])

    def test_format_path(self):
        extracted_path = aprs.util.format_path(3, self.test_frame)
        self.assertEqual('WIDE1-1', extracted_path)

    def test_encode_frame(self):
        frame = {
            'source': 'W2GMD-1',
            'destination': 'OMG',
            'path': 'WIDE1-1',
            'text': 'test_encode_frame'
        }
        encoded_frame = aprs.util.encode_frame(frame)
        legit = '\x9e\x9a\x8e@@@`\xaed\x8e\x9a\x88@b\xae\x92\x88\x8ab@c\x03\xf0test_encode_frame'
        self.assertEqual(legit, encoded_frame)

    def test_decode_frame_recorded(self):
        frame = {
            'text': '!3745.75NI12228.05W#W2GMD-6 Inner Sunset, SF iGate/Digipeater http://w2gmd.org',
            'path': 'WIDE1-1',
            'destination': 'APRX24',
            'source': 'W2GMD-6'
        }
        self.assertEqual(frame, aprs.util.decode_frame(self.test_frame))

    def test_decode_frame(self):
        frame = {
            'source': 'W2GMD-1',
            'destination': 'OMG',
            'path': 'WIDE1-1,WIDE2-2',
            'text': 'test_encode_frame'
        }
        encoded_frame = aprs.util.encode_frame(frame)
        decoded_frame = aprs.util.decode_frame(encoded_frame)
        self.assertEqual(frame, decoded_frame)

if __name__ == '__main__':
    unittest.main()
