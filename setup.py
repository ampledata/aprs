#!/usr/bin/env python

__author__ = 'Greg Albrecht <gba@gregalbrecht.com>'
__copyright__ = 'Copyright 2013 Greg Albrecht'
__license__ = 'Creative Commons Attribution 3.0 Unported License'


import setuptools


setuptools.setup(
    version='1.0.0',
    name='aprs',
    description='Python Bindings for aprs-is API.',
    author='Greg Albrecht',
    author_email='gba@gregalbrecht.com',
    license='Creative Commons Attribution 3.0 Unported License',
    url='https://github.com/ampledata/aprs',
    setup_requires=['nose'],
    tests_require=['nose', 'httpretty'],
    install_requires=['requests']

)
