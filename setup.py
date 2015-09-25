#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup for the APRS Python Module.

Source:: https://github.com/ampledata/aprs
"""


__title__ = 'aprs'
__version__ = '4.0.0'
__author__ = 'Greg Albrecht W2GMD <gba@orionlabs.co>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2015 Orion Labs, Inc.'


import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup  # pylint: disable=F0401,E0611


def publish():
    """Function for publishing package to pypi."""
    if sys.argv[-1] == 'publish':
        os.system('python setup.py sdist upload')
        sys.exit()


publish()


setup(
    name='aprs',
    version=__version__,
    description='Python Bindings for APRS.',
    author='Greg Albrecht',
    author_email='gba@orionlabs.co',
    packages=['aprs'],
    package_data={'': ['LICENSE']},
    license=open('LICENSE').read(),
    long_description=open('README.rst').read(),
    url='https://github.com/ampledata/aprs',
    setup_requires=[
      'coverage >= 3.7.1',
      'httpretty >= 0.8.10',
      'nose >= 1.3.7'
    ],
    install_requires=[
        'kiss >= 2.0.2',
        'pynmea2 >= 1.4.2',
        'pyserial >= 2.7',
        'requests >= 2.7.0'
    ],
    package_dir={'aprs': 'aprs'},
    zip_safe=False,
    include_package_data=True,
    entry_points={'console_scripts': ['aprs_tracker = aprs.cmd:tracker']}
)
