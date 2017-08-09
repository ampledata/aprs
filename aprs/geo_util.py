#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS Module Geo Utility Function Definitions."""

import aprs.decimaldegrees

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'  # NOQA pylint: disable=R0801
__copyright__ = 'Copyright 2017 Greg Albrecht and Contributors'  # NOQA pylint: disable=R0801
__license__ = 'Apache License, Version 2.0'  # NOQA pylint: disable=R0801


def dec2dm_lat(dec: float) -> str:
    """
    Converts DecDeg to APRS Coord format.

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


def dec2dm_lng(dec: float) -> str:
    """
    Converts DecDeg to APRS Coord format.

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


def ambiguate(pos: float, ambiguity: int) -> str:
    """
    Adjust ambiguity of position.

    Derived from @asdil12's `process_ambiguity()`.

    >>> pos = '12345.67N'
    >>> ambiguate(pos, 0)
    '12345.67N'
    >>> ambiguate(pos, 1)
    '12345.6 N'
    >>> ambiguate(pos, 2)
    '12345.  N'
    >>> ambiguate(pos, 3)
    '1234 .  N'
    """
    num = bytearray(pos, 'UTF-8')
    for i in range(0, ambiguity):
        if i > 1:
            # skip the dot
            i += 1
        # skip the direction
        i += 2
        num[-i] = ord(' ')
    return num.decode()


def run_doctest():  # pragma: no cover
    """Runs doctests for this module."""
    import doctest
    return doctest.testmod()


if __name__ == '__main__':
    run_doctest()  # pragma: no cover
