Python Module for APRS-IS.

.. image:: https://travis-ci.org/ampledata/aprs.png?branch=develop
        :target: https://travis-ci.org/ampledata/aprs


Example Usage
=============

Example 1:

The following example connects to APRS-IS as W2GMD (me!) and filters for APRS
frames coming from my prefix (W2GMD, W2GMD-n, etc). Any frames returned are
sent to my callback *my_cb* and printed.

    #!/usr/bin/env python

    import aprs

    def my_callback(line):
        print line

    a = aprs.APRS('W2GMD', '12345')

    a.connect()

    a.send('W2GMD>APRS:>Test!')

    a.receive(callback=my_callback)


Example 1 output:

    W2GMD-6>APRX28,TCPIP*,qAC,APRSFI-I1:T#471,7.5,34.7,37.0,1.0,137.0,00000000

Example 2:

The following example uses the `aprs_tracker` command to connect to APRS-IS
as W2GMD and send a single-shot location frame using location data from my
locally connected USB (or USB->Serial) GPS:

    $ aprs_tracker -c W2GMD -p 12345 -s /dev/cu.usbmodem1a1211 -u 3 -d

Example 2 output:

    2015-09-25 15:04:55,930 INFO aprs.classes.connect:63 - Connected to server=rotate.aprs.net port=14580
    2015-09-25 15:04:55,931 DEBUG aprs.cmd.tracker:113 - frame=W2GMD-3>APRS:!3745.78N/12225.14W>000/000/A=000175 APRS Python Module

See `$ aprs_tracker -h` for more information.

Source
======
Github: https://github.com/ampledata/aprs

Author
======
Greg Albrecht W2GMD <gba@orionlabs.co>

Copyright
=========
Copyright 2015 Orion Labs, Inc.

License
=======
Apache License, Version 2.0
