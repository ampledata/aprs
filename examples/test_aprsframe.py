#!/usr/bin/env python

import logging
import aprs
import kiss

import pprint

def test_frame1():
    frame_ascii = 'OROTAC-4>APAVT5,WIDE1-1,WIDE2-1:>AP510 3.90V  27.4C X AVRT5 20151117'
    frame_hex = '0082a082aca86a609ea49ea8828668ae92888a624062ae92888a64406303f03e415035313020332e383956202032372e34432058204156525435203230313531313137'
    frame_raw = frame_hex.decode('hex')

    frame_ascii_decoded = APRSFrame(frame_ascii)
    frame_raw_decoded = APRSFrame(frame_raw)

    pprint.pprint(locals())

    #print str(frame_raw_decoded) == str(frame_hex_decoded)


def test_frame2():
    frame__ok = '0086a24040404060a6aa9ca68aa86082a492a6a6406103f021333734352e36304e2f31323232392e383557605732474d442048656c6c6f2066726f6d2040616d706c656461746161'
    print frame__ok.decode('hex')
    frame__ok_decoded = aprs.APRSFrame(frame__ok.decode('hex'))
    print frame__ok_decoded

    frame_bad = '0086a24040404060a6aa9ca68aa86082a492a6a6406103f021333734352e36304e2f31323232392e383557605732474d442048656c6c6f2066726f6d2040616d706c6564617461'
    print frame_bad.decode('hex')
    frame_bad_decoded = aprs.APRSFrame(frame_bad.decode('hex'))
    print frame_bad_decoded

    frame_bad = '0086a24040404060a6aa9ca68aa86082a492a6a6406103f022'
    print frame_bad.decode('hex')
    frame_bad_decoded = aprs.APRSFrame(frame_bad.decode('hex'))
    print frame_bad_decoded


if __name__ == '__main__':
    #test_frame1()
    test_frame2()
