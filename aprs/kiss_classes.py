#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS KISS Module Class Definitions."""

import logging

import kiss  # pylint: disable=R0801

import aprs  # pylint: disable=R0801

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'  # NOQA pylint: disable=R0801
__copyright__ = 'Copyright 2017 Greg Albrecht and Contributors'  # NOQA pylint: disable=R0801
__license__ = 'Apache License, Version 2.0'  # NOQA pylint: disable=R0801


class Frame(object):

    """
    Frame Class.

    Defines the components of an APRS Frame and can decode a frame
    from either ASCII or KISS.
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
        self.destination = 'APRS'
        self.path = []
        self.text = ''
        if frame is not None:
            self.frame = kiss.strip_df_start(str(frame))
            self.parse()

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
        Parses an Frame from either ASCII or KISS Encoded frame.
        """
        # Allows to be called as class method:
        if frame is not None:
            self.frame = frame

        try:
            self.parse_kiss()
        except IndexError as exc:
            self._logger.info('Not a KISS Frame? %s', self.frame.encode('hex'))

        if not self.source or not self.destination:
            try:
                self.parse_text()
            except UnicodeDecodeError as exc:
                self._logger.info(
                    'Cannot decode frame=%s', self.frame.encode('hex'))
                self._logger.exception(exc)

    def parse_text(self):
        """
        Parses and Extracts the components of an ASCII-Encoded Frame.
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

    def parse_kiss(self):
        """
        Parses and Extracts the components of an KISS-Encoded Frame.
        """
        frame_len = len(self.frame)

        if frame_len < 16:
            self._logger.debug('Frame len(%s) < 16, Exiting.', frame_len)
            return

        for raw_slice in range(0, frame_len):

            # Is address field length correct?
            # Find the first ODD Byte followed by the next boundary:
            if (ord(self.frame[raw_slice]) & 0x01
                    and ((raw_slice + 1) % 7) == 0):

                i = (raw_slice + 1) / 7

                # Less than 2 callsigns?
                if 1 < i < 11:
                    # For frames <= 70 bytes
                    if frame_len >= raw_slice + 2:
                        if (ord(self.frame[raw_slice + 1]) & 0x03 == 0x03 and
                                ord(self.frame[raw_slice + 2]) in
                                [0xf0, 0xcf]):
                            self._extract_kiss_text(raw_slice)
                            self._extract_kiss_destination()
                            self._extract_kiss_source()
                            self._extract_kiss_path(i)

    def encode_kiss(self):
        """
        Encodes an Frame as KISS.
        """
        enc_frame = ''.join([
            self.destination.encode_kiss(),
            self.source.encode_kiss(),
            ''.join([path_call.encode_kiss() for path_call in self.path])
        ])
        return ''.join([
            enc_frame[:-1],
            chr(ord(enc_frame[-1]) | 0x01),
            kiss.SLOT_TIME,
            chr(0xF0),
            self.text
        ])

    def _extract_kiss_text(self, raw_slice):
        """
        Extracts a Text portion of a KISS-Encoded Frame.
        """
        self.text = self.frame[raw_slice + 3:]

    def _extract_kiss_source(self):
        """
        Extracts a Source Callsign of a KISS-Encoded Frame.
        """
        self.source = aprs.Callsign(self.frame[7:])

    def _extract_kiss_destination(self):
        """
        Extracts a Destination Callsign of a KISS-Encoded Frame.
        """
        self.destination = aprs.Callsign(self.frame)

    def _extract_kiss_path(self, start):
        """
        Extracts path from raw APRS KISS frame.
        """
        for i in range(2, start):
            path_call = aprs.Callsign(self.frame[i * 7:])

            if path_call:
                if ord(self.frame[i * 7 + 6]) & 0x80:
                    path_call.digi = True

                self.path.append(path_call)


class SerialKISS(kiss.SerialKISS):

    """APRS interface for KISS serial devices."""

    def __init__(self, port, speed, strip_df_start=False):
        super(SerialKISS, self).__init__(port, speed, strip_df_start)
        self.send = self.write
        self.receive = self.read
        self.use_i_construct = False

    def write(self, frame):
        """Writes APRS-encoded frame to KISS device.

        :param frame: APRS frame to write to KISS device.
        :type frame: str
        """
        super(SerialKISS, self).write(frame.encode_kiss())


class TCPKISS(kiss.TCPKISS):

    """APRS interface for KISS serial devices."""

    def __init__(self, host, port, strip_df_start=False):
        super(TCPKISS, self).__init__(host, port, strip_df_start)
        self.send = self.write
        self.receive = self.read
        self.use_i_construct = False

    def write(self, frame):
        """
        Writes APRS-encoded frame to KISS device.

        :param frame: APRS frame to write to KISS device.
        :type frame: str
        """
        super(TCPKISS, self).write(frame.encode_kiss())
