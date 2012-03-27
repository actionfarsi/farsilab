# Bragg Scattering
from numpy import *
from res.units import *
from res.material import optical
from matplotlib import pylab as pl

l0 = 1550 * nano
d = 0.0352 * pico / (nano**2 * kilo)
b2 = - d * l0**2 / (2*pi*3e8)
b4 = -0.29 *pico**4/kilo
 
bb = lambda l: b2*((1/l0-1/l)*(2*pi*C))**2 + b4 * ((1/l0-1/l)*(2*pi*C))**4

l_mean = 15*nano
l_delta = 4*nano

oc1 = lambda l0,lm,ld: (2*pi*C) * (1./(l0+lm-ld))
oc2 = lambda l0,lm,ld: (2*pi*C) * (1./(l0+lm+ld))
ocp = lambda l0,lm,ld: (2*pi*C) * (1./(l0-lm-ld))
ocs = lambda l0,lm,ld: (2*pi*C) * (1./(l0-lm+ld))

o1 = (2*pi*C) * (1./(l0+l_mean-l_delta))
o2 = (2*pi*C) * (1./(l0+l_mean+l_delta))
op = (2*pi*C) * (1./(l0-l_mean-l_delta))
os = (2*pi*C) * (1./(l0-l_mean+l_delta))

w_mean = l_mean *(2*pi*C) /l0**2

lm = linspace(5*nano,40*nano, 50)
ld = linspace(1*nano, 5*nano,  50)

Lm,Ld = meshgrid(lm,ld)

d_beta_b = b2*(o1**2-o2**2+os**2-op**2)
#d_beta = b2*((oc1(l0,Lm,Ld)**2-oc2(l0,Lm,Ld)**2+ocs(l0,Lm,Ld)**2-ocp(l0,Lm,Ld)**2))
d_beta = bb(l0+Lm+Ld)-bb(l0+Lm-Ld)+bb(l0-Lm+Ld)-bb(l0-Lm-Ld)
d_beta_i = bb(l0+Lm)+bb(l0+Lm)-bb(l0-Lm)-bb(l0+2*Lm)

pl.contourf(lm,ld, 1/d_beta*1e9)
pl.clabel(pl.contour(lm,ld,d_beta/d_beta_i,
            linewidths = 3),
            fmt = '%3.2f', colors = 'k', fontsize=14)
pl.show()

## Phasematching lenght
print "Phasematching lenght %.4f nm"%(1/d_beta_b*1e9)

