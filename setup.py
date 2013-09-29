#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup for the APRS Python Module.

Source:: https://github.com/ampledata/aprs
"""

__author__ = 'Greg Albrecht W2GMD <gba@onbeep.com>'
__copyright__ = 'Copyright 2013 OnBeep, Inc.'
__license__ = 'Apache License, Version 2.0'


import os
import sys

import aprs

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup  # pylint: disable=F0401,E0611


packages = ['aprs']
requires = ['requests', 'kiss']


def publish():
    """Function for publishing package to pypi."""
    if sys.argv[-1] == 'publish':
        os.system('python setup.py sdist upload')
        sys.exit()


publish()


setup(
    name='aprs',
    version=aprs.__version__,
    description='Python Bindings for APRS-IS API.',
    author='Greg Albrecht',
    author_email='gba@onbeep.com',
    packages=packages,
    package_data={'': ['LICENSE']},
    license=open('LICENSE').read(),
    long_description=open('README.rst').read(),
    url='https://github.com/ampledata/aprs',
    setup_requires=['nose'],
    tests_require=['coverage', 'httpretty', 'nose'],
    install_requires=requires,
    package_dir={'aprs': 'aprs'},
    zip_safe=False,
    include_package_data=True
)
