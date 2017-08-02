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

    def setUp(self):  # pylint: disable=C0103
        """Setup."""
        self.test_frames = open(constants.TEST_FRAMES, 'r')
        self.test_frame = self.test_frames.readlines()[0].strip()

    def tearDown(self):  # pylint: disable=C0103
        """Teardown."""
        self.test_frames.close()

    def test_extract_callsign_source(self):
        """
        Tests extracting the source callsign from a KISS-encoded APRS frame
        using `aprs.Callsign`.
        """
        callsign = 'W2GMD'
        ssid = str(6)
        full = '-'.join([callsign, ssid])

        extracted_callsign = aprs.Callsign(
            constants.TEST_FRAME.decode('hex')[7:])

        self.assertEqual(full, str(extracted_callsign))
        self.assertEqual(callsign, extracted_callsign.callsign)
        self.assertEqual(ssid, extracted_callsign.ssid)

    def test_extract_callsign_dest(self):
        """
        Tests extracting the destination callsign from a KISS-encoded APRS
        frame using `aprs.Callsign`.
        """
        extracted_callsign = aprs.Callsign(constants.TEST_FRAME.decode('hex'))
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

    def test_encode_kiss(self):
        """
        Tests encoding a non-digipeated Callsign.
        """
        encoded_callsign = aprs.Callsign('W2GMD-1').encode_kiss()
        self.assertEqual('\xaed\x8e\x9a\x88@b', encoded_callsign)

    # FIXME: Currently not working...
    def test_encode_kiss_digipeated(self):
        """
        Tests encoding a digipeated callsign.
        """
        callsign = 'W2GMD*'
        callsign_obj = aprs.Callsign(callsign)
        self._logger.info(callsign_obj.encode_kiss().encode('hex'))
        self._logger.info('\xaed\x8e\x9a\x88@\xe2'.encode('hex'))
        # self.assertEqual(
        #    '\xaed\x8e\x9a\x88@\xe2', callsign_obj.encode_kiss())


if __name__ == '__main__':
    unittest.main()
