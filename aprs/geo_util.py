#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Geo Utilities for the APRS Python Module."""

__author__ = 'Greg Albrecht W2GMD <gba@orionlabs.io>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'


import aprs.constants
import aprs.decimaldegrees


def dec2dm_lat(dec):
    """Converts DecDeg to APRS Coord format.
    See: http://ember2ash.com/lat.htm

    Source: http://stackoverflow.com/questions/2056750

    Example:
        >>> test_lat = 37.7418096
        >>> aprs_lat = dec2dm_lat(test_lat)
        >>> aprs_lat
        '3744.51N'
        >>> test_lat = -8.01
        >>> aprs_lat = dec2dm_lat(test_lat)
        >>> aprs_lat
        '0800.60S'
    """
    dec_min = aprs.decimaldegrees.decimal2dm(dec)

    deg = dec_min[0]
    abs_deg = abs(deg)

    if not deg == abs_deg:
        suffix = 'S'
    else:
        suffix = 'N'

    return "%02d%05.2f%s" % (abs_deg, dec_min[1], suffix)


def dec2dm_lng(dec):
    """Converts DecDeg to APRS Coord format.
    See: http://ember2ash.com/lat.htm

    Example:
        >>> test_lng = 122.38833
        >>> aprs_lng = dec2dm_lng(test_lng)
        >>> aprs_lng
        '12223.30E'
        >>> test_lng = -99.01
        >>> aprs_lng = dec2dm_lng(test_lng)
        >>> aprs_lng
        '09900.60W'
    """
    dec_min = aprs.decimaldegrees.decimal2dm(dec)

    deg = dec_min[0]
    abs_deg = abs(deg)

    if not deg == abs_deg:
        suffix = 'W'
    else:
        suffix = 'E'

    return "%03d%05.2f%s" % (abs_deg, dec_min[1], suffix)


def run_doctest():  # pragma: no cover
    """Runs doctests for this module."""
    import doctest
    import aprs.util  # pylint: disable=W0406,W0621
    return doctest.testmod(aprs.util)


if __name__ == '__main__':
    run_doctest()  # pragma: no cover
