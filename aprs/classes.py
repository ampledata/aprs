#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""APRS Class Definitions"""

__author__ = 'Greg Albrecht W2GMD <gba@orionlabs.co>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2015 Orion Labs, Inc.'


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


class APRS(object):

    """APRS Object."""

    logger = logging.getLogger(__name__)
    logger.setLevel(aprs.constants.LOG_LEVEL)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(aprs.constants.LOG_LEVEL)
    console_handler.setFormatter(aprs.constants.LOG_FORMAT)
    logger.addHandler(console_handler)
    logger.propagate = False

    def __init__(self, user, password='-1', input_url=None):
        self.user = user
        self._url = input_url or aprs.constants.APRSIS_URL
        self._auth = ' '.join(
            ['user', user, 'pass', password, 'vers', 'APRS Python Module'])
        self.aprsis_sock = None

    def connect(self, server=None, port=None, aprs_filter=None):
        """
        Connects & logs in to APRS-IS.

        :param server: Optional alternative APRS-IS server.
        :param port: Optional APRS-IS port.
        :param filter: Optional filter to use.
        :type server: str
        :type port: int
        :type filte: str
        """
        server = server or aprs.constants.APRSIS_SERVER
        port = port or aprs.constants.APRSIS_FILTER_PORT
        aprs_filter = aprs_filter or '/'.join(['p', self.user])

        full_auth = ' '.join([self._auth, 'filter', aprs_filter])

        self.aprsis_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.aprsis_sock.connect((server, int(port)))
        self.logger.info('Connected to server=%s port=%s', server, port)
        self.logger.debug('Sending full_auth=%s', full_auth)
        self.aprsis_sock.sendall(full_auth + '\n\r')

    def send(self, message, headers=None, protocol='TCP'):
        """
        Sends message to APRS-IS.

        :param message: Message to send to APRS-IS.
        :param headers: Optional HTTP headers to post.
        :param protocol: Protocol to use: One of TCP, HTTP or UDP.
        :type message: str
        :type headers: dict

        :return: True on success, False otherwise.
        :rtype: bool
        """
        self.logger.debug(
            'message=%s headers=%s protocol=%s', message, headers, protocol)

        if 'TCP' in protocol:
            self.logger.debug('sending message=%s', message)
            self.aprsis_sock.sendall(message + '\n\r')
            return True
        elif 'HTTP' in protocol:
            content = "\n".join([self._auth, message])
            headers = headers or aprs.constants.APRSIS_HTTP_HEADERS
            result = requests.post(self._url, data=content, headers=headers)
            return 204 in result.status_code
        elif 'UDP' in protocol:
            content = "\n".join([self._auth, message])
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(
                content,
                (aprs.constants.APRSIS_SERVER, aprs.constants.APRSIS_RX_PORT)
            )
            return True

    def receive(self, callback=None):
        """
        Receives from APRS-IS.

        :param callback: Optional callback to deliver data to.
        :type callback: func
        """
        recvd_data = ''

        try:
            while 1:
                recv_data = self.aprsis_sock.recv(aprs.constants.RECV_BUFFER)

                if not recv_data:
                    break

                recvd_data += recv_data

                self.logger.debug('recv_data=%s', recv_data.strip())

                if recvd_data.endswith('\r\n'):
                    lines = recvd_data.strip().split('\r\n')
                    recvd_data = ''
                else:
                    lines = recvd_data.split('\r\n')
                    recvd_data = str(lines.pop(-1))

                for line in lines:
                    if line.startswith('#'):
                        if 'logresp' in line:
                            self.logger.debug('logresp=%s', line)
                    else:
                        self.logger.debug('line=%s', line)
                        if callback:
                            callback(line)

        except socket.error as sock_err:
            self.logger.error(sock_err)
            raise


class APRSKISS(kiss.KISS):

    """APRS interface for KISS serial devices."""

    def write(self, frame):
        """Writes APRS-encoded frame to KISS device.

        :param frame: APRS frame to write to KISS device.
        :type frame: str
        """
        encoded_frame = aprs.util.encode_frame(frame)
        super(APRSKISS, self).write(encoded_frame)


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
