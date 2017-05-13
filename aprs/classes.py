#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS Module Class Definitions."""

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)

import binascii
import logging
import socket
import struct

import bitarray
import requests
import six

import aprs

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2017 Greg Albrecht and Contributors'
__license__ = 'Apache License, Version 2.0'


class APRS(object):

    """APRS Object."""

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprs.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprs.LOG_LEVEL)
        _console_handler.setFormatter(aprs.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, user, password='-1'):
        self.user = user
        self._auth = ' '.join(
            ['user', user, 'pass', password, 'vers', aprs.APRSIS_SW_VERSION])
        self._full_auth = None
        self.interface = None
        self.use_i_construct = False

    def start(self):
        """
        Abstract method for starting connection to APRS-IS.
        """
        pass

    def send(self, message):
        """
        Abstract method for sending messages to APRS-IS.
        """
        pass

    def receive(self, callback=None):
        """
        Abstract method for receiving messages from APRS-IS.
        """
        pass


class CallsignOLD(object):

    """
    Callsign Class.
    Defines parts of a Callsign decoded from either ASCII or KISS.
    """

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprs.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprs.LOG_LEVEL)
        _console_handler.setFormatter(aprs.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    __slots__ = ['callsign', 'ssid', 'digi']

    def __init__(self, callsign):
        self.callsign = ''
        self.ssid = str(0)
        self.digi = False
        self.parse(callsign)

    def __repr__(self):
        if int(self.ssid) > 0:
            call_repr = '-'.join([self.callsign, str(self.ssid)])
        else:
            call_repr = self.callsign

        if self.digi:
            return ''.join([call_repr, '*'])
        else:
            return call_repr

    def to_h(self):
        """
        Returns a Callsign as a Hex String.
        """
        return binascii.hexlify(self)

    def parse(self, callsign):
        """
        Parse and extract the components of a Callsign from ASCII or KISS.
        """
        try:
            self._extract_callsignsign(callsign)
        except:
            pass
            # self._logger.debug(
            #    'Not a KISS Callsign? "%s"',
            #    binascii.hexlify(callsign.encode('utf-8'))
            # )

        if not aprs.valid_callsign(self.callsign):
            self.parse_text(callsign)

        if not aprs.valid_callsign(self.callsign):
            raise aprs.BadCallsignError(
                'Could not extract callsign from %s',
                binascii.hexlify(self.callsign)
            )

    def parse_text(self, callsign):
        """
        Parses and extracts a Callsign and SSID from an ASCII-Encoded APRS
        Callsign or Callsign-SSID.

        :param callsign: ASCII-Encoded APRS Callsign
        :type callsign: str
        """
        _callsign = callsign
        ssid = str(0)

        if '-' in callsign:
            _callsign, ssid = callsign.split('-')

        if _callsign[-1] == '*':
            _callsign = _callsign[:-1]
            self.digi = True

        self.callsign = _callsign.lstrip().rstrip()
        self.ssid = ssid.lstrip().rstrip()

    def encode_kiss(self):
        """
        Encodes Callsign (or Callsign-SSID) as KISS.
        """
        encoded_ssid = (int(self.ssid) << 1) | 0x60
        _callsign = self.callsign

        if self.digi:
            # _callsign = ''.join([_callsign, '*'])
            encoded_ssid |= 0x80

        # Pad the callsign to at least 6 characters.
        while len(_callsign) < 6:
            _callsign = ''.join([_callsign, ' '])

        encoded_callsign = ''.join([chr(ord(p) << 1) for p in _callsign])

        return ''.join([encoded_callsign, chr(encoded_ssid)])

    def _extract_callsignsign(self, frame):
        """
        Extracts a Callsign and SSID from a KISS-Encoded APRS Frame.

        :param frame: KISS-Encoded APRS Frame as str of octs.
        :type frame: str
        """
        callsign = ''.join([chr(x >> 1) for x in frame[:6]])
        self.callsign = callsign.lstrip().rstrip()
        self.ssid = str((frame[6] >> 1) & 0x0F)


class Callsign(object):

    """
    Callsign Class.

    Callsign with no SSID:
    >>> c = Callsign('W2GMD')
    >>> c.callsign
    'W2GMD'
    >>> c.ssid
    '0'
    >>> c
    W2GMD
    >>> c.digipeated
    False
    >>> k = c.encode()
    >>> k
    b'\xaed\x8e\x9a\x88`'
    >>> c2 = Callsign(k)
    >>> c2.ssid
    '0'
    >>> c2.callsign
    'W2GMD'
    >>> c2
    W2GMD

    Digipeated Callsign:
    >>> c = Callsign('W2GMD*')
    >>> c.callsign
    'W2GMD'
    >>> c.ssid
    '0'
    >>> c
    W2GMD*
    >>> c.digipeated
    True
    >>> k = c.encode()
    >>> k
    b'\xaed\x8e\x9a\x88\xe0'
    >>> c2 = Callsign(k)
    >>> c2.ssid
    '0'
    >>> c2.callsign
    'W2GMD'
    >>> c2
    W2GMD*


    Digipeated Callsign:
    >>> c = Callsign('KF4MKT*')
    >>> c.callsign
    'KF4MKT'
    >>> c.ssid
    '0'
    >>> c
    KF4MKT*
    >>> c.digipeated
    True
    >>> k = c.encode()
    >>> k
    b'\x96\x8ch\x9a\x96\xa8\xe0'
    >>> c2 = Callsign(k)
    >>> c2.ssid
    '0'
    >>> c2.callsign
    'KF4MKT'
    >>> c2
    KF4MKT*

    Callsign with SSID 0:
    >>> c = Callsign('W2GMD-0')
    >>> c.callsign
    'W2GMD'
    >>> c.ssid
    '0'
    >>> c
    W2GMD
    >>> c.digipeated
    False
    >>> k = c.encode()
    >>> k
    b'\xaed\x8e\x9a\x88`'
    >>> c2 = Callsign(k)
    >>> c2.ssid
    '0'
    >>> c2.callsign
    'W2GMD'
    >>> c2
    W2GMD

    Callsign with an SSID of 1:
    >>> c = Callsign('W2GMD-1')
    >>> c.callsign
    'W2GMD'
    >>> c.ssid
    '1'
    >>> c
    W2GMD-1
    >>> c.digipeated
    False
    >>> k = c.encode()
    >>> k
    b'\xaed\x8e\x9a\x88b'
    >>> c2 = Callsign(k)
    >>> c2.ssid
    '1'
    >>> c2.callsign
    'W2GMD'
    >>> c2
    W2GMD-1

    Callsign with an SSID of 11:
    >>> c = Callsign('W2GMD-11')
    >>> c.callsign
    'W2GMD'
    >>> c.ssid
    '11'
    >>> c
    W2GMD-11
    >>> c.digipeated
    False
    >>> k = c.encode()
    >>> k
    b'\xaed\x8e\x9a\x88v'
    >>> c2 = Callsign(k)
    >>> c2.ssid
    '11'
    >>> c2.callsign
    'W2GMD'
    >>> c2
    W2GMD-11

    Short Callsign:
    >>> c = Callsign('W2G')
    >>> c.callsign
    'W2G'
    >>> c.ssid
    '0'
    >>>
    W2G
    >>> c.digipeated
    False
    >>> e = c.encode()
    >>> e
    b'\\xaed\\x8e`'
    >>> type(e)
    <class 'bytes'>
    >>> c2 = Callsign(e)
    >>> c2
    W2G
    >>> c2.ssid
    '0'
    >>> c2.callsign
    'W2G'

    >>> f = bytes.fromhex('00a88aa6a84040e0ae84649ea6b4ff03f02c54686520717569636b2062726f776e20666f78206a756d7073206f76657220746865206c617a7920646f6721202030323532206f662031303030')  # NOQA
    >>> f[1:]
    b'\\xa8\\x8a\\xa6\\xa8@@\\xe0\\xae\\x84d\\x9e\\xa6\\xb4\\xff\\x03\\xf0,The quick brown fox jumps over the lazy dog!  0252 of 1000'  # NOQA
    >>> d = Callsign(f[1:7])
    >>> d
    TEST
    >>> d.callsign
    'TEST'
    >>> d.ssid
    '0'
    >>> s = Callsign(f[8:15])
    >>> s
    WB2OSZ-15
    >>> s.callsign
    'WB2OSZ'
    >>> s.ssid
    '15'
    """

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprs.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprs.LOG_LEVEL)
        _console_handler.setFormatter(aprs.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    __slots__ = ['callsign', 'ssid', 'digipeated']

    def __init__(self, callsign=None):
        self.callsign = callsign
        self.ssid = '0'
        self.digipeated = False
        if self.callsign is not None:
            self.parse()

    def __repr__(self):
        if self.ssid != '0':
            call_repr = '-'.join([self.callsign, self.ssid])
        else:
            call_repr = self.callsign

        if self.digipeated:
            call_repr = ''.join([call_repr, '*'])

        return call_repr

    def parse(self, callsign=None):
        if callsign is not None:
            self.callsign = callsign

        if isinstance(self.callsign, bytes):
            self.decode()
        else:
            self._parse_text()

    def _parse_text(self):
        if '*' in self.callsign:
            self.callsign = self.callsign.replace('*', '')
            self.digipeated = True

        if '-' in self.callsign:
            self.callsign, self.ssid = self.callsign.split('-')

    def encode(self):
        _callsign = self.callsign.upper()
        encoded_callsign = b''

        encoded_ssid = (int(self.ssid) << 1) | 0x60

        if self.digipeated:
            encoded_ssid |= 0x80

        for char in _callsign:
            encoded_char = ord(char) << 1
            encoded_callsign += bytes([encoded_char])

        return b''.join([encoded_callsign, bytes([encoded_ssid])])

    def decode(self, callsign=None):
        _callsign = ''
        if callsign is not None:
            self.callsign = callsign

        self._logger.debug('len(self.callsign)=%s', len(self.callsign))
        self._logger.debug('self.callsign=%s', self.callsign)

        # To determine the encoded SSID:
        # 1. Right-shift (or un-left-shift) the SSID bit [-1].
        # 2. mod15 the bit (max SSID of 15).
        self.ssid = str((self.callsign[-1] >> 1) & 0x0F)  # aka 15

        # not quite working...
        # if self.callsign[-1] & 0x80:
        #    self.digipeated = True

        for char in self.callsign[:-1]:
            _callsign += chr(char >> 1)

        self.callsign = _callsign.strip()


class Frame(object):

    """
    Frame Class.

    Defines the components of an APRS Frame and can decode both Plain-Text and
    AX.25 Frames.
    """

    __slots__ = ['frame', 'source', 'destination', 'path', 'text', 'full_path']

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprs.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprs.LOG_LEVEL)
        _console_handler.setFormatter(aprs.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, frame=None):
        self.source = ''
        self.destination = ''
        self.path = []
        self.full_path = ''
        self.text = ''
        self.frame = frame
        if self.frame is not None:
            self.parse()

    def __repr__(self):
        _path = [str(self.destination)]
        _path.extend([str(p) for p in self.path])
        self.full_path = ','.join(_path)
        return "{f.source}>{f.full_path}:{f.text}".format(f=self)

    def parse(self, frame=None):
        """
        Parses an Frame from either Plain-Text or AX.25.
        """
        # Allows to be called as class method:
        if frame is not None:
            self.frame = frame

        if isinstance(self.frame, bytes):
            self.decode()
        else:
            self._parse_text()

    def _parse_text(self):
        """
        Parses and Extracts the components of an Plain-Text Frame.
        """
        frame_so_far = ''

        for char in self.frame:
            if '>' in char and not self.source:
                self.source = aprs.Callsign(frame_so_far)
                frame_so_far = ''
            elif ':' in char:
                if not self.path:
                    if ',' in frame_so_far:
                        self.destination = aprs.Callsign(
                            frame_so_far.split(',')[0])
                        self.path = []
                        for path in frame_so_far.split(',')[1:]:
                            self.path.append(aprs.Callsign(path))
                        frame_so_far = ''
                    elif not self.destination:
                        self.destination = aprs.Callsign(frame_so_far)
                        frame_so_far = ''
                    else:
                        frame_so_far = ''.join([frame_so_far, char])
                else:
                    frame_so_far = ''.join([frame_so_far, char])
            else:
                frame_so_far = ''.join([frame_so_far, char])

        self.text = frame_so_far

    def decode(self, frame=None):
        """
        Decodes AX.25 Frames.
        """
        if frame is not None:
            self.frame = frame

        frame_len = len(self.frame)
        self._logger.debug('len(frame)=%s', frame_len)
        for frame_slice in range(0, frame_len):
            # Is address field length correct?
            # Find the first ODD Byte followed by the next boundary:
            if (self.frame[frame_slice] & 0x01
                    and ((frame_slice + 1) % 7) == 0):

                bound = int((frame_slice + 1) / 7)

                # Less than 2 callsigns?
                if 1 < bound < 11:
                    # For frames <= 70 bytes
                    if frame_len >= frame_slice + 2:
                        if (self.frame[frame_slice + 1] & 0x03 == 0x03 and
                                self.frame[frame_slice + 2] in
                                [aprs.UI_PROTOCOL_ID[0], 0xCF]):
                            self._extract_text(frame_slice)
                            self._extract_destination()
                            self._extract_source()
                            self._extract_path(bound)

    def encode(self):
        frame = b''.join([
            aprs.FLAG,
            self._encode_header(),
            # bytes(self.text, 'UTF-8'),
            # self.fcs()
        ])
        return frame

    def fcs(self):
        content = bitarray.bitarray(endian='little')
        content.frombytes(
            b''.join([self._encode_header(), bytes(self.text, 'UTF-8')]))

        fcs = FCS()
        for bit in content:
            fcs.update_bit(bit)

        return fcs.digest()

    def _encode_addresses(self):
        """
        Encodes an Frame as AX.25.
        """
        addresses = bytearray(
            b''.join([
                self.destination.encode(),
                self.source.encode(),
                b''.join([x.encode() for x in self.path])
            ])
        )

        # set the low order (first, with eventual little bit endian encoding)
        # bit in order to flag the end of the address string
        addresses[-1] |= 0x01

        return addresses

    def _encode_header(self):
        header = b''.join([
            self._encode_addresses(),
            aprs.CONTROL_FIELD,
            aprs.UI_PROTOCOL_ID
        ])
        print("header={}".format(header))
        return header

    def _extract_text(self, frame_slice):
        """
        Extracts a Text portion of an AX.25 Frame.
        """
        self.text = self.frame[frame_slice + 3:].decode('UTF-8', 'ignore')

    def _extract_source(self):
        """
        Extracts the Source callsign from an AX.25 Frame.
        """
        self.source = self._extract_callsign(self.frame[7:14])

    def _extract_destination(self):
        """
        Extracts the Destination callsign from an AX.25 Frame.
        """
        self.destination = self._extract_callsign(self.frame[:7])

    def _extract_callsign(self, frame_slice):
        """
        Extracts Callsign from an AX.25 Frame Slice.
        """
        self._logger.debug('Extracting Callsign from "%s"', frame_slice)
        return aprs.Callsign(frame_slice)

    def _extract_path(self, start):
        """
        Extracts Path callsigns from AX.25 Frame.
        """
        for bound in range(2, start):
            path_call = self._extract_callsign(
                self.frame[bound * 7:bound * 7 + 7])

            if path_call:
                # FIXME (gba@20170210) Digi detection is broken.
                # if self.frame[bound * 7 + 7] & 0x80:
                #    path_call.digipeated = True

                self.path.append(path_call)


class TCP(APRS):

    """APRS-IS TCP Class."""

    def __init__(self, user, password='-1', server=None, port=None,  # NOQA pylint: disable=R0913
                 aprs_filter=None):
        super(TCP, self).__init__(user, password)
        server = server or aprs.APRSIS_SERVER
        port = port or aprs.APRSIS_FILTER_PORT
        self.address = (server, int(port))
        aprs_filter = aprs_filter or '/'.join(['p', user])
        self._full_auth = ' '.join([self._auth, 'filter', aprs_filter])
        self.use_i_construct = True

    def _send(self, data):
        """
            Send a string to the socket, encoding as bytes if necessary
        """
        if isinstance(data, six.string_types):
            data = data.encode('iso-8859-1')
        self.interface.sendall(data)

    def start(self):
        """
        Connects & logs in to APRS-IS.
        """
        self.interface = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._logger.info('Connecting to to "%s"', self.address)
        self.interface.connect(self.address)

        self._logger.debug('Sending full_auth=%s', self._full_auth)
        self._send(self._full_auth + '\r\n')

    def send(self, frame):
        """
        Sends frame to APRS-IS.

        :param frame: Frame to send to APRS-IS.
        :type frame: str
        """
        self._logger.debug('Sending frame="%s"', frame)
        return self._send("%s\r\n" % frame)  # Ensure cast->str.

    def receive(self, callback=None):
        """
        Receives from APRS-IS.

        :param callback: Optional callback to deliver frame to.
        :type callback: func

        :returns: Nothing, but calls a callback with an Frame object.
        :rtype: None
        """
        recvd_data = b''

        try:
            while 1:
                recv_data = self.interface.recv(aprs.RECV_BUFFER)

                if not recv_data:
                    break

                recvd_data += recv_data

                self._logger.debug('recv_data=%s', recv_data.strip())

                if recvd_data.endswith(b'\r\n'):
                    lines = recvd_data.strip().split(b'\r\n')
                    recvd_data = b''
                else:
                    lines = recvd_data.split(b'\r\n')
                    recvd_data = lines.pop(-1)

                for line in lines:
                    if line.startswith(b'#'):
                        if b'logresp' in line:
                            self._logger.debug('logresp=%s', line)
                    else:
                        self._logger.debug('line=%s', line)
                        if callback:
                            callback(aprs.Frame(line.decode('iso-8859-1')))

        except socket.error as sock_err:
            self._logger.error(sock_err)
            raise


class UDP(APRS):

    """APRS-IS UDP Class."""

    def __init__(self, user, password='-1', server=None, port=None):
        super(UDP, self).__init__(user, password)
        server = server or aprs.APRSIS_SERVER
        port = port or aprs.APRSIS_RX_PORT
        self._addr = (server, int(port))
        self.use_i_construct = True

    def start(self):
        """
        Connects & logs in to APRS-IS.
        """
        self.interface = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _send(self, data):
        """
            Send a string to the socket, encoding as bytes if necessary
        """
        if isinstance(data, six.string_types):
            data = data.encode('iso-8859-1')
        return self.interface.sendto(data, self._addr)

    def send(self, frame):
        """
        Sends frame to APRS-IS.

        :param frame: Frame to send to APRS-IS.
        :type frame: str
        """
        self._logger.debug('frame="%s"', frame)
        content = "\n".join([self._auth, str(frame)])
        return self._send(content)


class HTTP(APRS):

    """APRS-IS HTTP Class."""

    def __init__(self, user, password='-1', url=None, headers=None):
        super(HTTP, self).__init__(user, password)
        self.url = url or aprs.APRSIS_URL
        self.headers = headers or aprs.APRSIS_HTTP_HEADERS
        self.use_i_construct = True

    def start(self):
        """
        Connects & logs in to APRS-IS.
        """
        self.interface = requests.post

    def send(self, frame):
        """
        Sends frame to APRS-IS.

        :param frame: Frame to send to APRS-IS.
        :type frame: str
        """
        content = "\n".join([self._auth, str(frame)])
        result = self.interface(self.url, data=content, headers=self.headers)
        return result.status_code == 204


class FCS(object):

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprs.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprs.LOG_LEVEL)
        _console_handler.setFormatter(aprs.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self):
        self.fcs = 0xffff

    def update_bit(self, bit):
        check = (self.fcs & 0x1 == 1)
        self.fcs >>= 1
        if check != bit:
            self.fcs ^= 0x8408

    def update(self, ubytes):
        for byte in (ord(b) for b in ubytes):
            for i in range(7, -1, -1):
                self.update_bit((byte >> i) & 0x01 == 1)

    def digest(self):
        # digest is two bytes, little endian
        return struct.pack("<H", ~self.fcs % 2**16)
