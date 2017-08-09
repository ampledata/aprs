#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""FCS Definitions."""

import bitarray

import struct

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'  # NOQA pylint: disable=R0801
__copyright__ = 'Copyright 2017 Greg Albrecht and Contributors'  # NOQA pylint: disable=R0801
__license__ = 'Apache License, Version 2.0'  # NOQA pylint: disable=R0801


class FCS(object):

    def __init__(self) -> None:
        self.fcs = 0xFFFF

    def update_bit(self, bit) -> None:
        check = (self.fcs & 0x1 == 1)
        self.fcs >>= 1
        if check != bit:
            self.fcs ^= 0x8408

    def update(self, bytes) -> None:
        for byte in (ord(b) for b in bytes):
            for i in range(7,-1,-1):
                self.update_bit((byte >> i) & 0x01 == 1)

    def digest(self):
#        print ~self.fcs
#        print "%r" % struct.pack("<H", ~self.fcs % 2**16)
#        print "%r" % "".join([chr((~self.fcs & 0xff) % 256), chr((~self.fcs >> 8) % 256)])
        # digest is two bytes, little endian
        return struct.pack("<H", ~self.fcs % 2**16)


def fcs(bits):
    """
    Append running bitwise FCS CRC checksum to end of generator
    """
    fcs = FCS()
    for bit in bits:
        yield bit
        fcs.update_bit(bit)

#    test = bitarray()
#    for byte in (digest & 0xff, digest >> 8):
#        print byte
#        for i in range(8):
#            b = (byte >> i) & 1 == 1
#            test.append(b)
#            yield b

    # append fcs digest to bit stream

    # n.b. wire format is little-bit-endianness in addition to little-endian
    digest = bitarray(endian="little")
    digest.frombytes(fcs.digest())
    for bit in digest:
        yield bit


def fcs_validate(bits):
    buffer = bitarray()
    fcs = FCS()

    for bit in bits:
        buffer.append(bit)
        if len(buffer) > 16:
            bit = buffer.pop(0)
            fcs.update(bit)
            yield bit

    if buffer.tobytes() != fcs.digest():
        raise Exception("FCS checksum invalid.")
