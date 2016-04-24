#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for Python APRS Geo Util methods.

Spec per ftp://ftp.tapr.org/aprssig/aprsspec/spec/aprs101/APRS101.pdf

Latitude
--------

Latitude is expressed as a fixed 8-character field, in degrees and decimal
minutes (to two decimal places), followed by the letter N for north or S for
south.

Latitude degrees are in the range 00 to 90. Latitude minutes are expressed as
whole minutes and hundredths of a minute, separated by a decimal point.

For example:

    4903.50N    is 49 degrees 3 minutes 30 seconds north.

In generic format examples, the latitude is shown as the 8-character string
ddmm.hhN (i.e. degrees, minutes and hundredths of a minute north).


Longitude Format
----------------

Longitude is expressed as a fixed 9-character field, in degrees and decimal
minutes (to two decimal places), followed by the letter E for east or W for
west.

Longitude degrees are in the range 000 to 180. Longitude minutes are expressed
as whole minutes and hundredths of a minute, separated by a decimal point.

For example:

    07201.75W    is 72 degrees 1 minute 45 seconds west.

In generic format examples, the longitude is shown as the 9-character string
dddmm.hhW (i.e. degrees, minutes and hundredths of a minute west).

"""

__author__ = 'Greg Albrecht W2GMD <gba@orionlabs.io>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'


import unittest
import logging
import logging.handlers

from .context import aprs

from . import constants


class APRSGeoTestCase(unittest.TestCase):  # pylint: disable=R0904
    """Tests for Python APRS Utils."""

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprs.constants.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprs.constants.LOG_LEVEL)
        _console_handler.setFormatter(aprs.constants.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def test_latitude_north(self):
        """Test Decimal to APRS Latitude conversion."""
        test_lat = 37.7418096
        aprs_lat = aprs.geo_util.dec2dm_lat(test_lat)
        self._logger.info('test_lat=%s aprs_lat=%s', test_lat, aprs_lat)

        lat_deg = int(aprs_lat.split('.')[0][:1])
        # lat_hsec = aprs_lat.split('.')[1]

        self.assertTrue(len(aprs_lat) == 8)
        self.assertTrue(lat_deg >= 00)
        self.assertTrue(lat_deg <= 90)
        self.assertTrue(aprs_lat.endswith('N'))

    def test_latitude_south(self):
        """Test Decimal to APRS Latitude conversion."""
        test_lat = -37.7418096
        aprs_lat = aprs.geo_util.dec2dm_lat(test_lat)
        self._logger.info('test_lat=%s aprs_lat=%s', test_lat, aprs_lat)

        lat_deg = int(aprs_lat.split('.')[0][:1])

        self.assertTrue(len(aprs_lat) == 8)
        self.assertTrue(lat_deg >= 00)
        self.assertTrue(lat_deg <= 90)
        self.assertTrue(aprs_lat.endswith('S'))

    def test_latitude_south_padding_minutes(self):
        """
        Test Decimal to APRS Latitude conversion for latitudes in the
        following situations:
            - minutes < 10
            - whole degrees latitude < 10
        """
        test_lat = -38.01
        aprs_lat = aprs.geo_util.dec2dm_lat(test_lat)
        self._logger.info('test_lat=%s aprs_lat=%s', test_lat, aprs_lat)

        lat_deg = int(aprs_lat.split('.')[0][:1])

        self.assertTrue(len(aprs_lat) == 8)
        self.assertTrue(lat_deg >= 00)
        self.assertTrue(lat_deg <= 90)
        self.assertTrue(aprs_lat.endswith('S'))

    def test_latitude_south_padding_degrees(self):
        """
        Test Decimal to APRS Latitude conversion for latitudes in the
        following situations:
            - minutes < 10
            - whole degrees latitude < 10
        """
        test_lat = -8.01
        aprs_lat = aprs.geo_util.dec2dm_lat(test_lat)
        self._logger.info('test_lat=%s aprs_lat=%s', test_lat, aprs_lat)

        lat_deg = int(aprs_lat.split('.')[0][:1])

        self.assertTrue(len(aprs_lat) == 8)
        self.assertTrue(lat_deg >= 00)
        self.assertTrue(lat_deg <= 90)
        self.assertTrue(aprs_lat.endswith('S'))

    def test_longitude_west(self):
        """Test Decimal to APRS Longitude conversion."""
        test_lng = -122.38833
        aprs_lng = aprs.geo_util.dec2dm_lng(test_lng)
        self._logger.info('test_lng=%s aprs_lng=%s', test_lng, aprs_lng)

        lng_deg = int(aprs_lng.split('.')[0][:2])
        # lng_hsec = aprs_lng.split('.')[1]

        self.assertTrue(len(aprs_lng) == 9)
        self.assertTrue(lng_deg >= 000)
        self.assertTrue(lng_deg <= 180)
        self.assertTrue(aprs_lng.endswith('W'))

    def test_longitude_west_padding_minutes(self):
        """
        Test Decimal to APRS Longitude conversion for longitude in the
        following situations:
            - minutes < 10
            - whole degrees longitude < 100
        """
        test_lng = -122.01
        aprs_lng = aprs.geo_util.dec2dm_lng(test_lng)
        self._logger.info('test_lng=%s aprs_lng=%s', test_lng, aprs_lng)

        lng_deg = int(aprs_lng.split('.')[0][:2])
        # lng_hsec = aprs_lng.split('.')[1]

        self.assertTrue(len(aprs_lng) == 9)
        self.assertTrue(lng_deg >= 000)
        self.assertTrue(lng_deg <= 180)
        self.assertTrue(aprs_lng.endswith('W'))

    def test_longitude_west_padding_degrees(self):
        """
        Test Decimal to APRS Longitude conversion for longitude in the
        following situations:
            - minutes < 10
            - whole degrees longitude < 100
        """
        test_lng = -99.01
        aprs_lng = aprs.geo_util.dec2dm_lng(test_lng)
        self._logger.info('test_lng=%s aprs_lng=%s', test_lng, aprs_lng)

        lng_deg = int(aprs_lng.split('.')[0][:2])
        # lng_hsec = aprs_lng.split('.')[1]

        self.assertTrue(len(aprs_lng) == 9)
        self.assertTrue(lng_deg >= 000)
        self.assertTrue(lng_deg <= 180)
        self.assertTrue(aprs_lng.endswith('W'))

    def test_longitude_east(self):
        """Test Decimal to APRS Longitude conversion."""
        test_lng = 122.38833
        aprs_lng = aprs.geo_util.dec2dm_lng(test_lng)
        self._logger.info('test_lng=%s aprs_lng=%s', test_lng, aprs_lng)

        lng_deg = int(aprs_lng.split('.')[0][:2])
        # lng_hsec = aprs_lng.split('.')[1]

        self.assertTrue(len(aprs_lng) == 9)
        self.assertTrue(lng_deg >= 000)
        self.assertTrue(lng_deg <= 180)
        self.assertTrue(aprs_lng.endswith('E'))


if __name__ == '__main__':
    unittest.main()
