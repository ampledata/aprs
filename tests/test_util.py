#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS Module Utility Function Tests."""

import logging
import logging.handlers
import unittest

from .context import aprs

from . import constants

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2017 Greg Albrecht and Contributors'
__license__ = 'Apache License, Version 2.0'


class APRSUtilTestCase(unittest.TestCase):  # pylint: disable=R0904
    """Tests for Python APRS Utils."""

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprs.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprs.LOG_LEVEL)
        _console_handler.setFormatter(aprs.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def setUp(self):  # pylint: disable=C0103
        """Setup."""
        self.test_frames = open(constants.TEST_FRAMES, 'r', errors='ignore')
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
