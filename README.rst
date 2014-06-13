Python Module for APRS-IS.

.. image:: https://travis-ci.org/ampledata/aprs.png?branch=develop
        :target: https://travis-ci.org/ampledata/aprs


Example Usage
=============

The following example connects to APRS-IS as W2GMD (me!) and filters for APRS
frames coming from my prefix (W2GMD, W2GMD-n, etc). Any frames returned are
sent to my callback *my_cb* and printed.

    #!/usr/bin/env python

    import aprs

    a = aprs.APRS('W2GMD')

    def my_cb(line):
        print line

    a.receive(callback=my_cb)


Example output:

    W2GMD-6>APRX28,TCPIP*,qAC,APRSFI-I1:T#471,7.5,34.7,37.0,1.0,137.0,00000000

Source
======
Github: https://github.com/ampledata/aprs

Author
======
Greg Albrecht W2GMD <gba@gregalbrecht.com>

Copyright
=========
Copyright 2013 Greg Albrecht

License
=======
Creative Commons Attribution 3.0 Unported License
