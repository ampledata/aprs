#!/usr/bin/env python

import logging
import aprs

import pprint

def print_frame(frame):
    fa = 'OROTAC-4>APAVT5,WIDE1-1,WIDE2-1:>AP510 3.90V  27.4C X AVRT5 20151117'
    fh = '0082a082aca86a609ea49ea8828668ae92888a624062ae92888a64406303f03e415035313020332e383956202032372e34432058204156525435203230313531313137'
    fr = fh.decode('hex')

    fr_decoded = aprs.APRSFrame(fr)
    fh_decoded = aprs.APRSFrame(fh)
    fa_decoded = aprs.APRSFrame(fa)

    frame_decoded = aprs.APRSFrame(frame)

    pprint.pprint(locals())

    print str(fr_decoded) == str(fh_decoded)


a = aprs.APRSTCPKISS(host='belfast.local', port=8001)
a.start()
a.read(callback=print_frame)
