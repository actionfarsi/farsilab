from numpy import *

from matplotlib import pylab as pl

import sys,os

#for f in sys.argv[1:]:
#       findres(f)

power = 100
dutycycle = 1e-8 * 100e3
flux = 10**(-power/10.-3)/1.23e-19*dutycycle
print "flux =", flux


v,dc = loadtxt("breakdown-011.txt", delimiter=",", unpack=True)
v,lg = loadtxt("breakdown-012.txt", delimiter=",", unpack=True)
sign = lg-dc
snr = sign/(dc+0.1)
# deriv = diff(sign)
# where(sign>0,sign,0.0001)

# pl.plot(v,dc)
# pl.plot(v,lg)
# pl.plot(v,dc)
# pl.figure(2)
pl.plot(v,snr, label="APD 1")

pl.figure(3)
pl.errorbar(v,sign/flux, yerr=0*(dc)/flux, label="APD 1", color = 'b')
pl.grid()
pl.fill_between(v,dc/flux, 0.0001, alpha = 0.2, color='b')
# pl.figure()
# pl.plot(v,dc)
pl.semilogy()


pl.show()