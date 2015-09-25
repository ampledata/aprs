#!/usr/bin/env python
# -*- coding: utf-8 -*-

# APRS Python Module.

"""
APRS Python Module.
~~~~


:author: Greg Albrecht W2GMD <gba@orionlabs.co>
:copyright: Copyright 2015 Orion Labs, Inc.
:license: Apache License, Version 2.0
:source: <https://github.com/ampledata/aprs>

"""

import logging

from .classes import APRS, APRSKISS, SerialGPSPoller


# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        """Default logging handler to avoid "No handler found" warnings."""
        def emit(self, record):
            """Default logging handler to avoid "No handler found" warnings."""
            pass

logging.getLogger(__name__).addHandler(NullHandler())
