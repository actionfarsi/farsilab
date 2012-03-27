from numpy import *
from matplotlib import pylab as pl

import sys,os

def breakp(n):
	v,s = loadtxt("breakdown-%03d.txt"%n,delimiter=',', unpack=True)
	pl.plot(v,s/s[5])
	pl.semilogy()

breakp(1)
#breakp(2)
breakp(3)
breakp(4)
pl.show()
