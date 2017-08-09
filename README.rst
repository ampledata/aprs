aprs - Python APRS Module
*************************

aprs is a Python Module that supports connecting to APRS Interfaces, and
receiving, parsing and sending APRS Frames.

Included are several Interface Classes:

* APRS - Abstract Class from which all other Connection Interfaces are inherited.
* TCP - Connection Interface Class for connecting to APRS-IS via TCP. Can send or receive APRS Frames.
* UDP - Connection Interface Class for connecting to APRS-IS via UDP. Only supports sending APRS Frames.
* HTTP - Connection Interface Class for connecting to APRS-IS via HTTP. Currently only supports sending APRS Frames.

Frame and Callsign classes are included:

* Frame - Describes the components of an APRS Frame.
* Callsign - Describes the components of an APRS Callsign.

Versions
========

- 6.5.x branch will be the last version of this Module that supports Python 2.7.x
- 7.x.x branch and-on will be Python 3.x ONLY.

Installation
============
Install from pypi using pip: ``pip install aprs``


Usage Examples
==============

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

    frame = aprs.parse_frame('W2GMD>APRS:>Hello World!')

    a = aprs.TCP('W2GMD', '12345')
    a.start()

    a.send(frame)

Testing
=======
Run nosetests from a Makefile target::

    make test

Errata
======

7.0.0rc1 - Currently setting/getting digi flag on KISS frames is broken. Expect it to
be fixed in final release of 7.0.0.


See Also
========

* `Python KISS Module <https://github.com/ampledata/kiss>`_ Library for interfacing-to and encoding-for various KISS Interfaces.
* `Python APRS Module <https://github.com/ampledata/aprs>`_ Library for sending, receiving and parsing APRS Frames to and from multiple Interfaces
* `Python APRS Gateway <https://github.com/ampledata/aprsgate>`_ Uses Redis PubSub to run a multi-interface APRS Gateway.
* `Python APRS Tracker <https://github.com/ampledata/aprstracker>`_ TK.
* `dirus <https://github.com/ampledata/dirus>`_ Dirus is a daemon for managing a SDR to Dire Wolf interface. Manifests that interface as a KISS TCP port.


Similar Projects
================

* `apex <https://github.com/Syncleus/apex>`_ by Jeffrey Phillips Freeman (WI2ARD). Next-Gen APRS Protocol. (based on this Module! :)
* `aprslib <https://github.com/rossengeorgiev/aprs-python>`_ by Rossen Georgiev. A Python APRS Library with build-in parsers for several Frame types.
* `aprx <http://thelifeofkenneth.com/aprx/>`_ by Matti & Kenneth. A C-based Digi/IGate Software for POSIX platforms.
* `dixprs <https://sites.google.com/site/dixprs/>`_ by HA5DI. A Python APRS project with KISS, digipeater, et al., support.
* `APRSDroid <http://aprsdroid.org/>`_ by GE0RG. A Java/Scala Android APRS App.
* `YAAC <http://www.ka2ddo.org/ka2ddo/YAAC.html>`_ by KA2DDO. A Java APRS Client.
* `Ham-APRS-FAP <http://search.cpan.org/dist/Ham-APRS-FAP/>`_ by aprs.fi: A Perl APRS Parser.
* `Dire Wolf <https://github.com/wb2osz/direwolf>`_ by WB2OSZ. A C-Based Soft-TNC for interfacing with sound cards. Can present as a KISS interface!


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
Greg Albrecht W2GMD oss@undef.net

http://ampledata.org/

Copyright
=========
Copyright 2017 Greg Albrecht and Contributors

`Automatic Packet Reporting System (APRS) <http://www.aprs.org/>`_ is Copyright Bob Bruninga WB4APR wb4apr@amsat.org

fcs.py - Copyright (c) 2013 Christopher H. Casebeer. All rights reserved.

decimaldegrees.py - Copyright (C) 2006-2013 by Mateusz Łoskot <mateusz@loskot.net>


License
=======
Apache License, Version 2.0. See LICENSE for details.

fcs.py - BSD 2-clause Simplified License

decimaldegrees.py - BSD 3-clause License
