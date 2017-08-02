#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS Module Class Definitions."""

import itertools
import logging
import socket
import time

import pkg_resources
import requests

import kiss  # pylint: disable=R0801

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


class Callsign(object):

    """
    Callsign Class.
    Defines parts of a Callsign decoded from either ASCII or KISS.
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

    def __init__(self, callsign):
        self.callsign = ''
        self.ssid = str(0)
        self.digi = False
        self.parse(callsign)

    def __repr__(self):
        call_repr = self.callsign

        try:
            if int(self.ssid) > 0:
                call_repr = '-'.join([self.callsign, str(self.ssid)])
        except ValueError:
            if self.ssid != 0:
                call_repr = '-'.join([self.callsign, str(self.ssid)])

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
        try:
            self._extract_kiss_callsign(callsign)
        except IndexError:
            pass

        if not aprs.valid_callsign(self.callsign):
            self.parse_text(callsign)

        if not aprs.valid_callsign(self.callsign):
            raise aprs.BadCallsignError(
                'Could not extract callsign from %s' %
                self.callsign.encode('hex'))

    def parse_text(self, callsign):
        """
        Parses and extracts a Callsign and SSID from an ASCII-Encoded APRS
        Callsign or Callsign-SSID.

        :param callsign: ASCII-Encoded APRS Callsign
        :type callsign: str
        """
        self._logger.debug('callsign=%s', callsign.encode('hex'))
        _callsign = callsign.lstrip().rstrip()
        ssid = str(0)

        if '*' in _callsign:
            _callsign = _callsign.strip('*')
            self.digi = True

        if '-' in _callsign:
            _callsign, ssid = _callsign.split('-')

        self.callsign = _callsign
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

    def _extract_kiss_callsign(self, frame):
        """
        Extracts a Callsign and SSID from a KISS-Encoded APRS Frame.

        :param frame: KISS-Encoded APRS Frame as str of octs.
        :type frame: str
        """
        self._logger.debug('frame=%s', frame.encode('hex'))
        callsign = ''.join([chr(ord(x) >> 1) for x in frame[:6]])
        self.callsign = callsign.lstrip().rstrip()
        self.ssid = str((ord(frame[6]) >> 1) & 0x0F)


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
