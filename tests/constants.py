#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS Module Test Constants."""

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2017 Greg Albrecht and Contributors'
__license__ = 'Apache License, Version 2.0'


PANGRAM = 'the quick brown fox jumps over the lazy dog'
ALPHABET = PANGRAM.replace(' ', '')

NUMBERS = ''.join([str(x) for x in range(0, 10)])
POSITIVE_NUMBERS = NUMBERS[1:]
ALPHANUM = ''.join([ALPHABET, NUMBERS])

VALID_CALLSIGNS = ['W2GMD', 'W2GMD-1', 'KF4MKT', 'KF4MKT-1', 'KF4LZA-15']
INVALID_CALLSIGNS = ['xW2GMDx', 'W2GMD-16', 'W2GMD-A', 'W', 'W2GMD-1-0',
                     'W*GMD', 'W2GMD-123']

TEST_FRAMES = 'tests/test_frames.log'

TEST_FRAME = (
    '82a0a4b0646860ae648e9a88406cae92888a62406303f021333734352e3735'
    '4e4931323232382e303557235732474d442d3620496e6e65722053756e73657'
    '42c2053462069476174652f4469676970656174657220687474703a2f2f7732'
    '676d642e6f7267')
