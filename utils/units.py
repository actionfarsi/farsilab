#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Action Farsi"
__date__ ="$Apr 28, 2010 4:25:07 PM$"

## Helper Class
class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

# Constants
C = 2.99792458e8
PI      = 3.1416

giga      = 1e9
mega      = 1e6
kilo      = 1e3
mill      = 1e-3
micr      = 1e-6
nano      = 1e-9
angs      = 1e-10
pico      = 1e-12
femt      = 1e-15
atto      = 1e-18

units = {giga: 'G',
         mega: 'M',
         kilo: 'k',
         mill: 'm',
         micr: r'\mu',
         nano: 'n',
         angs: r'\aa',
         pico: 'p',
         femt: 'f',
         atto: 'a'}

if __name__ == "__main__":
    print "Units";
