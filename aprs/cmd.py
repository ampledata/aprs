#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""APRS commands."""

__author__ = 'Greg Albrecht W2GMD <gba@orionlabs.io>'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'
__license__ = 'All rights reserved. Do not redistribute.'


import argparse
import logging
import logging.handlers
import time

import aprs.classes
import aprs.constants
import aprs.geo_util
import aprs.util


def setup_logging(log_level=None):
    """
    Sets up logging.

    :param log_level: Log level to setup.
    :type param: `logger` level.
    :returns: logger instance
    :rtype: instance
    """
    log_level = log_level or aprs.constants.LOG_LEVEL

    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(aprs.constants.LOG_FORMAT)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger


def tracker():
    """Tracker Command Line interface for APRS."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--debug', help='Enable debug logging', action='store_true'
    )
    parser.add_argument(
        '-c', '--callsign', help='callsign', required=True
    )
    parser.add_argument(
        '-p', '--passcode', help='passcode', required=True
    )
    parser.add_argument(
        '-s', '--serial_port', help='serial_port', required=True
    )
    parser.add_argument(
        '-b', '--serial_speed', help='serial_speed', default=9600
    )
    parser.add_argument(
        '-i', '--interval', help='interval', default=0
    )
    parser.add_argument(
        '-u', '--ssid', help='ssid', default='1'
    )

    opts = parser.parse_args()

    if opts.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logger = setup_logging(log_level)

    gps_p = aprs.SerialGPSPoller(opts.serial_port, opts.serial_speed)
    gps_p.start()
    time.sleep(aprs.constants.GPS_WARM_UP)

    aprs_i = aprs.APRS(opts.callsign, opts.passcode)
    aprs_i.connect()

    src_callsign = aprs.util.full_callsign(
        {'callsign': opts.callsign, 'ssid': opts.ssid})

    try:
        while 1:
            aprs_latitude = None
            aprs_longitude = None
            gps_latitude = gps_p.gps_props['latitude']
            gps_longitude = gps_p.gps_props['longitude']

            if gps_latitude is not None:
                aprs_latitude = aprs.geo_util.dec2dm_lat(gps_latitude)
            if gps_longitude is not None:
                aprs_longitude = aprs.geo_util.dec2dm_lng(gps_longitude)

            if aprs_latitude is not None and aprs_longitude is not None:
                frame = aprs.util.create_location_frame(
                    source=src_callsign,
                    destination='APRS',
                    latitude=aprs_latitude,
                    longitude=aprs_longitude,
                    course=0,
                    speed=0,
                    altitude=gps_p.gps_props.get('altitude', 0),
                    symboltable='/',
                    symbolcode='>',
                )

                logger.debug('frame=%s', frame)
                aprs_i.send(frame)

                if opts.interval == 0:
                    break
                else:
                    time.sleep(opts.interval)

    except KeyboardInterrupt:
        gps_p.stop()
    finally:
        gps_p.stop()
