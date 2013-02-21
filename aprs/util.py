#!/usr/bin/env python


import decimaldegrees


# http://stackoverflow.com/questions/2056750/lat-long-to-minutes-and-seconds
def dec2dm_lat(dec):
    """Converts DecDeg to APRS Coord format.
    See: http://ember2ash.com/lat.htm

    Example:
        >>> test_lat = 37.7418096
        >>> aprs_lat = dec2dm_lat(test_lat)
        >>> aprs_lat
        '3744.51N'
    """
    dm = decimaldegrees.decimal2dm(dec)

    deg = dm[0]
    abs_deg = abs(deg)

    if not deg == abs_deg:
        suffix = 'S'
    else:
        suffix = 'N'

    return ''.join([str(abs_deg), "%.2f" % dm[1], suffix])


def dec2dm_lng(dec):
    """Converts DecDeg to APRS Coord format.
    See: http://ember2ash.com/lat.htm

    Example:
        >>> test_lng = -122.38833
        >>> aprs_lng = dec2dm_lng(test_lng)
        >>> aprs_lng
        '12223.30W'
    """
    dm = decimaldegrees.decimal2dm(dec)

    deg = dm[0]
    abs_deg = abs(deg)

    if not deg == abs_deg:
        suffix = 'W'
    else:
        suffix = 'E'

    return ''.join([str(abs_deg), "%.2f" % dm[1], suffix])


def run_doctest():
    import doctest
    import util
    return doctest.testmod(util)


if __name__ == '__main__':
    run_doctest()
