#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python APRS Module.

"""
Python APRS Module.
~~~~


:author: Greg Albrecht W2GMD <oss@undef.net>
:copyright: Copyright 2017 Greg Albrecht and Contributors
:license: Apache License, Version 2.0
:source: <https://github.com/ampledata/aprs>

"""

from .constants import (LOG_FORMAT, LOG_LEVEL, APRSIS_SW_VERSION,  # NOQA
                        APRSIS_HTTP_HEADERS, APRSIS_SERVER, APRSIS_FILTER_PORT,
                        APRSIS_RX_PORT, RECV_BUFFER, APRSIS_URL,
                        UI_PROTOCOL_ID, CONTROL_FIELD, FLAG)

from .exceptions import BadCallsignError  # NOQA

from .util import valid_callsign  # NOQA

from .geo_util import dec2dm_lat, dec2dm_lng  # NOQA

from .classes import APRS, Callsign, Frame, TCP, UDP, HTTP  # NOQA

from .kiss_classes import TCPKISS, SerialKISS  # NOQA

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2017 Greg Albrecht and Contributors'
__license__ = 'Apache License, Version 2.0'
