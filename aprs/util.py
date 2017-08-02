#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS Module Utility Functions Definitions."""

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'  # NOQA pylint: disable=R0801
__copyright__ = 'Copyright 2017 Greg Albrecht and Contributors'  # NOQA pylint: disable=R0801
__license__ = 'Apache License, Version 2.0'  # NOQA pylint: disable=R0801


def valid_callsign(callsign):
    """
    Validates an over-the-air callsign. APRS-IS is more forgiving.

    Verifies that a valid callsign is valid:
    >>> valid_callsign('W2GMD-1')
    True
    >>>

    Verifies that an invalid callsign is invalid:
    >>> valid_callsign('BURRITOS-99')
    False
    >>>

    :param callsign: Callsign to validate.
    :type callsign: str

    :returns: True if valid, False otherwise.
    :rtype: bool
    """
    callsign = callsign.lstrip().rstrip().strip('*')

    if '-' in callsign:
        if not callsign.count('-') == 1:
            return False
        else:
            callsign, ssid = callsign.split('-')
    else:
        ssid = 0

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


def run_doctest():  # pragma: no cover
    """Runs doctests for this module."""
    import doctest
    return doctest.testmod()


if __name__ == '__main__':
    run_doctest()  # pragma: no cover
