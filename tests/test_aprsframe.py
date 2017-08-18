#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS Module APRS Frame Tests."""

import unittest  # pylint: disable=R0801

from .context import aprs  # pylint: disable=R0801
from .context import aprs_test_classes  # pylint: disable=R0801

from . import constants  # pylint: disable=R0801

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'  # NOQA pylint: disable=R0801
__copyright__ = 'Copyright 2017 Greg Albrecht and Contributors'  # NOQA pylint: disable=R0801
__license__ = 'Apache License, Version 2.0'  # NOQA pylint: disable=R0801


class FrameTestCase(aprs_test_classes.APRSTestClass):  # pylint: disable=R0904

    """Tests for `aprs.Frame`."""

    def test_aprs_frame(self):
        """
        Tests creating APRS Frame Object from plain-text APRS Frame string.
        """
        frame = "%s>%s,WIDE1-1:>test_aprs_frame" % \
            (self.real_callsign, self.fake_callsign)
        formatted_frame = aprs.parse_frame(frame)
        self.assertEqual(str(formatted_frame), frame)

    def test_aprs_frame_no_path(self):
        """
        Tests creating APRS Frame Object from plain-text APRS Frame string.
        """
        frame = "%s>%s:>test_aprs_frame_no_path" % \
            (self.real_callsign, self.fake_callsign)
        formatted_frame = aprs.parse_frame(frame)
        self.assertEqual(str(formatted_frame), frame)

    def test_aprs_frame_long_path(self):
        """
        Tests creating APRS Frame Object from plain-text APRS Frame string.
        """
        frame = "%s>%s,WIDE1-1,WIDE4-2,WIDE9-9:>test_aprs_frame_long_path" % \
            (self.real_callsign, self.fake_callsign)
        formatted_frame = aprs.parse_frame(frame)
        self.assertEqual(str(formatted_frame), frame)

    def test_decode_aprs_frame(self):
        """
        Tests creating an APRS Frame Object from plain-text APRS Frame string.
        """
        frame = (
            "%s>APOTC1,WIDE1-1,WIDE2-1:!3745.94N/12228.05W>118/010/"
            "A=000269 http://w2gmd.org/ Twitter: @ampledata" %
            self.real_callsign)
        self._logger.info('frame=%s', frame)

        aprs_frame = aprs.parse_frame(frame)
        self._logger.info('aprs_frame=%s', aprs_frame)

        self.assertEqual(str(aprs_frame), frame)
        self.assertEqual(str(aprs_frame.source), self.real_callsign)
        self.assertEqual(str(aprs_frame.destination), 'APOTC1')
        self.assertEqual(str(aprs_frame.path[0]), 'WIDE1-1')
        self.assertEqual(str(aprs_frame.path[1]), 'WIDE2-1')

    def test_ax25_encode(self):
        """
        Tests AX.25 Encoding a plain-text APRS Frame.
        """
        frame = (
            'W2GMD-6>APRX24,WIDE1-1,WIDE2-1:!3745.75NI12228.05W#W2GMD-6 '
            'Inner Sunset, SF iGate/Digipeater http://w2gmd.org'
        )
        aprs_frame = aprs.parse_frame(frame)
        encoded_frame = aprs_frame.encode_ax25()
        self._logger.debug('encoded_frame=%s', encoded_frame)

        self.assertEqual(encoded_frame[0], 126)
        self.assertEqual(encoded_frame[-1:], aprs.AX25_FLAG)
        self.assertEqual(encoded_frame[-3:-1], b'\xff\x07')
        self.assertEqual(str(aprs.parse_callsign_ax25(encoded_frame[1:8])), 'APRX24')
        self.assertEqual(str(aprs.parse_callsign_ax25(encoded_frame[8:15])), 'W2GMD-6')
        self.assertEqual(str(aprs.parse_callsign_ax25(encoded_frame[15:22])), 'WIDE1-1')
        self.assertEqual(str(aprs.parse_callsign_ax25(encoded_frame[22:29])), 'WIDE2-1')
        self.assertEqual(encoded_frame[29:31], aprs.ADDR_INFO_DELIM)
        self.assertEqual(
            encoded_frame[31:-3],
            bytearray(b'!3745.75NI12228.05W#W2GMD-6 Inner Sunset, SF iGate/Digipeater http://w2gmd.org')
        )

        decoded_frame = aprs.parse_frame(encoded_frame)

        self.assertEqual(str(decoded_frame.source), 'W2GMD-6')
        self.assertEqual(str(decoded_frame.destination), 'APRX24')
        self.assertEqual(str(decoded_frame.path[0]), 'WIDE1-1')
        self.assertEqual(str(decoded_frame.path[1]), 'WIDE2-1')
        self.assertEqual(
            str(decoded_frame.info),
            '!3745.75NI12228.05W#W2GMD-6 Inner Sunset, SF iGate/Digipeater http://w2gmd.org'
        )

    def test_ax25_decode(self):
        """
        Tests AX.25 Encoding a plain-text APRS Frame.
        """
        #frame = 'W2GMD-1>APRY07,WIDE1-1:>test_ax25_decode'
        frame = 'W2GMD-1>APRY07:>test_ax25_decode'
        aprs_frame = aprs.parse_frame(frame)
        encoded_frame = aprs_frame.encode_ax25()

        decoded_frame = aprs.Frame(encoded_frame)



if __name__ == '__main__':
    unittest.main()
