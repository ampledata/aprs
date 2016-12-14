#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `aprs.Frame`."""

import logging
import logging.handlers
import random
import unittest

from .context import aprs

from . import constants

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'


class FrameTestCase(unittest.TestCase):  # pylint: disable=R0904

    """Tests for `aprs.Frame`."""

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprs.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprs.LOG_LEVEL)
        _console_handler.setFormatter(aprs.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    @classmethod
    def random(cls, length=8, alphabet=constants.ALPHANUM):
        """
        Generates a random string for test cases.

        :param length: Length of string to generate.
        :param alphabet: Alphabet to use to create string.
        :type length: int
        :type alphabet: str
        """
        return ''.join(random.choice(alphabet) for _ in xrange(length))

    def setUp(self):  # pylint: disable=C0103
        """Setup."""
        self.test_frames = open(constants.TEST_FRAMES, 'r')
        self.test_frame = self.test_frames.readlines()[0].strip()

        self.fake_callsign = ''.join([
            self.random(1, 'KWN'),
            self.random(1, constants.NUMBERS),
            self.random(3, constants.ALPHABET),
            '-',
            self.random(1, constants.POSITIVE_NUMBERS)
        ])

        self.real_callsign = '-'.join(
            ['W2GMD', self.random(1, constants.POSITIVE_NUMBERS)])

        self._logger.debug(
            "fake_callsign=%s real_callsign=%s",
            self.fake_callsign,
            self.real_callsign
        )

    def tearDown(self):  # pylint: disable=C0103
        """Teardown."""
        self.test_frames.close()

    def test_format_aprs_frame(self):
        """
        Tests formatting an APRS frame-as-string from an APRS frame-as-dict
        using `aprs.util.format_aprs_frame()`.
        """
        frame = "%s>%s,WIDE1-1:>test_format_aprs_frame" % \
            (self.real_callsign, self.fake_callsign)

        formatted_frame = aprs.Frame(frame)

        self.assertEqual(str(formatted_frame), frame)

    def test_decode_aprs_ascii_frame(self):
        """
        Tests creating an Frame Object from an APRS ASCII Frame
        using `aprs.Frame`.
        """
        ascii_frame = (
            "%s>APOTC1,WIDE1-1,WIDE2-1:!3745.94N/12228.05W>118/010/"
            "A=000269 http://w2gmd.org/ Twitter: @ampledata" %
            self.real_callsign)

        aprs_frame = aprs.Frame(ascii_frame)

        self.assertEqual(str(aprs_frame), ascii_frame)
        self.assertEqual(str(aprs_frame.source), self.real_callsign)
        self.assertEqual(str(aprs_frame.destination), 'APOTC1')
        self.assertEqual(str(aprs_frame.path[0]), 'WIDE1-1')
        self.assertEqual(str(aprs_frame.path[1]), 'WIDE2-1')

    def test_encode_ascii_frame_as_kiss(self):
        """
        Tests KISS-encoding an ASCII APRS frame using `aprs.Frame()`.
        """
        frame = 'W2GMD-1>OMG,WIDE1-1:test_encode_frame'
        kiss_frame = (
            '9e9a8e40404060ae648e9a884062ae92888a62406303f074657'
            '3745f656e636f64655f6672616d65')

        aprs_frame = aprs.Frame(frame)

        self.assertEqual(kiss_frame.decode('hex'), aprs_frame.encode_kiss())


if __name__ == '__main__':
    unittest.main()
