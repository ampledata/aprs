#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS Module APRS-IS Bindings Tests."""

import logging
import random
import unittest

from .context import aprs

from . import constants

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'  # NOQA pylint: disable=R0801
__copyright__ = 'Copyright 2017 Greg Albrecht and Contributors'  # NOQA pylint: disable=R0801
__license__ = 'Apache License, Version 2.0'  # NOQA pylint: disable=R0801


class APRSTestClass(unittest.TestCase):  # pylint: disable=R0904

    """Tests for Python APRS-IS Bindings."""

    _logger = logging.getLogger(__name__)  # pylint: disable=R0801
    if not _logger.handlers:  # pylint: disable=R0801
        _logger.setLevel(aprs.LOG_LEVEL)  # pylint: disable=R0801
        _console_handler = logging.StreamHandler()  # pylint: disable=R0801
        _console_handler.setLevel(aprs.LOG_LEVEL)  # pylint: disable=R0801
        _console_handler.setFormatter(aprs.LOG_FORMAT)  # pylint: disable=R0801
        _logger.addHandler(_console_handler)  # pylint: disable=R0801
        _logger.propagate = False  # pylint: disable=R0801

    def setUp(self):  # pylint: disable=C0103
        """Setup."""
        self.test_frames = open(constants.TEST_FRAMES, 'rb')
        self.test_frame = self.test_frames.read()#lines()[0].strip()

        self.fake_callsign = ''.join([
            self.random(1, 'KWN'),
            self.random(1, constants.NUMBERS),
            self.random(3, constants.ALPHABET),
            '-',
            self.random(1, constants.POSITIVE_NUMBERS)
        ])

        self.real_callsign = '-'.join(
            ['W2GMD', self.random(1, constants.POSITIVE_NUMBERS)])

        self.fake_server = ''.join([
            'http://localhost:',
            self.random(4, constants.POSITIVE_NUMBERS),
            '/'
        ])

        self.real_server = 'http://localhost:14580'

        self._logger.debug(
            "fake_callsign=%s real_callsign=%s",
            self.fake_callsign,
            self.real_callsign
        )

        self._logger.debug(
            "fake_server=%s real_server=%s",
            self.fake_server,
            self.real_server
        )

    def tearDown(self):  # pylint: disable=C0103
        """Teardown."""
        self.test_frames.close()

    @classmethod
    def random(cls, length=8, alphabet=constants.ALPHANUM):
        """
        Generates a random string for test cases.

        :param length: Length of string to generate.
        :param alphabet: Alphabet to use to create string.
        :type length: int
        :type alphabet: str
        """
        return ''.join(random.choice(alphabet) for _ in range(length))
