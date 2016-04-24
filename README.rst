Python Module for APRS-IS
*************************

Includes Python module with bindings for APRS as well as ``aprs_tracker``
command-line APRS location tracking utility.


Examples
========

Example 1: APRS Tracker
-----------------------

The following example uses the ``aprs_tracker`` command to connect to APRS-IS
as W2GMD and send a single-shot location frame using location data from my
locally connected USB (or USB->Serial) GPS:

Example 1 Code
^^^^^^^^^^^^^^
::

    $ aprs_tracker -c W2GMD -p 12345 -s /dev/cu.usbmodem1a1211 -u 3 -d

Example 1 Output
^^^^^^^^^^^^^^^^
::

    2015-09-25 15:04:55,930 INFO aprs.classes.connect:63 - Connected to server=rotate.aprs.net port=14580
    2015-09-25 15:04:55,931 DEBUG aprs.cmd.tracker:113 - frame=W2GMD-3>APRS:!3745.78N/12225.14W>000/000/A=000175 APRS


See Also
^^^^^^^^
See ``$ aprs_tracker -h`` for more information.


Example 2: Library Usage - Receive
----------------------------------

The following example connects to APRS-IS as W2GMD (me!) and filters for APRS
frames coming from my prefix (W2GMD, W2GMD-n, etc). Any frames returned are
sent to my callback *my_callback* and printed.

Example 2 Code
^^^^^^^^^^^^^^
::

    import aprs

    def my_callback(line):
        print line

    a = aprs.APRS('W2GMD', '12345')
    a.connect()
    a.receive(callback=my_callback)

Example 2 Output
^^^^^^^^^^^^^^^^
::

    W2GMD-6>APRX28,TCPIP*,qAC,APRSFI-I1:T#471,7.5,34.7,37.0,1.0,137.0,00000000

Example 3: Library Usage - Send
----------------------------------

The following example connects to APRS-IS as W2GMD (me!) and sends an APRS
frame.

Example 3 Code
^^^^^^^^^^^^^^
::

    import aprs

    a = aprs.APRS('W2GMD', '12345')
    a.connect()
    a.send('W2GMD>APRS:>Hello World!')


Build Status
============

Master:

.. image:: https://travis-ci.org/ampledata/aprs.svg?branch=master
    :target: https://travis-ci.org/ampledata/aprs

Develop:

.. image:: https://travis-ci.org/ampledata/aprs.svg?branch=develop
    :target: https://travis-ci.org/ampledata/aprs


Source
======
Github: https://github.com/ampledata/aprs

Author
======
Greg Albrecht W2GMD <gba@orionlabs.io>

Copyright
=========
Copyright 2016 Orion Labs, Inc.

License
=======
Apache License, Version 2.0
