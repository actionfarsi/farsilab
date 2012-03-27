from matplotlib import pylab as pl
from numpy import *
from numpy import fft

c = 3e8

def beta(w):
    l0 = 1.550e-6
    w0 = 2*pi*c/l0
    d = 0.019e-15
    b = [1/c*w0, 1/c, -d*l0**2/(2*pi*c), 1e-40, 1e-50]
    return b[0] + b[1]*(w-w0)+b[2]*(w-w0)**2#+b[3]*(w-w0)**3 +b[4]*(w-w0)**4
 
wavelength = linspace(1.510e-6, 1.560e-6,2**10)
w =2*pi*c/wavelength
print w-2*pi*c/1.550e-6
phi = (1/c*w-beta(w)*1.05)

#pl.plot(wavelength/1e-6,cos(phi))
pl.plot(abs(fft.fft(cos(phi))))
pl.show()
