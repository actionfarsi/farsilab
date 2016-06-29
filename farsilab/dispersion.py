""" Dispersion """

import numpy as np
from numpy import pi, linspace, sqrt, sin, r_, conj, exp
from scipy.interpolate import UnivariateSpline as spline

from .units import *

class Dispersion():
    def __init__(self, wl_range = (1000, 1800)):
        self.wl = linspace(wl_range[0], wl_range[1], 300) * nm
        self.n = np.ones_like(self.wl)
    
    @property
    def w(self): return 2*pi*c_light / self.wl
    
    def beta(self, wl = None, deriv = 0):
        k = 2*pi*self.n / self.wl

        i = np.argsort(self.w)
        w, k = self.w[i], k[i]

        beta = spline(w.to('THz').magnitude, k.to('1/nm').magnitude, s = 0)
        if wl is not None:
            return beta.derivative(n=deriv)( (2*pi*c_light/wl).to('THz')) / Q_('THz')**deriv / nm
        else:
            return ureg.wraps(1/nm, Q_('THz'))(lambda x: beta(x))
    
    def beta1(self, wl): return self.beta(wl, 1)
    
    def beta2(self, wl): return self.beta(wl, 2)
    
    def beta3(self, wl): return self.beta(wl, 3)
    
    def from_coef(w0, b2 = Q_(0, "ps**2/m"), b3 = Q_(0, "ps**3/m"), b4 = Q_(0,"ps**4/m")):
        d = Dispersion()
        k = 1/2. * b2 * (d.w - w0)**2 + 1/6. *b3 * (d.w - w0)**3 + 1/24. *b4 * (d.w - w0)**4
        d.n = k*d.wl/(2*pi)
        return d
    
    
    def from_beta2(w, b):
        d = Dispersion()
        # Make sure is ordered
        i = np.argsort(w)
        w, b = w[i], b[i]

        b1 = spline(w,b.to('s**2/m').magnitude).integral(0, w.to('s').magnitude)
        k = b1.integra(0, w)
        self.n = k*d.wl/(2*pi)
        return d
    
    
    def from_dispersion(wl, d):
        # convert to beta2
        b2 = - wl**2/(2*pi*c_light)*d
        return Dispersion.from_beta2(2*pi*c_light/wl, b2)
    
    def __call__(self, wl):
        return self.beta2(2*pi*c_light/wl)