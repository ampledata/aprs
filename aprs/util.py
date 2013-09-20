#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Utilities for the APRS Python Module."""

__author__ = 'Greg Albrecht W2GMD <gba@onbeep.com>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2013 OnBeep, Inc.'


import logging

import aprs.constants
import aprs.decimaldegrees
import aprs.util
import kiss.constants


logger = logging.getLogger(__name__)
logger.setLevel(aprs.constants.LOG_LEVEL)
console_handler = logging.StreamHandler()
console_handler.setLevel(aprs.constants.LOG_LEVEL)
formatter = logging.Formatter(aprs.constants.LOG_FORMAT)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.propagate = False


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
    dm = aprs.decimaldegrees.decimal2dm(dec)

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
    dm = aprs.decimaldegrees.decimal2dm(dec)

    deg = dm[0]
    abs_deg = abs(deg)

    if not deg == abs_deg:
        suffix = 'W'
    else:
        suffix = 'E'

    return ''.join([str(abs_deg), "%.2f" % dm[1], suffix])


# TODO: Convert doctest to unittest.
def decode_aprs_ascii_frame(ascii_frame):
    """
    Breaks an ASCII APRS Frame down to it's constituent parts.

    Test & Example
    ~~~~

        >>> frame = 'W2GMD-9>APOTC1,WIDE1-1,WIDE2-1:!3745.94N/12228.05W>118/010/A=000269 38C=Temp http://w2gmd.org/ Twitter: @ampledata'
        >>> decode_aprs_ascii_frame(frame)
        {'source': 'W2GMD-9', 'destination': 'APOTC1', 'text': '!3745.94N/12228.05W>118/010/A=000269 38C=Temp http://w2gmd.org/ Twitter: @ampledata', 'path': 'APOTC1,WIDE1-1,WIDE2-1'}


    :param frame: ASCII APRS Frame.
    :type frame: str

    :returns: Dictionary of APRS Frame parts: source, destination, path, text.
    :rtype: dict
    """
    logger.debug('frame=%s', ascii_frame)
    decoded_frame = {}
    frame_so_far = ''

    for c in ascii_frame:
        if '>' in c and not 'source' in decoded_frame:
            decoded_frame['source'] = frame_so_far
            frame_so_far = ''
        elif ':' in c and not 'path' in decoded_frame:
            decoded_frame['path'] = frame_so_far
            frame_so_far = ''
        else:
            frame_so_far = ''.join([frame_so_far, c])

    decoded_frame['text'] = frame_so_far
    decoded_frame['destination'] = decoded_frame['path'].split(',')[0]

    return decoded_frame


def format_aprs_frame(frame):
    formatted_frame = '>'.join([frame['source'], frame['destination']])
    formatted_frame = ','.join([formatted_frame, frame['path']])
    formatted_frame = ':'.join([formatted_frame, frame['text']])
    return formatted_frame


def create_callsign(raw_callsign):
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
    logger.debug('callsign=%s', callsign)

    if '-' in callsign:
        if not callsign.count('-') == 1:
            return False
        else:
            callsign, ssid = callsign.split('-')
    else:
        ssid = 0

    logger.debug('callsign=%s ssid=%s', callsign, ssid)

    if len(callsign) < 2 or len(callsign) > 6:
        return False

    if len(str(ssid)) < 1 or len(str(ssid)) > 2:
        return False

    for c in callsign:
        if not (c.isalpha() or c.isdigit()):
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
    return ','.join(extract_path(start, raw_frame))


def encode_callsign(callsign):
    call_sign = callsign['callsign']

    ct = (callsign['ssid'] << 1) | 0x60

    if '*' in call_sign:
        call_sign = call_sign.replace('*', '')
        ct |= 0x80

    while len(call_sign) < 6:
        call_sign = ''.join([call_sign, ' '])

    encoded = ''.join([chr(ord(p) << 1) for p in call_sign])
    return ''.join([encoded, chr(ct)])


def encode_frame(frame):
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
    logging.debug('raw_frame=%s', raw_frame)
    frame = {}
    frame_len = len(raw_frame)

    if frame_len > 16:
        for raw_slice in range(0, frame_len):
            # Is address field length correct?
            if ord(raw_frame[raw_slice]) & 0x01 and ((raw_slice + 1) % 7) == 0:
                n = (raw_slice + 1) / 7
                # Less than 2 callsigns?
                if 2 < n < 10:
                    if (ord(raw_frame[raw_slice + 1]) & 0x03 == 0x03 and
                            ord(raw_frame[raw_slice + 2]) == 0xf0):
                        frame['text'] = raw_frame[raw_slice + 3:]
                        frame['destination'] = full_callsign(
                            extract_callsign(raw_frame))
                        frame['source'] = full_callsign(
                            extract_callsign(raw_frame[7:]))
                        frame['path'] = format_path(n, raw_frame)

    logging.debug('frame=%s', frame)
    return frame


def run_doctest():
    import doctest
    import aprs.util
    return doctest.testmod(aprs.util)


if __name__ == '__main__':
    run_doctest()
