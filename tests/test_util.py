#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS Module Utility Function Tests."""

import unittest  # pylint: disable=R0801

from .context import aprs  # pylint: disable=R0801
from .context import aprs_test_classes  # pylint: disable=R0801

from . import constants  # pylint: disable=R0801

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'  # NOQA pylint: disable=R0801
__copyright__ = 'Copyright 2017 Greg Albrecht and Contributors'  # NOQA pylint: disable=R0801
__license__ = 'Apache License, Version 2.0'  # NOQA pylint: disable=R0801


class APRSUtilTestCase(aprs_test_classes.APRSTestClass):  # pylint: disable=R0904

    """Tests for Python APRS Utils."""

    def setUp(self):  # pylint: disable=C0103
        """Setup."""
        self.test_frames = open(constants.TEST_FRAMES, 'r')
        self.test_frame = self.test_frames.readlines()[0].strip()

    def tearDown(self):  # pylint: disable=C0103
        """Teardown."""
        self.test_frames.close()

    def test_valid_callsign_valid(self):
        """
        Tests valid callsigns using `aprs.valid_callsign()`.
        """
        for i in constants.VALID_CALLSIGNS:
            self.assertTrue(
                aprs.valid_callsign(i), "%s is a valid call" % i)

    def test_valid_callsign_invalid(self):
        """
        Tests invalid callsigns using `aprs.valid_callsign()`.
        """
        for i in constants.INVALID_CALLSIGNS:
            self.assertFalse(
                aprs.valid_callsign(i), "%s is an invalid call" % i)


if __name__ == '__main__':
    unittest.main()
