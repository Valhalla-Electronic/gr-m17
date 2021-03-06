#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 J. Elms
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#


import numpy
from gnuradio import gr
from m17.m17_lich import lich

class m17_framer(gr.basic_block):
    """
    framing for M17 specification
    """
    def __init__(self, dst, src, stream_type, nonce=None):
        gr.basic_block.__init__(self,
            name="m17_framer",
            in_sig=[numpy.byte],
            out_sig=[numpy.byte])
        self.set_relative_rate(176, 64)
        self.buffer = numpy.array([])

        if nonce is None:
            nonce = bytearray(96)
        self.lich = lich(dst, src, stream_type, nonce)
        self.lich_array = numpy.array(self.lich.asList(),dtype=numpy.int8)

        gr.log.debug('LICH {}'.format(self.lich))
        gr.log.debug('LICH bytes {}'.format(self.lich_array))

    def forecast(self, noutput_items, ninput_items_required):
        #setup size of input_items[i] for work call
        for i in range(len(ninput_items_required)):
            ninput_items_required = 128 * int(noutput_items / 176)
        #gr.log.debug("forecast {} {}".format(noutput_items, ninput_items_required))

    def general_work(self, input_items, output_items):

        self.buffer = numpy.concatenate((self.buffer, input_items[0],) )
        self.consume_each(len(input_items[0]))

        nout = 0
        while len(self.buffer) > 128:
            output_items[0][nout:(nout + len(self.lich_array))] = self.lich_array
            nout += len(self.lich_array)
            output_items[0][nout:(nout + 128)] = self.buffer[:128]
            self.buffer = self.buffer[128:]
            nout += 128
        if nout > 0 or len(input_items[0]) > 0:
            gr.log.debug("rx: {} gen: {}".format(len(input_items[0]), nout))

        return nout
