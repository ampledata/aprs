#!/usr/bin/env python


# http://stackoverflow.com/questions/2056750/lat-long-to-minutes-and-seconds
def lat_deg_to_dms(coord):
    """Converts DecDeg to APRS Coord format.
    See: http://ember2ash.com/lat.htm
    """
    degrees = int(coord)

    mindeg = abs(coord - degrees) * 60
    minutes = int(mindeg)

    secdeg = (mindeg - minutes) * 60
    seconds = int(secdeg)

    if not degrees == abs(degrees):
        suffix = 'S'
    else:
        suffix = 'N'

    ddmmss = [degrees, minutes, '.', seconds, suffix]
    return ''.join([str(c) for c in ddmmss])


def lng_deg_to_dms(coord):
    """Converts DecDeg to APRS Coord format.
    See: http://ember2ash.com/lat.htm
    """
    degrees = int(coord)

    mindeg = abs(coord - degrees) * 60
    minutes = int(mindeg)

    secdeg = (mindeg - minutes) * 60
    seconds = int(secdeg)

    if not degrees == abs(degrees):
        suffix = 'W'
    else:
        suffix = 'E'

    ddmmss = [abs(degrees), minutes, '.', seconds, suffix]
    return ''.join([str(c) for c in ddmmss])
