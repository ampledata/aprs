#!/usr/bin/env python

import logging
import aprs

import pprint

import threading
import Queue
import time

import argparse

import predict

ISS_TLE = """ISS (ZARYA)
1 25544U 98067A   16340.19707176  .00003392  00000-0  59140-4 0  9992
2 25544  51.6453 285.3071 0006023 292.9316 269.6257 15.53798216 31586
"""

QTH = (37.76, 122.4975, 56)


class GateOut(threading.Thread):

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprs.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprs.LOG_LEVEL)
        _console_handler.setFormatter(aprs.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, aprsc, queue):
        threading.Thread.__init__(self)
        self.aprsc = aprsc
        self.daemon = True
        self.queue = queue
        self._stop = threading.Event()

    def stop(self):
        """Stop the thread at the next opportunity."""
        self._stop.set()

    def stopped(self):
        """Checks if the thread is stopped."""
        return self._stop.isSet()

    def run(self):
        self._logger.info('Running %s', self)
        self.aprsc.start()

        while not self.stopped():
            aprs_frame = self.queue.get()
            self._logger.debug('Got from Queue aprs_frame="%s"', aprs_frame)
            self.aprsc.send(str(aprs_frame))
            self.queue.task_done()


class GateIn(threading.Thread):

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprs.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprs.LOG_LEVEL)
        _console_handler.setFormatter(aprs.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, aprsc, queue):
        threading.Thread.__init__(self)
        self.aprsc = aprsc
        self.daemon = True
        self.queue = queue
        self._stop = threading.Event()

    def stop(self):
        """Stop the thread at the next opportunity."""
        self._stop.set()

    def stopped(self):
        """Checks if the thread is stopped."""
        return self._stop.isSet()

    def handle_frame(self, frame):
        aprs_frame = aprs.APRSFrame(frame)
        aprs_frame.path.extend(['qAR', 'SUNSET-6'])
        self._logger.debug('Adding to Queue aprs_frame="%s"', aprs_frame)
        self.queue.put(aprs_frame)

    def run(self):
        self._logger.info('Running %s', self)
        self.aprsc.start()

        while not self.stopped():
            self.aprsc.read(callback=self.handle_frame)


class Beacon(threading.Thread):

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprs.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprs.LOG_LEVEL)
        _console_handler.setFormatter(aprs.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.daemon = True
        self.queue = queue
        self._stop = threading.Event()

    def stop(self):
        """Stop the thread at the next opportunity."""
        self._stop.set()

    def stopped(self):
        """Checks if the thread is stopped."""
        return self._stop.isSet()

    def send_beacon(self, frame):
        self.queue.put(frame)

    def run(self):
        self._logger.info('Running %s', self)
        while not self.stopped():
            self.queue.put(
                'SUNSET-6>BEACON:>W2GMD Experimental Python SGate')
            time.sleep(600)


class ISSCQ(threading.Thread):

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprs.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprs.LOG_LEVEL)
        _console_handler.setFormatter(aprs.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.daemon = True
        self.queue = queue
        self._stop = threading.Event()

    def stop(self):
        """Stop the thread at the next opportunity."""
        self._stop.set()

    def stopped(self):
        """Checks if the thread is stopped."""
        return self._stop.isSet()

    def send_beacon(self, frame):
        self.queue.put(frame)

    def run(self):
        self._logger.info('Running %s', self)
        p = predict.transits(ISS_TLE, QTH)

        while not self.stopped():
            passes = predict.transits(ISS_TLE, QTH)
            next_pass = passes.next()
            start = next_pass.start
            end = next_pass.start + next_pass.duration()
            now = time.time()
            if now >= start and now <= end:
                self.queue.put(
                    'SUNSET-6>CQ,ARISS:>W2GMD Hello from my experimental SGate.')
                time.sleep(60)


def setup_logging(log_level=None):
    """
    Sets up logging.

    :param log_level: Log level to setup.
    :type param: `logger` level.
    :returns: logger instance
    :rtype: instance
    """
    log_level = log_level or aprs.LOG_LEVEL

    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(aprs.LOG_FORMAT)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger


def gate():
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
        '-H', '--host', help='host', required=True
    )
    parser.add_argument(
        '-P', '--port', help='port', default=8001
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
        log_level = None

    logger = setup_logging(log_level)

    queue = Queue.Queue()

    aprs_listener = aprs.APRSTCPKISS(host=opts.host, port=opts.port)
    aprs_talker = aprs.TCPAPRS(opts.callsign, opts.passcode)

    gate_in = GateIn(aprs_listener, queue)
    gate_out = GateOut(aprs_talker, queue)
    beacon = Beacon(queue)
    iss_cq = ISSCQ(queue)

    try:
        gate_in.start()
        gate_out.start()
        beacon.start()
        iss_cq.start()

        queue.join()

        while gate_in.is_alive() and gate_out.is_alive() and beacon.is_alive() and iss_cq.is_alive():
            time.sleep(0.01)
    except KeyboardInterrupt:
        gate_in.stop()
        gate_out.stop()
        beacon.stop()
        iss_cq.stop()
    finally:
        gate_in.stop()
        gate_out.stop()
        beacon.stop()
        iss_cq.stop()


if __name__ == '__main__':
    gate()
