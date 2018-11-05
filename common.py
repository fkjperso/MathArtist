#!/usr/bin/python

# Copyright (c) 2010, Andrej Bauer, http://andrej.com/
# Copyright (c) 2018, Yaroslav Zotov, https://github.com/qiray/
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import math
import itertools

CANVAS = 1
IMAGE = 2

# File with utility functions

# Math functions

def well(x):
    '''A function which looks a bit like a well.'''
    result = 1 - 2 / (1 + x*x) ** 8
    result = 1 if result < -1 else result
    return result

def tent(x):
    '''A function that looks a bit like a tent.'''
    return 1 - 2 * abs(x)

def sin_curve(x):
    val = x if x != 0 else 1
    return math.sin(1/val)

def abs_sin(x):
    return math.sin(math.fabs(x))

def wave(x, y):
    return math.sin(math.sqrt(x**2 + y**2))

# Color functions

def float_color_to_int(c):
    return max(0, min(255, int(128 * (c + 1))))

def average(c1, c2, w=0.5):
    '''Compute the weighted average of two colors. With w = 0.5 we get the average.'''
    (r1,g1,b1) = c1
    (r2,g2,b2) = c2
    r3 = w * r1 + (1 - w) * r2
    g3 = w * g1 + (1 - w) * g2
    b3 = w * b1 + (1 - w) * b2
    return (r3, g3, b3)

def rgb(r,g,b):
    '''Convert a color represented by (r,g,b) to a string understood by tkinter.'''
    u = float_color_to_int(r)
    v = float_color_to_int(g)
    w = float_color_to_int(b)
    return '#%02x%02x%02x' % (u, v, w)

def parse_color(str):
    h = str.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))

def color_binary(c1, c2, operator):
    colors1 = tuple([float_color_to_int(x) for x in c1])
    colors2 = tuple([float_color_to_int(x) for x in c2])
    return tuple([2*operator(x1, x2)/255.0 - 1 for x1, x2 in zip(colors1, colors2)])
