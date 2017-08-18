#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS Module Function Definitions."""

import typing

import aprs  # pylint: disable=R0801

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'  # NOQA pylint: disable=R0801
__copyright__ = 'Copyright 2017 Greg Albrecht and Contributors'  # NOQA pylint: disable=R0801
__license__ = 'Apache License, Version 2.0'  # NOQA pylint: disable=R0801


AprsCallsign = typing.TypeVar('AprsCallsign', bound='aprs.Callsign')
AprsFrame = typing.TypeVar('AprsFrame', bound='aprs.Frame')


def parse_frame(raw_frame: typing.Union[bytes, str]) -> AprsFrame:
    """
    Parses an AX.25/APRS Frame from either plain-text or AX.25.
    """
    if isinstance(raw_frame, aprs.Frame):
        return raw_frame
    elif isinstance(raw_frame, str):
        return parse_frame_text(bytes(raw_frame, 'UTF-8'))
    elif isinstance(raw_frame, bytes) or isinstance(raw_frame, bytearray):
        if aprs.ADDR_INFO_DELIM in raw_frame:
            return parse_frame_ax25(raw_frame)
        else:
            return parse_frame_text(raw_frame)


def parse_frame_text(raw_frame: bytes) -> AprsFrame:
    """
    Parses and Extracts the components of a str Frame.
    """
    parsed_frame = aprs.Frame()
    _path = []

    # Source>Destination
    sd_delim = raw_frame.index(b'>')

    parsed_frame.set_source(raw_frame[:sd_delim])

    # Path:Info
    pi_delim = raw_frame.index(b':')

    parsed_path = raw_frame[sd_delim + 1:pi_delim]
    if b',' in parsed_path:
        for path in parsed_path.split(b','):
            _path.append(path)
        parsed_frame.set_destination(_path.pop(0))
        parsed_frame.set_path(_path)
    else:
        parsed_frame.set_destination(parsed_path)

    parsed_frame.set_info(raw_frame[pi_delim + 1:])

    return parsed_frame


def parse_frame_ax25(raw_frame: bytes) -> AprsFrame:
    """
    Parses and Extracts the components of an AX.25-Encoded Frame.
    """
    parsed_frame = aprs.Frame()
    kiss_call = False

    _frame = raw_frame.strip(aprs.AX25_FLAG)
    if (_frame.startswith(aprs.KISS_DATA_FRAME) or
            _frame.endswith(aprs.KISS_DATA_FRAME)):
        _frame = _frame.lstrip(aprs.KISS_DATA_FRAME)
        _frame = _frame.rstrip(aprs.KISS_DATA_FRAME)
        kiss_call = True

    # Use these two fields as the address/information delimiter
    frame_addressing, frame_information = _frame.split(aprs.ADDR_INFO_DELIM)

    info_field = frame_information.rstrip(b'\xFF\x07')

    destination = parse_callsign_ax25(frame_addressing, kiss_call)
    source = parse_callsign_ax25(frame_addressing[7:], kiss_call)

    paths = frame_addressing[7+7:]
    n_paths = int(len(paths) / 7)
    n = 0
    path = []
    while n < n_paths:
        path.append(parse_callsign_ax25(paths[:7]))
        paths = paths[7:]
        n += 1

    parsed_frame.set_source(source)
    parsed_frame.set_destination(destination)
    parsed_frame.set_path(path)
    parsed_frame.set_info(info_field)
    return parsed_frame


def parse_callsign(raw_callsign: bytes) -> AprsCallsign:
    """
    Parses an AX.25/APRS Callsign from plain-text or AX.25 input.
    """
    if isinstance(raw_callsign, aprs.Callsign):
        return raw_callsign
    try:
        return parse_callsign_ax25(raw_callsign)
    except:
        if isinstance(raw_callsign, str):
            return parse_callsign_text(bytes(raw_callsign, 'UTF-8'))
        else:
            return parse_callsign_text(raw_callsign)


def parse_callsign_text(raw_callsign: bytes) -> AprsCallsign:
    """
    Parses an AX.25/APRS Callsign & SSID from a plain-text AX.25/APRS Frame.
    """
    parsed_callsign: AprsCallsign = aprs.Callsign()
    _callsign = raw_callsign
    ssid = b'0'
    digi = False

    if b'*' in _callsign:
        _callsign = _callsign.strip(b'*')
        digi = True

    if b'-' in _callsign:
        _callsign, ssid = _callsign.split(b'-')

    parsed_callsign.set_callsign(_callsign)
    parsed_callsign.set_ssid(ssid)
    parsed_callsign.set_digi(digi)

    return parsed_callsign


def parse_callsign_ax25(raw_callsign: bytes, kiss_call: bool=False) -> AprsCallsign:
    """
    Extracts a Callsign and SSID from a AX.25 Encoded APRS Frame.

    :param frame: AX.25 Encoded APRS Frame.
    :type frame: str
    """
    parsed_callsign = aprs.Callsign()
    _callsign = bytes()
    digi = False

    for _chunk in raw_callsign[:6]:
        chunk = _chunk & 0xFF
        if chunk & 1:
            # aprx: /* Bad address-end flag ? */
            raise aprs.BadCallsignError('Bad address-end flag.')

        # Shift by one bit:
        chunk = chunk >> 1
        chr_chunk = chr(chunk)

        if chr_chunk.isalnum():
            _callsign += bytes([chunk])

    # 7th byte carries SSID or digi:
    seven_chunk = raw_callsign[6] & 0xFF
    ssid = (seven_chunk >> 1) & 0x0F  # Limit it to 4 bits.

    # FIXME gba@20170809: This works for KISS frames, but not otherwise.
    # Should consult: https://github.com/chrissnell/GoBalloon/blob/master/ax25/encoder.go
    if kiss_call:
        if seven_chunk >> 1 & 0x80:
            digi = True
    else:
        if seven_chunk & 0x80:
            digi = True

    parsed_callsign.set_callsign(_callsign)
    parsed_callsign.set_ssid(ssid)
    parsed_callsign.set_digi(digi)

    return parsed_callsign


def parse_info_field(raw_data: bytes, handler=None) -> bytes:
    if not raw_data:
        return bytes()
    elif isinstance(raw_data, aprs.InformationField):
        return raw_data
    elif isinstance(raw_data, bytes) or isinstance(raw_data, bytearray):
        data_type = b''
        data_type_field = chr(raw_data[0])
        data_type = aprs.DATA_TYPE_MAP.get(data_type_field)

        if data_type:
            if handler:
                handler_func = getattr(
                    handler,
                    "handle_data_type_%s" % data_type,
                    None
                )
                return handler_func(raw_data, data_type)

        return aprs.InformationField(raw_data, data_type, safe=True)


def default_data_handler(data: bytes, data_type: bytes) -> bytes:
    """
    Handler for Undefined Data Types.
    """
    try:
        decoded_data = data.decode('UTF-8')
    except UnicodeDecodeError as ex:
        decoded_data = data.decode('UTF-8', 'backslashreplace')

    return aprs.InformationField(decoded_data, data_type)
