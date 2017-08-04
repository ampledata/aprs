#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS Module Class Definitions."""

import itertools
import logging
import socket
import time

import bitarray
import pkg_resources
import requests

import aprs  # pylint: disable=R0801

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'  # NOQA pylint: disable=R0801
__copyright__ = 'Copyright 2017 Greg Albrecht and Contributors'  # NOQA pylint: disable=R0801
__license__ = 'Apache License, Version 2.0'  # NOQA pylint: disable=R0801


class APRS(object):

    """APRS Object."""

    _logger = logging.getLogger(__name__)  # pylint: disable=R0801
    if not _logger.handlers:  # pylint: disable=R0801
        _logger.setLevel(aprs.LOG_LEVEL)  # pylint: disable=R0801
        _console_handler = logging.StreamHandler()  # pylint: disable=R0801
        _console_handler.setLevel(aprs.LOG_LEVEL)  # pylint: disable=R0801
        _console_handler.setFormatter(aprs.LOG_FORMAT)  # pylint: disable=R0801
        _logger.addHandler(_console_handler)  # pylint: disable=R0801
        _logger.propagate = False  # pylint: disable=R0801

    def __init__(self, user, password='-1'):
        self.user = user

        try:
            version = pkg_resources.get_distribution(  # pylint: disable=E1101
                'aprs').version
        except:  # pylint: disable=W0702
            version = 'GIT'
        version_str = "Python APRS Module v%s" % version

        self._auth = ' '.join(
            ['user', user, 'pass', password, 'vers', version_str])

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


class Frame(object):

    """
    Frame Class.

    Defines the components of an APRS Frame and can decode a frame
    from either plain-text or AX.25.
    """

    __slots__ = ['frame', 'source', 'destination', 'path', 'text']

    _logger = logging.getLogger(__name__)  # pylint: disable=R0801
    if not _logger.handlers:  # pylint: disable=R0801
        _logger.setLevel(aprs.LOG_LEVEL)  # pylint: disable=R0801
        _console_handler = logging.StreamHandler()  # pylint: disable=R0801
        _console_handler.setLevel(aprs.LOG_LEVEL)  # pylint: disable=R0801
        _console_handler.setFormatter(aprs.LOG_FORMAT)  # pylint: disable=R0801
        _logger.addHandler(_console_handler)  # pylint: disable=R0801
        _logger.propagate = False  # pylint: disable=R0801

    def __init__(self, frame=None):
        self.source = ''
        self.destination = 'APYT70'
        self.path = []
        self.text = ''
        if frame is not None:
            #self.frame = kiss.strip_df_start(str(frame))
            self.parse(frame)

    def __repr__(self):
        full_path = [str(self.destination)]
        full_path.extend([str(p) for p in self.path])
        frame = "%s>%s:%s" % (
            self.source,
            ','.join(full_path),
            self.text
        )
        return frame

    def to_h(self):
        """
        Returns an Frame as a Hex String.
        """
        return str(self).encode('hex')

    def parse(self, frame=None):
        """
        Parses an Frame from either plain-text or AX.25.
        """
        if isinstance(frame, bytearray):
            self.parse_ax25(frame)
        else:
            self.parse_text(frame)

        if not self.source or not self.destination:
            self._logger.info(
                'Cannot decode frame=%s', frame)

    def parse_text(self, frame=None):
        """
        Parses and Extracts the components of an ASCII-Encoded Frame.
        """
        # Source>Destination
        sd_delim = frame.index('>')
        self.source = aprs.Callsign(frame[:sd_delim])
        self._logger.debug('self.source=%s', self.source)

        # Path:Info
        pi_delim = frame.index(':')
        _path = frame[sd_delim + 1:pi_delim]
        if ',' in _path:
            self.path = [aprs.Callsign(p) for p in _path.split(',')]
            self.destination = self.path.pop(0)
        else:
            self.destination = aprs.Callsign(_path)

        self._logger.debug('self.path=%s', self.path)
        self._logger.debug('self.destination=%s', self.destination)

        self.text = frame[pi_delim + 1:]
        self._logger.debug('self.text=%s', self.text)

    def parse_ax25(self, frame=None):
        """
        Parses and Extracts the components of an KISS-Encoded Frame.
        """
        frame = frame.strip(b'\x7E')

        # Control Field — This field is set to 0x03 (UI-frame)
        control_field = b'\x03'
        # Protocol ID — This field is set to 0xf0 (no layer 3 protocol).
        protocol_id = b'\xF0'
        # Use these two fields as the address/information delimiter
        frame_addressing, frame_information = frame.split(
            control_field + protocol_id)

        self.text = frame_information[:-2]

        self._logger.debug('frame_addressing="%s"', frame_addressing)
        self._logger.debug('self.text="%s"', self.text)

        self.destination = aprs.Callsign(frame_addressing)
        self.source = aprs.Callsign(frame_addressing[7:])

        paths = frame_addressing[7+7:]
        n_paths = int(len(paths) / 7)
        n = 0
        while n < n_paths:
            self.path.append(aprs.Callsign(paths[:7]))
            paths = paths[7:]
            n += 1

    def encode_ax25(self):
        """
        Encodes an Frame as AX.25.
        """
        encoded_frame = bytearray()
        encoded_frame.append(0x7E)
        encoded_frame.extend(self.destination.encode_ax25())
        encoded_frame.extend(self.source.encode_ax25())
        for path_call in self.path:
            encoded_frame.extend(path_call.encode_ax25())
        encoded_frame.append(0x03)
        encoded_frame.append(0xF0)
        encoded_frame.extend([ord(t) for t in self.text])

        fcs = aprs.FCS()
        for bit in encoded_frame:
            fcs.update_bit(bit)

        encoded_frame.extend(fcs.digest())
        encoded_frame.append(0x7E)
        return encoded_frame


class Callsign(object):

    """
    Callsign Class.

    Defines parts of an APRS AX.25 Callsign.
    """

    _logger = logging.getLogger(__name__)  # pylint: disable=R0801
    if not _logger.handlers:  # pylint: disable=R0801
        _logger.setLevel(aprs.LOG_LEVEL)  # pylint: disable=R0801
        _console_handler = logging.StreamHandler()  # pylint: disable=R0801
        _console_handler.setLevel(aprs.LOG_LEVEL)  # pylint: disable=R0801
        _console_handler.setFormatter(aprs.LOG_FORMAT)  # pylint: disable=R0801
        _logger.addHandler(_console_handler)  # pylint: disable=R0801
        _logger.propagate = False  # pylint: disable=R0801

    __slots__ = ['callsign', 'ssid', 'digi']

    def __init__(self, callsign=None):
        self.callsign = ''
        self.ssid = str(0)
        self.digi = False
        if callsign is not None:
            self.parse(callsign)

    def __repr__(self):
        call_repr = self.callsign

        # Don't print callsigns with ssid 0.
        try:
            if int(self.ssid) > 0:
                call_repr = '-'.join([self.callsign, str(self.ssid)])
        except ValueError:
            if self.ssid != 0:
                call_repr = '-'.join([self.callsign, str(self.ssid)])

        # If callsign was digipeated, append '*'.
        if self.digi:
            return ''.join([call_repr, '*'])
        else:
            return call_repr

    def to_h(self):
        """
        Returns a Callsign as a Hex String.
        """
        return str(self).encode('hex')

    def parse(self, callsign):
        """
        Parse and extract the components of a Callsign from ASCII or KISS.
        """
        if isinstance(callsign, bytearray):
            self._parse_ax25(callsign)
        else:
            self._parse_text(callsign)

        if not aprs.valid_callsign(self.callsign):
            raise aprs.BadCallsignError(
                'Could not extract callsign from %s' %
                self.callsign)

    def _parse_text(self, callsign):
        """
        Parses and extracts a Callsign and SSID from plain-text APRS
        Callsign or Callsign-SSID.

        :param callsign: ASCII-Encoded APRS Callsign
        :type callsign: str
        """
        self._logger.debug('callsign="%s"', callsign)
        _callsign = str(callsign).lstrip().rstrip()
        ssid = str(0)

        if '*' in str(_callsign):
            _callsign = _callsign.strip('*')
            self.digi = True

        if '-' in _callsign:
            _callsign, ssid = _callsign.split('-')

        self.callsign = _callsign
        self.ssid = ssid.lstrip().rstrip()

    def _parse_ax25(self, callsign):
        """
        Extracts a Callsign and SSID from a AX.25 Encoded APRS Frame.

        :param frame: AX.25 Encoded APRS Frame.
        :type frame: str
        """
        self._logger.debug('callsign="%s"', callsign)
        self._logger.debug('type callsign="%s"', type(callsign))
        if not len(callsign) >= 6:
            raise aprs.BadCallsignError('Callsign is too short.')

        for _chunk in callsign[:6]:
            chunk = _chunk & 0xFF
            if chunk & 1:
                # aprx: /* Bad address-end flag ? */
                raise aprs.BadCallsignError('Bad address-end flag.')

            # Shift by one bit:
            chunk = chunk >> 1
            self._logger.debug('chunk={}'.format(chunk))
            chr_chunk = chr(chunk)

            if chr_chunk.isalnum():
                self.callsign += chr_chunk
            #else:
            #    raise aprs.BadCallsignError('Invalid characters in callsign.')

        self._logger.debug('self.callsign=%s', self.callsign)

        # 7th byte carries SSID or digi:
        seven_chunk = callsign[6] & 0xFF
        self.ssid = str((seven_chunk >> 1) & 0x0F)
        self._logger.debug('self.ssid=%s', self.ssid)

        if seven_chunk & 0x80:
            self.digi = True
        self._logger.debug('self.digi=%s', self.digi)

    def encode_ax25(self):
        """
        Encodes Callsign (or Callsign-SSID) as AX.25.
        """
        encoded_callsign = bytearray(self.callsign, encoding='UTF-8')

        encoded_ssid = (int(self.ssid) << 1) | 0x60

        if self.digi:
            # _callsign = ''.join([_callsign, '*'])
            encoded_ssid |= 0x80

        # Pad the callsign to at least 6 characters.
        while len(encoded_callsign) < 6:
            encoded_callsign.append(0)

        ec = bytearray()
        for pos in encoded_callsign:
            ec.append(pos << 1)

        ec.append(encoded_ssid)
        return ec


class TCP(APRS):

    """APRS-IS TCP Class."""

    def __init__(self, user, password, servers=None, aprs_filter=None):
        super(TCP, self).__init__(user, password)
        servers = servers or aprs.APRSIS_SERVERS
        aprs_filter = aprs_filter or '/'.join(['p', user])

        self._full_auth = ' '.join([self._auth, 'filter', aprs_filter])

        self.servers = itertools.cycle(servers)
        self.use_i_construct = True
        self._connected = False

    def start(self):
        """
        Connects & logs in to APRS-IS.
        """
        while not self._connected:
            servers = next(self.servers)
            if ':' in servers:
                server, port = servers.split(':')
                port = int(port)
            else:
                server = servers
                port = aprs.APRSIS_FILTER_PORT

            try:
                addr_info = socket.getaddrinfo(server, port)

                self.interface = socket.socket(*addr_info[0][0:3])

                # Connect
                self._logger.info(
                    "Connect To %s:%i", addr_info[0][4][0], port)

                self.interface.connect(addr_info[0][4])

                server_hello = self.interface.recv(1024)

                self._logger.info(
                    'Connect Result "%s"', server_hello.rstrip())

                # Auth
                self._logger.info(
                    "Auth To %s:%i", addr_info[0][4][0], port)
                self.interface.sendall(self._full_auth + '\n\r')

                server_return = self.interface.recv(1024)
                self._logger.info(
                    'Auth Result "%s"', server_return.rstrip())

                self._connected = True
            except socket.error as ex:
                self._logger.warn(
                    "Error when connecting to %s:%d: '%s'",
                    server, port, str(ex))
                time.sleep(1)

    def send(self, frame):
        """
        Sends frame to APRS-IS.

        :param frame: Frame to send to APRS-IS.
        :type frame: str
        """
        self._logger.info('Sending frame="%s"', frame)
        return self.interface.send("%s\n\r" % frame)  # Ensure cast->str.

    def receive(self, callback=None):
        """
        Receives from APRS-IS.

        :param callback: Optional callback to deliver frame to.
        :type callback: func

        :returns: Nothing, but calls a callback with an Frame object.
        :rtype: None
        """
        recvd_data = ''

        try:
            while 1:
                recv_data = self.interface.recv(aprs.RECV_BUFFER)

                if not recv_data:
                    break

                recvd_data += recv_data

                self._logger.debug('recv_data=%s', recv_data.strip())

                if recvd_data.endswith('\r\n'):
                    lines = recvd_data.strip().split('\r\n')
                    recvd_data = ''
                else:
                    lines = recvd_data.split('\r\n')
                    recvd_data = str(lines.pop(-1))

                for line in lines:
                    if line.startswith('#'):
                        if 'logresp' in line:
                            self._logger.debug('logresp=%s', line)
                    else:
                        self._logger.debug('line=%s', line)
                        if callback:
                            callback(kiss.Frame(line))

        except socket.error as sock_err:
            self._logger.error(sock_err)
            raise


class UDP(APRS):

    """APRS-IS UDP Class."""

    def __init__(self, user, password='-1', server=None, port=None):
        super(UDP, self).__init__(user, password)
        server = server or aprs.APRSIS_SERVERS[0]
        port = port or aprs.APRSIS_RX_PORT
        self._addr = (server, int(port))
        self.use_i_construct = True

    def start(self):
        """
        Connects & logs in to APRS-IS.
        """
        self.interface = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, frame):
        """
        Sends frame to APRS-IS.

        :param frame: Frame to send to APRS-IS.
        :type frame: str
        """
        self._logger.info('Sending frame="%s"', frame)
        content = "\n".join([self._auth, str(frame)])
        return self.interface.sendto(content, self._addr)


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
        self._logger.info('Sending frame="%s"', frame)
        content = "\n".join([self._auth, str(frame)])
        result = self.interface(self.url, data=content, headers=self.headers)
        return result.status_code == 204
