aprs - Python APRS Module
*************************

aprs is a Python Module that supports connecting to APRS Interfaces, and
receiving, parsing and sending APRS Frames.

Included are several Interface Classes:

* APRS - Abstract Class from which all other Interfaces are inherited.
* TCPAPRS - Interfaces Class for connecting to APRS-IS via TCP. Can send or receive APRS Frames.
* UDPAPRS - Interfaces Class for connecting to APRS-IS via UDP. Only supports sending APRS Frames.
* HTTPAPRS - Interfaces Class for connecting to APRS-IS via HTTP. Currently only supports sending APRS Frames.

Additional Interface Classes for connecting to KISS Interfaces are included:

* SerialKISS - Interface Class for connecting to KISS Serial devices. Can send or receive APRS Frames.
* TCPKISS - Interface Class for connecting to KISS TCP Hosts. Can send or receive APRS Frames.

Finally, Frame and Callsign classes are included:

* Frame - Describes the components of an APRS Frame.
* Callsign - Describes the components of an APRS Callsign.


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

    a = aprs.TCPAPRS('W2GMD', '12345')
    a.start()
    def p(x): print(x)
    a.receive(callback=p)

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

    a = aprs.TCPAPRS('W2GMD', '12345')
    a.start()
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
Greg Albrecht W2GMD <oss@undef.net>

Copyright
=========
Copyright 2016 Orion Labs, Inc.

License
=======
Apache License, Version 2.0
