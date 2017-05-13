#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS KISS Module Class Definitions."""

import kiss

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2017 Greg Albrecht and Contributors'
__license__ = 'Apache License, Version 2.0'


class SerialKISS(kiss.SerialKISS):  # pylint: disable=R0903

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


class TCPKISS(kiss.TCPKISS):  # pylint: disable=R0903

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
