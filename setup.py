#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup for the Python APRS Module.

:author: Greg Albrecht W2GMD <oss@undef.net>
:copyright: Copyright 2017 Greg Albrecht and Contributors
:license: Apache License, Version 2.0
:source: <https://github.com/ampledata/aprs>
"""

import os
import sys

import setuptools

__title__ = 'aprs'
__version__ = '7.0.0'
__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'  # NOQA pylint: disable=R0801
__copyright__ = 'Copyright 2017 Greg Albrecht and Contributors'  # NOQA pylint: disable=R0801
__license__ = 'Apache License, Version 2.0'  # NOQA pylint: disable=R0801


def publish():
    """Function for publishing package to pypi."""
    if sys.argv[-1] == 'publish':
        os.system('python setup.py sdist')
        os.system('twine upload dist/*')
        sys.exit()


publish()


setuptools.setup(
    name=__title__,
    version=__version__,
    description='Python APRS Module.',
    author='Greg Albrecht',
    author_email='oss@undef.net',
    packages=['aprs'],
    package_data={'': ['LICENSE']},
    package_dir={'aprs': 'aprs'},
    license=open('LICENSE').read(),
    long_description=open('README.rst').read(),
    url='https://github.com/ampledata/aprs',
    zip_safe=False,
    include_package_data=True,
    tests_require=[
        'coverage >= 4.4.1',
        'nose >= 1.3.7',
        'httpretty >= 0.8.14'
    ],
    install_requires=[
        'kiss > 6.9',
        'requests >= 2.7.0',
        'bitarray >= 0.8.1'
    ],
    classifiers=[
        'Topic :: Communications :: Ham Radio',
        'Programming Language :: Python',
        'License :: OSI Approved :: Apache Software License'
    ],
    keywords=[
        'Ham Radio', 'APRS', 'KISS'
    ]
)
