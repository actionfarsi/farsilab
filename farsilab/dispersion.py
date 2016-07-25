""" Dispersion """

import numpy as np
from numpy import pi, linspace, sqrt, sin, r_, conj, exp, \
                 diff,cumsum
from scipy.interpolate import UnivariateSpline as spline
from scipy.integrate import cumtrapz
from .units import *

class Dispersion():
    def __init__(self, wl_range = (1000, 1800)):
        self.wl = linspace(wl_range[0], wl_range[1], 300) * nm
        self.n = np.ones_like(self.wl)
        self.t_unit = Q_('THz')
    
    @property
    def w(self): return 2*pi*c_light / self.wl
    
    def beta(self, omega = None, *argv, wl = None):
        k = 2*pi*self.n / self.wl

        i = np.argsort(self.w)
        w, k = self.w[i], k[i]

        beta = spline(w.to('THz').magnitude,
                      k.to('1/m').magnitude, s = 0, k = 5)
        beta_f = ureg.wraps(Q_('1/m'), Q_('THz'))(lambda x: beta(x))

        if wl is not None: return beta_f(2*pi*c_light/wl)
        if omega is None:  return beta
        else:              return beta_f(omega)
    
    def beta1(self, omega = None, *argv, wl = None):
        i = np.argsort(self.w)
        w = self.w[i].to('THz').magnitude
        beta = self.beta(self.w[i])

        beta = beta.to('1/m')
        #beta1 = spline( w[1:], diff(beta)/diff(w), s = 0 , k = 4)
        beta1 = self.beta().derivative(1)
        beta1_f = ureg.wraps(Q_('ps/m'), Q_('THz'))(lambda x: beta1(x))
        if wl is not None:  return beta1_f(2*pi*c_light/wl)
        if omega is None:   return beta1_f
        else:               return beta1_f(omega)

        #return self.beta(wl, 1)
    
    def beta2(self, omega = None, *argv, wl = None):
        i = np.argsort(self.w)
        w = self.w[i].to('THz').magnitude
        #beta1 = self.beta1(self.w[i])

        #beta1 = beta1.to('ps/m')
        #beta2 = spline(  w[1:], diff(beta1)/diff(w), s = 0, k = 4)
        beta2 = self.beta().derivative(2)
        beta2_f = ureg.wraps(Q_('ps**2/m'), Q_('THz'))(lambda x: beta2(x))

        if wl is not None: return beta2_f(2*pi*c_light/wl)
        if omega is None:  return beta2_f
        else:              return beta2_f(omega)

        # return self.beta(wl, 2)
    
    def beta3(self, wl):
        beta3 = self.beta().derivative(3)
        beta3_f = ureg.wraps(Q_('ps**3/m'), Q_('THz'))(lambda x: beta2(x))

        if wl is not None: return beta3_f(2*pi*c_light/wl)
        if omega is None:  return beta3_f
        else:              return beta3_f(omega)
        # return self.beta(wl, 3)
    
    def beta4(self, wl):
        beta3 = self.beta().derivative(4)
        beta3_f = ureg.wraps(Q_('ps**4/m'), Q_('THz'))(lambda x: beta2(x))

        if wl is not None: return beta4_f(2*pi*c_light/wl)
        if omega is None:  return beta4_f
        else:              return beta4_f(omega)


    def from_coef(w0, b2 = Q_(0, "ps**2/m"), b3 = Q_(0, "ps**3/m"), b4 = Q_(0,"ps**4/m")):
        d = Dispersion()
        k = 1/2. * b2 * (d.w - w0)**2 + 1/6. *b3 * (d.w - w0)**3 + 1/24. *b4 * (d.w - w0)**4
        d.n = k*d.wl/(2*pi)
        return d
    
    
    def from_beta2(omega, beta2, wl_range = (1200, 1600)):
        print(wl_range)
        d = Dispersion(wl_range = wl_range)
        # Make sure is ordered
        i = np.argsort(omega)
        w = omega[i].to('THz').magnitude
        b2 = beta2[i].to('ps**2/nm').magnitude

        #b2_s = spline(w, b)
        #b1_s = spline(w,[b2_s.integral(w[0],ww) for ww in w])
        #k_s  = spline(w,[b1_s.integral(w[0],ww) for ww in w])

        b1 = cumtrapz(b2,w, initial = 0)
        k = cumtrapz(b1,w, initial = 0)

        # Careful, if w and k have very large numbers, spline fails
        k_s = spline(w,k, s = 0, k = 4)
        d.n = k_s(d.w.to('THz').magnitude) * d.wl.to('nm').magnitude/(2*pi)
        return d
    
    
    def from_dispersion(wl, d):
        # convert to beta2
        b2 = - wl**2/(2*pi*c_light)*d
        return Dispersion.from_beta2(2*pi*c_light/wl, b2,
        wl_range = (np.amin(wl).to('nm').magnitude, np.amax(wl).to('nm').magnitude))
    
    def __call__(self, wl):
        return - self.beta2(2*pi*c_light/wl) / wl**2*(2*pi*c_light)