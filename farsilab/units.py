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

import pint
ureg = pint.UnitRegistry()

c = pint.Context('optics')
c.add_transformation('[length]', '1/[time]',
                      lambda ureg, x: ureg.speed_of_light / x)
c.add_transformation('1/[time]', '[length]',
                      lambda ureg, x: ureg.speed_of_light / x)
ureg.add_context(c)

Q_ = ureg.Quantity

ps = Q_(1,'ps')
nm = Q_(1,'nm')
THz = Q_(1,'THz')

c_light = Q_(299792458, 'm/s')

# Constants
PI      = 3.1416

