#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""APRS Class Definitions"""

import logging
import logging.handlers
import socket
import threading

import kiss
import pynmea2
import requests
import serial

import aprs.constants
import aprs.util

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'


class APRS(object):

    """APRS Object."""

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprs.constants.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprs.constants.LOG_LEVEL)
        _console_handler.setFormatter(aprs.constants.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, user, password='-1'):
        self.user = user
        self._auth = ' '.join(
            ['user', user, 'pass', password, 'vers', 'APRS Python Module'])
        self._full_auth = None
        self.interface = None

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


class APRSFrame(object):

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprs.constants.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprs.constants.LOG_LEVEL)
        _console_handler.setFormatter(aprs.constants.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, frame):
        self.source = None
        self.destination = None
        self.path = []
        self.text = None
        self.parse(frame)

    def parse(self, frame):
        """
        Parse APRS Frame.
        """
        frame_so_far = ''

        for char in frame.decode('ISO-8859-1'):
            if '>' in char and not self.source:
                self.source = frame_so_far
                frame_so_far = ''
            elif ':' in char and not self.path:
                if ',' in frame_so_far:
                    self.path = frame_so_far.split(',')[1:]
                    self.destination = frame_so_far.split(',')[0]
                else:
                    self.destination = frame_so_far
                frame_so_far = ''
            else:
                frame_so_far = ''.join([frame_so_far, char])

        self.text = frame_so_far

    def __repr__(self):
        frame = "%s>%s:%s" % (
            self.source,
            ','.join([self.destination] + self.path),
            self.text
        )
        return frame.encode('ISO-8859-1')


class APRSSerialKISS(kiss.SerialKISS):

    """APRS interface for KISS serial devices."""

    def write(self, frame):
        """Writes APRS-encoded frame to KISS device.

        :param frame: APRS frame to write to KISS device.
        :type frame: str
        """
        encoded_frame = aprs.encode_frame(frame)
        super(APRSSerialKISS, self).write(encoded_frame)


class APRSTCPKISS(kiss.TCPKISS):

    """APRS interface for KISS serial devices."""

    def write(self, frame):
        """Writes APRS-encoded frame to KISS device.

        :param frame: APRS frame to write to KISS device.
        :type frame: str
        """
        encoded_frame = aprs.encode_frame(frame)
        super(APRSTCPKISS, self).write(encoded_frame)


class TCPAPRS(APRS):

    """APRS-IS TCP Class."""

    def __init__(self, user, password='-1', server=None, port=None,
                 aprs_filter=None):
        super(TCPAPRS, self).__init__(user, password)
        server = server or aprs.constants.APRSIS_SERVER
        port = port or aprs.constants.APRSIS_FILTER_PORT
        self._addr = (server, int(port))
        aprs_filter = aprs_filter or '/'.join(['p', user])
        self._full_auth = ' '.join([self._auth, 'filter', aprs_filter])

    def start(self):
        """
        Connects & logs in to APRS-IS.
        """
        self.interface = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._logger.info('Connecting to to "%s"', self._addr)
        self.interface.connect(self._addr)

        self._logger.debug('Sending full_auth=%s', self._full_auth)
        self.interface.sendall(self._full_auth + '\n\r')

    def send(self, message):
        """
        Sends message to APRS-IS.

        :param message: Message to send to APRS-IS.
        :type message: str
        """
        self._logger.debug('message="%s"', message)
        return self.interface.sendall(message + '\n\r')

    def receive(self, callback=None):
        """
        Receives from APRS-IS.

        :param callback: Optional callback to deliver data to.
        :type callback: func
        """
        recvd_data = ''

        try:
            while 1:
                recv_data = self.interface.recv(aprs.constants.RECV_BUFFER)

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
                            callback(line)

        except socket.error as sock_err:
            self._logger.error(sock_err)
            raise


class UDPAPRS(APRS):

    """APRS-IS UDP Class."""

    def __init__(self, user, password='-1', server=None, port=None):
        super(UDPAPRS, self).__init__(user, password)
        server = server or aprs.constants.APRSIS_SERVER
        port = port or aprs.constants.APRSIS_RX_PORT
        self._addr = (server, int(port))

    def start(self):
        """
        Connects & logs in to APRS-IS.
        """
        self.interface = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, message):
        """
        Sends message to APRS-IS.

        :param message: Message to send to APRS-IS.
        :type message: str
        """
        self._logger.debug('message="%s"', message)
        content = "\n".join([self._auth, message])
        return self.interface.sendto(content, self._addr)


class HTTPAPRS(APRS):

    """APRS-IS HTTP Class."""

    def __init__(self, user, password='-1', url=None, headers=None):
        super(HTTPAPRS, self).__init__(user, password)
        self.url = url or aprs.constants.APRSIS_URL
        self.headers = headers or aprs.constants.APRSIS_HTTP_HEADERS

    def start(self):
        """
        Connects & logs in to APRS-IS.
        """
        self.interface = requests.post

    def send(self, message):
        """
        Sends message to APRS-IS.

        :param message: Message to send to APRS-IS.
        :type message: str
        """
        content = "\n".join([self._auth, message])
        result = self.interface(self.url, data=content, headers=self.headers)
        return result.status_code == 204


class SerialGPSPoller(threading.Thread):

    """Threadable Object for polling a serial NMEA-compatible GPS."""

    NMEA_PROPERTIES = [
        'timestamp',
        'lat',
        'latitude',
        'lat_dir',
        'lon',
        'longitude',
        'lon_dir',
        'gps_qual',
        'mode_indicator',
        'num_sats',
        'hdop',
        'altitude',
        'horizontal_dil',
        'altitude_units',
        'geo_sep',
        'geo_sep_units',
        'age_gps_data',
        'ref_station_id',
        'pos_fix_dim',
        'mode_fix_type',
        'mode',
        'pdop',
        'vdop',
        'fix'
    ]

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprs.constants.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprs.constants.LOG_LEVEL)
        _console_handler.setFormatter(aprs.constants.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, serial_port, serial_speed):
        threading.Thread.__init__(self)
        self._serial_port = serial_port
        self._serial_speed = serial_speed
        self._stopped = False

        self.gps_props = {}
        for prop in self.NMEA_PROPERTIES:
            self.gps_props[prop] = None

        self._serial_int = serial.Serial(
            self._serial_port, self._serial_speed, timeout=1)

    def stop(self):
        """
        Stop the thread at the next opportunity.
        """
        self._stopped = True
        return self._stopped

    def run(self):
        streamreader = pynmea2.NMEAStreamReader(self._serial_int)
        try:
            while not self._stopped:
                for msg in streamreader.next():
                    for prop in self.NMEA_PROPERTIES:
                        if getattr(msg, prop, None) is not None:
                            self.gps_props[prop] = getattr(msg, prop)
                            self._logger.debug(
                                '%s=%s', prop, self.gps_props[prop])
        except StopIteration:
            pass
