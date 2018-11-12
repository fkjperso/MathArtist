#!/usr/bin/python

# MathArtist - tool for generating pictures using mathematical formulas.
# Copyright (c) 2018, Yaroslav Zotov, https://github.com/qiray/
# All rights reserved.

# This file is part of MathArtist.

# MathArtist is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# MathArtist is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with MathArtist.  If not, see <https://www.gnu.org/licenses/>.

################################################################################

# This file uses code from Andrej Bauer's randomart project under 
# following conditions:

# Copyright (c) 2010, Andrej Bauer, http://andrej.com/
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

#pyinstaller --onefile --windowed main.py --hidden-import='PIL._tkinter_finder'

import math
import random
import time
import hashlib
import sys
import signal
from datetime import datetime
from tkinter import Tk, ALL, Canvas, Button, Entry
import argparse
from PIL import Image, ImageDraw, ImageTk
import pyscreenshot as ImageGrab

from common import rgb, CONSOLE, GUI
from operators import Palette
from operator_lists import operatorsLists, fulllist, generate_lists
from coords import coord_transforms
from read_data import parse_formula, read_file
from names_generator import generate_name

APP_NAME = "MathArtist"
VERSION_MAJOR = 0
VERSION_MINOR = 9
VERSION_BUILD = 0

#TODO: readme
#TODO: console version read text file - draw image
#TODO: some refactoring
#TODO: checker for image quality?
#TODO: generate operators' lists or find nice examples and make them predefined, find more operators

class Art():
    """A simple graphical user interface for random art."""
    operatorsList = random.choice(operatorsLists)
    terminals = [op for op in operatorsList if op.arity == 0]
    nonterminals = [op for op in operatorsList if op.arity > 0]
    use_depth = True
    coord_transform = coord_transforms[0]
    polar_shifts = [[0.5, 0.5], [0, 0], [0, 1], [1, 0], [1, 1]]
    polar_shift = [0, 0]
    use_random_lists = True

    @staticmethod
    def init_static_data():
        if Art.use_random_lists:
            # We precompute those operators that have arity 0 and arity > 0
            Art.operatorsList = random.choice(operatorsLists)
            Art.terminals = [op for op in Art.operatorsList if op.arity == 0]
            Art.nonterminals = [op for op in Art.operatorsList if op.arity > 0]

        Art.use_depth = True if random.random() >= 0.5 else False
        Art.coord_transform = random.choice(coord_transforms)
        index = random.randint(-1, len(Art.polar_shifts) - 1)
        if index == -1:
            Art.polar_shift = [random.random(), random.random()]
        else:
            Art.polar_shift = Art.polar_shifts[index]

    @staticmethod
    def generate(k=8, depth=0):
        '''Randomly generate an expession of a given size.'''
        if k <= depth:
            # We used up available size, generate a leaf of the expression tree
            op = random.choice(Art.terminals)
            return op()
        # randomly pick an operator whose arity > 0 and mindepth <= depth
        if Art.use_depth and False:
            op = random.choice([x for x in Art.nonterminals if x.mindepth <= depth])
        else:
            op = random.choice(Art.nonterminals)
        # generate subexpressions
        args = [] # the list of generated subexpression
        depth += 1
        for _ in range(0, op.arity):
            args.append(Art.generate(k, depth))
        return op(*args)

    @staticmethod
    def generate_lists():
        Art.terminals, Art.nonterminals = generate_lists(fulllist)
        Art.operatorsList = Art.terminals + Art.nonterminals
        Art.use_random_lists = False
        print([x.__name__ for x in Art.operatorsList])

    def __init__(self, master, size=512, app_style=GUI, hash_string=None):
        self.root = master
        if app_style == GUI:
            self.root.title('Random art')

            def close(event):
                self.root.withdraw()
                sys.exit()
            self.root.bind('<Escape>', close)

        if hash_string:
            hex_string = hashlib.md5(hash_string.encode('utf-8'))
            hexdigest = hex_string.hexdigest()
            random.seed(int(hexdigest, 16))
            self.name = hash_string
        else:
            random.seed(datetime.now())
            self.name = generate_name()
        self.app_style = app_style
        self.size = size
        self.size_log = int(math.log(self.size, 2))
        self.filepath = '1.png'
        self.img = Image.new('RGB', (size, size))
        self.image_draw = ImageDraw.Draw(self.img)
        self.photoImage = ImageTk.PhotoImage(image=self.img)

        if app_style == GUI:
            self.canvas = Canvas(self.root, width=size, height=size)
            self.canvas.grid(row=0,column=0, columnspan=3)
            b = Button(self.root, text='New image', command=self.redraw)
            b.grid(row=1, column=0)
            b1 = Button(self.root, text='Save image', command=self.get_screenshot)
            b1.grid(row=1, column=1)
            b2 = Button(self.root, text='Generate lists', command=Art.generate_lists)
            b2.grid(row=1, column=2)
            b3 = Button(self.root, text='Read file', command=self.read_file)
            b3.grid(row=2, column=0)
            self.e1 = Entry(self.root)
            self.e1.insert(0, "samples/1.txt")
            self.e1.grid(row=2, column=1)

        self.draw_alarm = None
        self.redraw()

    def redraw(self):
        Art.init_static_data()
        Palette.randomPalette()
        self.start = time.time()
        self.name = generate_name()
        if self.draw_alarm:
            self.canvas.after_cancel(self.draw_alarm)
        if self.app_style == GUI:
            self.canvas.delete(ALL)
        self.art = Art.generate(random.randrange(1, self.size_log + 1))
        self.start_drawing()

    def start_drawing(self):
        self.print_art()
        self.d = 64   # current square size
        self.y = 0    # current row
        self.draw()
        if self.app_style == CONSOLE:
            path = "output/"
            date = str(datetime.now().strftime('%Y-%m-%d %H-%M '))
            self.photoImage = ImageTk.PhotoImage(image=self.img)
            self.img.save(path + date + self.name + ".png")
            orig_stdout = sys.stdout #save original stdout
            f = open(path + date + self.name + ".txt", 'w')
            sys.stdout = f #redirect stdout to file
            self.print_art()
            sys.stdout = orig_stdout #restore original stdout
            f.close()
            exit(0)

    def draw(self):
        if self.y >= self.size:
            self.y = 0
            self.d = self.d // 4
        if self.d < 1:
            self.draw_alarm = None
            self.end = time.time()
            print("Time for drawing:", self.end - self.start)
            return
        for x in range(0, self.size, self.d):
            #Convert coordinates to range [-1, 1]
            u, v = Art.coord_transform(x, self.y, self.d, self.size, Art.polar_shift)
            (r, g, b) = self.art.eval(u, v)
            if self.app_style == CONSOLE:
                self.image_draw.rectangle(
                    ((x, self.y), (x + self.d, self.y + self.d)),
                    fill=rgb(r, g, b)
                )
            else:
                self.canvas.create_rectangle(
                    x, self.y, x+self.d, self.y+self.d,
                    width=0, fill=rgb(r, g, b)
                )
        self.y += self.d
        if self.app_style == CONSOLE:
            self.draw()
        else:
            self.draw_alarm = self.canvas.after(1, self.draw)

    def read_file(self):
        art, use_depth, coord_transform, polar_shift, name = read_file(self.e1.get())
        self.read_art_params(art, use_depth, coord_transform, polar_shift, name)

    def read_art_params(self, art, use_depth, coord_transform, polar_shift, name):
        self.art = parse_formula(art)
        Art.use_depth = parse_formula(use_depth)
        Art.coord_transform = parse_formula(coord_transform)
        if polar_shift:
            Art.polar_shift = parse_formula(polar_shift)
        if name:
            self.name = name
        else:
            self.name = generate_name()
        self.start = time.time()
        self.canvas.delete(ALL)
        self.start_drawing() #draw image with new params

    def print_art(self):
        print("Name:", self.name)
        print("Using operators:", [x.__name__ for x in Art.operatorsList])
        print("Use depth:", Art.use_depth)
        print("Coordinates transfrom:", Art.coord_transform.__name__)
        if Art.coord_transform.__name__ == 'polar':
            print("Polar shift:", Art.polar_shift)
        print("Formula:", self.art, '\n') #draw art tree

    def get_screenshot(self):
        if __name__ != '__main__':
            return
        margin = 2 #I don't know where did this value came from
        x = self.root.winfo_rootx() + self.canvas.winfo_x() + margin
        y = self.root.winfo_rooty() + self.canvas.winfo_y() + margin
        x1 = x + self.canvas.winfo_width() - 3*margin
        y1 = y + self.canvas.winfo_height() - 3*margin
        ImageGrab.grab(bbox=(x, y, x1, y1), childprocess=False).save(
            str(datetime.now().strftime('%Y-%m-%d %H-%M ')) + self.name + ".png"
        )

# Main program

def sigint_handler(sig, frame):
    print("Closing...")
    sys.exit(0)

def parse_args():
    """argparse settings"""
    parser = argparse.ArgumentParser(prog=APP_NAME, 
        description='Tool for generating pictures using mathematical formulas.')
    parser.add_argument('--console', action='store_true', help='Run in console mode (no window)')
    parser.add_argument('--about', action='store_true', help='Show about info')
    return parser.parse_args()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_handler)
    args = parse_args() #parse command line arguments
    win = Tk()
    if args.about:
        print("\n" + APP_NAME + " Copyright (C) 2018 Yaroslav Zotov.\n" +
            "Based on \"randomart\" Copyright (C) 2010, Andrej Bauer.\n"
            "This program comes with ABSOLUTELY NO WARRANTY.\n" +
            "This is free software; see the source for copying conditions\n")
        exit(0)
    if args.console:
        art = Art(None, app_style=CONSOLE)
    else:
        art = Art(win)
        win.mainloop()
