#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Frame Check Sequence

The FCS is a sequence of 16 bits used for checking the integrity of a
received frame.

Derived from https://github.com/casebeer/afsk

Copyright (c) 2013 Christopher H. Casebeer. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import struct

import bitarray

__author__ = 'Christopher H. Casebeer'  # NOQA pylint: disable=R0801
__copyright__ = 'Copyright (c) 2013 Christopher H. Casebeer. All rights reserved.'  # NOQA pylint: disable=R0801
__license__ = 'BSD 2-clause Simplified License'  # NOQA pylint: disable=R0801


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
