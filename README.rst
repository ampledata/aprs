aprs - Python APRS Module
*************************

aprs is a Python Module that supports connecting to APRS Interfaces, and
receiving, parsing and sending APRS Frames.

Included are several Interface Classes:

* APRS - Abstract Class from which all other Interfaces are inherited.
* TCP - Interfaces Class for connecting to APRS-IS via TCP. Can send or receive APRS Frames.
* UDP - Interfaces Class for connecting to APRS-IS via UDP. Only supports sending APRS Frames.
* HTTP - Interfaces Class for connecting to APRS-IS via HTTP. Currently only supports sending APRS Frames.

Additional Interface Classes for connecting to KISS Interfaces are included:

* SerialKISS - Interface Class for connecting to KISS Serial devices. Can send or receive APRS Frames.
* TCPKISS - Interface Class for connecting to KISS TCP Hosts. Can send or receive APRS Frames.

Finally, Frame and Callsign classes are included:

* Frame - Describes the components of an APRS Frame.
* Callsign - Describes the components of an APRS Callsign.


Examples
========

Example 1: Library Usage - Receive
----------------------------------

The following example connects to APRS-IS as W2GMD (me!) and filters for APRS
frames coming from my prefix (W2GMD, W2GMD-n, etc). Any frames returned are
sent to my callback *p* and printed.

Example 1 Code
^^^^^^^^^^^^^^
::

    import aprs

    def p(x): print(x)

    a = aprs.TCP('W2GMD', '12345')
    a.start()

    a.receive(callback=p)

Example 1 Output
^^^^^^^^^^^^^^^^
::

    W2GMD-6>APRX28,TCPIP*,qAC,APRSFI-I1:T#471,7.5,34.7,37.0,1.0,137.0,00000000

Example 2: Library Usage - Send
----------------------------------

The following example connects to APRS-IS as W2GMD (me!) and sends an APRS
frame.

Example 2 Code
^^^^^^^^^^^^^^
::

    import aprs

    frame = aprs.Frame('W2GMD>APRS:>Hello World!')

    a = aprs.TCP('W2GMD', '12345')
    a.start()

    a.send(frame)


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
