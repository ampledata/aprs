#!/usr/bin/env python


import unittest
import logging
import logging.handlers

from .context import aprs


ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
NUMBERS = '0123456789'
POSITIVE_NUMBERS = NUMBERS[1:]
ALPHANUM = ''.join([ALPHABET, NUMBERS])


class APRSUtilTest(unittest.TestCase):
    """Tests for Python APRS Utils."""

    logger = logging.getLogger('aprs.util.tests')
    logger.addHandler(logging.StreamHandler())

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
        self.logger.debug("aprs_lat=%s" % aprs_lat)

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
        self.logger.debug("aprs_lng=%s" % aprs_lng)

        lng_deg = int(aprs_lng.split('.')[0][:2])
        lng_hsec = aprs_lng.split('.')[1]

        self.assertTrue(len(aprs_lng) == 9)
        self.assertTrue(lng_deg >= 000)
        self.assertTrue(lng_deg <= 180)
        self.assertTrue(aprs_lng.endswith('W'))


if __name__ == '__main__':
    unittest.main()
