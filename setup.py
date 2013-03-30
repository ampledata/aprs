#!/usr/bin/env python

__author__ = 'Greg Albrecht W2GMD <gba@gregalbrecht.com>'
__copyright__ = 'Copyright 2013 Greg Albrecht'
__license__ = 'Creative Commons Attribution 3.0 Unported License'


import setuptools


setuptools.setup(
    version='1.0.0',
    name='aprs',
    description='Python Bindings for APRS-IS API.',
    author='Greg Albrecht',
    author_email='gba@gregalbrecht.com',
    license='Creative Commons Attribution 3.0 Unported License',
    url='https://github.com/ampledata/aprs',
    setup_requires=['nose'],
    tests_require=['coverage', 'httpretty', 'nose'],
    install_requires=['requests']

)
