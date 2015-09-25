#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Utilities for the APRS Python Module."""

__author__ = 'Greg Albrecht W2GMD <gba@orionlabs.co>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2015 Orion Labs, Inc.'


import logging

import aprs.constants
import aprs.decimaldegrees
import kiss.constants


def dec2dm_lat(dec):
    """Converts DecDeg to APRS Coord format.
    See: http://ember2ash.com/lat.htm

    Source: http://stackoverflow.com/questions/2056750

    Example:
        >>> test_lat = 37.7418096
        >>> aprs_lat = dec2dm_lat(test_lat)
        >>> aprs_lat
        '3744.51N'
    """
    dec_min = aprs.decimaldegrees.decimal2dm(dec)

    deg = dec_min[0]
    abs_deg = abs(deg)

    if not deg == abs_deg:
        suffix = 'S'
    else:
        suffix = 'N'

    return ''.join([str(abs_deg), "%.2f" % dec_min[1], suffix])


def dec2dm_lng(dec):
    """Converts DecDeg to APRS Coord format.
    See: http://ember2ash.com/lat.htm

    Example:
        >>> test_lng = -122.38833
        >>> aprs_lng = dec2dm_lng(test_lng)
        >>> aprs_lng
        '12223.30W'
    """
    dec_min = aprs.decimaldegrees.decimal2dm(dec)

    deg = dec_min[0]
    abs_deg = abs(deg)

    if not deg == abs_deg:
        suffix = 'W'
    else:
        suffix = 'E'

    return ''.join([str(abs_deg), "%.2f" % dec_min[1], suffix])


def decode_aprs_ascii_frame(ascii_frame):
    """
    Breaks an ASCII APRS Frame down to it's constituent parts.

    :param frame: ASCII APRS Frame.
    :type frame: str

    :returns: Dictionary of APRS Frame parts: source, destination, path, text.
    :rtype: dict
    """
    logging.debug('frame=%s', ascii_frame)
    decoded_frame = {}
    frame_so_far = ''

    for char in ascii_frame:
        if '>' in char and 'source' not in decoded_frame:
            decoded_frame['source'] = frame_so_far
            frame_so_far = ''
        elif ':' in char and 'path' not in decoded_frame:
            decoded_frame['path'] = frame_so_far
            frame_so_far = ''
        else:
            frame_so_far = ''.join([frame_so_far, char])

    decoded_frame['text'] = frame_so_far
    decoded_frame['destination'] = decoded_frame['path'].split(',')[0]

    return decoded_frame


def format_aprs_frame(frame):
    """
    Formats APRS frame-as-dict into APRS frame-as-string.

    :param frame: APRS frame-as-dict
    :type frame: dict

    :return: APRS frame-as-string.
    :rtype: str
    """
    formatted_frame = '>'.join([frame['source'], frame['destination']])
    if frame['path']:
        formatted_frame = ','.join([formatted_frame, frame['path']])
    formatted_frame = ':'.join([formatted_frame, frame['text']])
    return formatted_frame


def create_callsign(raw_callsign):
    """
    Creates callsign-as-dict from callsign-as-string.

    :param raw_callsign: Callsign-as-string (with or without ssid).
    :type raw_callsign: str

    :return: Callsign-as-dict.
    :rtype: dict
    """
    if '-' in raw_callsign:
        call_sign, ssid = raw_callsign.split('-')
    else:
        call_sign = raw_callsign
        ssid = 0
    return {'callsign': call_sign, 'ssid': int(ssid)}


def full_callsign(callsign):
    """
    Returns a fully-formatted callsign (Callsign + SSID).

    :param callsign: Callsign Dictionary {'callsign': '', 'ssid': n}
    :type callsign: dict
    :returns: Callsign[-SSID].
    :rtype: str
    """
    if callsign['ssid'] > 0:
        return '-'.join([callsign['callsign'], str(callsign['ssid'])])
    else:
        return callsign['callsign']


def valid_callsign(callsign):
    """
    Validates callsign.

    :param callsign: Callsign to validate.
    :type callsign: str

    :returns: True if valid, False otherwise.
    :rtype: bool
    """
    logging.debug('callsign=%s', callsign)

    if '-' in callsign:
        if not callsign.count('-') == 1:
            return False
        else:
            callsign, ssid = callsign.split('-')
    else:
        ssid = 0

    logging.debug('callsign=%s ssid=%s', callsign, ssid)

    if (len(callsign) < 2 or len(callsign) > 6 or len(str(ssid)) < 1 or
            len(str(ssid)) > 2):
        return False

    for char in callsign:
        if not (char.isalpha() or char.isdigit()):
            return False

    if not str(ssid).isdigit():
        return False

    if int(ssid) < 0 or int(ssid) > 15:
        return False

    return True


def extract_callsign(raw_frame):
    """
    Extracts callsign from a raw KISS frame.

    :param raw_frame: Raw KISS Frame to decode.
    :returns: Dict of callsign and ssid.
    :rtype: dict
    """
    callsign = ''.join([chr(ord(x) >> 1) for x in raw_frame[:6]]).strip()
    ssid = (ord(raw_frame[6]) >> 1) & 0x0f
    return {'callsign': callsign, 'ssid': ssid}


def extract_path(start, raw_frame):
    """Extracts path from raw APRS KISS frame.

    :param start:
    :param raw_frame: Raw APRS frame from a KISS device.

    :return: Full path from APRS frame.
    :rtype: list
    """
    full_path = []

    for i in range(2, start):
        path = aprs.util.full_callsign(extract_callsign(raw_frame[i * 7:]))
        if path:
            if ord(raw_frame[i * 7 + 6]) & 0x80:
                full_path.append(''.join([path, '*']))
            else:
                full_path.append(path)

    return full_path


def format_path(start, raw_frame):
    """
    Formats path from raw APRS KISS frame.

    :param start:
    :param raw_frame: Raw APRS KISS frame.

    :return: Formatted APRS path.
    :rtype: str
    """
    return ','.join(extract_path(start, raw_frame))


def encode_callsign(callsign):
    """
    Encodes a callsign-dict within a KISS frame.

    :param callsign: Callsign-dict to encode.
    :type callsign: dict

    :return: KISS-encoded callsign.
    :rtype: str
    """
    call_sign = callsign['callsign']

    enc_ssid = (callsign['ssid'] << 1) | 0x60

    if '*' in call_sign:
        call_sign = call_sign.replace('*', '')
        enc_ssid |= 0x80

    while len(call_sign) < 6:
        call_sign = ''.join([call_sign, ' '])

    encoded = ''.join([chr(ord(p) << 1) for p in call_sign])
    return ''.join([encoded, chr(enc_ssid)])


def encode_frame(frame):
    """
    Encodes an APRS frame-as-dict as a KISS frame.

    :param frame: APRS frame-as-dict to encode.
    :type frame: dict

    :return: KISS-encoded APRS frame.
    :rtype: str
    """
    enc_frame = ''.join([
        encode_callsign(create_callsign(frame['destination'])),
        encode_callsign(create_callsign(frame['source'])),
        ''.join([encode_callsign(create_callsign(p))
                 for p in frame['path'].split(',')])
    ])

    return ''.join([
        enc_frame[:-1],
        chr(ord(enc_frame[-1]) | 0x01),
        kiss.constants.SLOT_TIME,
        chr(0xf0),
        frame['text']
    ])


def decode_frame(raw_frame):
    """
    Decodes a KISS-encoded APRS frame.

    :param raw_frame: KISS-encoded frame to decode.
    :type raw_frame: str

    :return: APRS frame-as-dict.
    :rtype: dict
    """
    logging.debug('raw_frame=%s', raw_frame)
    frame = {}
    frame_len = len(raw_frame)

    if frame_len > 16:
        for raw_slice in range(0, frame_len):
            # Is address field length correct?
            if ord(raw_frame[raw_slice]) & 0x01 and ((raw_slice + 1) % 7) == 0:
                i = (raw_slice + 1) / 7
                # Less than 2 callsigns?
                if 1 < i < 11:
                    if (ord(raw_frame[raw_slice + 1]) & 0x03 == 0x03 and
                            ord(raw_frame[raw_slice + 2]) in [0xf0, 0xcf]):
                        frame['text'] = raw_frame[raw_slice + 3:]
                        frame['destination'] = full_callsign(
                            extract_callsign(raw_frame))
                        frame['source'] = full_callsign(
                            extract_callsign(raw_frame[7:]))
                        frame['path'] = format_path(i, raw_frame)
                        return frame

    logging.debug('frame=%s', frame)
    return frame


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
    return format_aprs_frame(frame_dict)


def run_doctest():  # pragma: no cover
    """Runs doctests for this module."""
    import doctest
    import aprs.util  # pylint: disable=W0406,W0621
    return doctest.testmod(aprs.util)


if __name__ == '__main__':
    run_doctest()  # pragma: no cover
