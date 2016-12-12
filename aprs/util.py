#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Utilities for the APRS Python Module."""

import logging

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'


def valid_callsign(callsign):
    """
    Validates callsign.

    :param callsign: Callsign to validate.
    :type callsign: str

    :returns: True if valid, False otherwise.
    :rtype: bool
    """
    #logging.debug('callsign=%s', callsign)
    callsign = callsign.lstrip().rstrip()

    if '-' in callsign:
        if not callsign.count('-') == 1:
            return False
        else:
            callsign, ssid = callsign.split('-')
    else:
        ssid = 0

    #logging.debug('callsign=%s ssid=%s', callsign, ssid)

    # Test length, call should be <6.
    if (len(callsign) < 2 or len(callsign) > 6 or len(str(ssid)) < 1 or
            len(str(ssid)) > 2):
        return False

    for char in callsign:
        if not (char.isalpha() or char.isdigit()):
            if char == '*' and callsign[-1] == '*':
                next
            else:
                return False

    if not str(ssid).isdigit():
        return False

    if int(ssid) < 0 or int(ssid) > 15:
        return False

    return True


def create_location_frame(source, latitude, longitude, altitude, course, speed,
                          symboltable, symbolcode, comment=None,
                          destination='APRS', path=None):
    """
    Creates an APRS Location frame.

    :param source: Source callsign (or callsign + SSID).
    :param latitude: Latitude.
    :param longitude: Longitude.
    :param altitude: Altitude.
    :param course: Course.
    :param speed: Speed.
    :param symboltable: APRS Symboltable.
    :param symbolcode: APRS Symbolcode.
    :param comment: Comment field. Default: Module + version.
    :param destination: Destination callsign. Default: 'APRS'.
    :param path: APRS Path.

    :return: APRS location frame.
    :rtype: str
    """
    comment = comment or 'APRS Python Module'

    location_text = ''.join([
        '!',
        latitude,
        symboltable,
        longitude,
        symbolcode,
        "%03d" % course,
        '/',
        "%03d" % speed,
        '/',
        'A=',
        "%06d" % altitude,
        ' ',
        comment
    ])
    frame_dict = {
        'source': source,
        'destination': destination,
        'path': path,
        'text': location_text
    }
    return format_aprs_frame(frame_dict)  # FIXME


def run_doctest():  # pragma: no cover
    """Runs doctests for this module."""
    import doctest
    import aprs  # pylint: disable=W0406,W0621
    return doctest.testmod(aprs.util)


if __name__ == '__main__':
    run_doctest()  # pragma: no cover
