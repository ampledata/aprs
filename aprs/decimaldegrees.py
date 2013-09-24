#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyDecimalDegrees - geographic coordinates conversion utility.

Copyright (C) 2006-2013 by Mateusz Łoskot <mateusz@loskot.net>
Copyright (C) 2010-2013 by Evan Wheeler <ewheeler@unicef.org>

This file is part of PyDecimalDegrees module.

This software is provided 'as-is', without any express or implied warranty.
In no event will the authors be held liable for any damages arising from
the use of this software.

Permission is granted to anyone to use this software for any purpose,
including commercial applications, and to alter it and redistribute it freely,
subject to the following restrictions:
1. The origin of this software must not be misrepresented; you must not
   claim that you wrote the original software. If you use this software
   in a product, an acknowledgment in the product documentation would be
   appreciated but is not required.
2. Altered source versions must be plainly marked as such, and must not be
   misrepresented as being the original software.
3. This notice may not be removed or altered from any source distribution.

DESCRIPTION

DecimalDegrees module provides functions to convert between
degrees/minutes/seconds and decimal degrees.

Original source distribution:
http://mateusz.loskot.net/software/gis/pydecimaldegrees/

Inspired by Walter Mankowski's Geo::Coordinates::DecimalDegrees module
for Perl, originally located in CPAN Archives:
http://search.cpan.org/~waltman/Geo-Coordinates-DecimalDegrees-0.05/

doctest examples are based following coordinates:
DMS: 121 8' 6"
DM: 121 8.1'
DD: 121.135

To run doctest units just execut this module script as follows
(-v instructs Python to run script in verbose mode):

$ python decimaldegrees.py [-v]

"""


__revision__ = '$Revision: 1.1 $'


import decimal as libdecimal

from decimal import Decimal as D


def decimal2dms(decimal_degrees):
    """ Converts a floating point number of degrees to the equivalent
    number of degrees, minutes, and seconds, which are returned
    as a 3-element tuple of decimals. If 'decimal_degrees' is negative,
    only degrees (1st element of returned tuple) will be negative,
    minutes (2nd element) and seconds (3rd element) will always be positive.

    Example:

        >>> decimal2dms(121.135)
        (Decimal('121'), Decimal('8'), Decimal('6.000'))
        >>> decimal2dms(-121.135)
        (Decimal('-121'), Decimal('8'), Decimal('6.000'))

    """

    degrees = D(int(decimal_degrees))
    decimal_minutes = libdecimal.getcontext().multiply(
        (D(str(decimal_degrees)) - degrees).copy_abs(), D(60))
    minutes = D(int(decimal_minutes))
    seconds = libdecimal.getcontext().multiply(
        (decimal_minutes - minutes), D(60))
    return (degrees, minutes, seconds)


def decimal2dm(decimal_degrees):
    """
    Converts a floating point number of degrees to the degress & minutes.

    Returns a 2-element tuple of decimals.

    If 'decimal_degrees' is negative, only degrees (1st element of returned
    tuple) will be negative, minutes (2nd element) will always be positive.

    Example:

        >>> decimal2dm(121.135)
        (Decimal('121'), Decimal('8.100'))
        >>> decimal2dm(-121.135)
        (Decimal('-121'), Decimal('8.100'))

    """
    degrees = D(int(decimal_degrees))

    minutes = libdecimal.getcontext().multiply(
        (D(str(decimal_degrees)) - degrees).copy_abs(), D(60))

    return (degrees, minutes)


def dms2decimal(degrees, minutes, seconds):
    """ Converts degrees, minutes, and seconds to the equivalent
    number of decimal degrees. If parameter 'degrees' is negative,
    then returned decimal-degrees will also be negative.

    NOTE: this method returns a decimal.Decimal

    Example:

        >>> dms2decimal(121, 8, 6)
        Decimal('121.135')
        >>> dms2decimal(-121, 8, 6)
        Decimal('-121.135')

    """
    decimal = D(0)
    degs = D(str(degrees))
    mins = libdecimal.getcontext().divide(D(str(minutes)), D(60))
    secs = libdecimal.getcontext().divide(D(str(seconds)), D(3600))

    if degrees >= D(0):
        decimal = degs + mins + secs
    else:
        decimal = degs - mins - secs

    return libdecimal.getcontext().normalize(decimal)


def dm2decimal(degrees, minutes):
    """ Converts degrees and minutes to the equivalent number of decimal
    degrees. If parameter 'degrees' is negative, then returned decimal-degrees
    will also be negative.

    Example:

        >>> dm2decimal(121, 8.1)
        Decimal('121.135')
        >>> dm2decimal(-121, 8.1)
        Decimal('-121.135')

    """
    return dms2decimal(degrees, minutes, 0)


def run_doctest():  # pragma: no cover
    """Runs doctests for this module."""
    import doctest
    import decimaldegrees  # pylint: disable=W0406
    return doctest.testmod(decimaldegrees)


if __name__ == '__main__':
    run_doctest()  # pragma: no cover
