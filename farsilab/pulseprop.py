import numpy as np
from numpy.fft import fftfreq, fft, fftshift
from numpy import pi, linspace, sqrt, exp
from matplotlib import pylab as pl

## Farsilab Package
from .units import *
from .dispersion import Dispersion
import .nlin_prop as nl

class PulsePropagation():
    """ Wrapper for nonlinear S. equation,
    tracking information about wavelenght and pulses
    and converting to frequencies
    
    Units are tracked via 'pint'
    
    """
    def __init__(self, beta = Q_(1e-20, 'ps**2/m'),
                 gamma = Q_(1,'watt^-1 meter^-1') ):
        
        self.pulses = []
        self.probes = [] 
        self.beta = [Q_(0,'ps/m'), beta, Q_(0,'ps**3/m') ]
        self.w0 = Q_(0,'rad THz')      ## Carrier freq and center of simulation (absolute value)
        self.w_gvd = Q_(0,'rad THz')   ## GVD expansion point (absolute values)
        self.gamma = gamma * Q_(.1,'watt')
        ## To be implemented
        self.reprate = None
        self.p_avg = None
        
        self.sols = None
        self.results = None
    
    @property
    def l0(self):
        if self.w0.magnitude == 0:
            return Q_(0,'nm')
        else:
            return self.w0.to('nm', 'optics')*(2*pi)
    
    @l0.setter
    def l0(self, value):
        self.w0 = value.to('THz', 'optics')*(2*pi)
    
    def add_pulse(self, **kwd):
        self.pulses.append(kwd)
        
    def add_probe(self, **kwd):
        self.probes.append(kwd)
    
    def generate_pulse(self, dt, f = nl.gaussian_pulse, t0 = 0, p = 1, 
                       dv = Q_(0, 'rad THz'),
                       wl = None):
        if wl is not None:
            if w0 == 0:
                print("Warning, l0 not set")
            else:
                dv = w0 / 2*pi - wl.to('THz', 'optics')
                
        return sqrt(p)*f(self.t, dt)*exp(-1j*2*pi*dv*self.t)
    
    def set_dispersion(self, d, wl_gvd):
        beta = - wl_gvd**2 / (c_light * 2 * pi) * d
        self.beta = [Q_(0,'ps/m'), beta, Q_(0,'ps**3/m')]
        
        ## if array fit and then calculate b2 and b3 at w0 point
        if len(np.array(d),ndmin = 1) > 1:
            beta_fit = poly1d(polyfit(beta.to('ps^2'),d,3))
            self.beta[1] = beta_fit(self.w0)
            self.beta[2] = beta_fit.diff(self.w0)
        
    
    def set_gvd(self, b1, b2, b3,  w_gvd = Q_(0,'rad THz'), wl_gvd = None):
        self.w_gvd = w_gvd
        if wl_gvd is not None:
            self.w_gvd = wl_gvd.to('rad THz', 'optics')
        
    def init_report(self):
        t_step = self.t[1]-self.t[0]
        w_step = self.w[2]-self.w[1]
        report = ""
        if self.w0.magnitude != 0:
            report += "w0 = 2 Pi {:.1f~}  (l0 = {:.1f~})\n".format( self.w0.to('rad THz')/(2 * pi), self.l0)
            
        report += "GVD at w0 = {:.1f~}\n".format( self.beta[1].to('ps**2/m'))
        if self.w0.magnitude != 0:
            report += "(D = {:.2f~})\n".format((-self.beta[1]*(2*pi*c_light)/self.l0**2).to('ps/nm/km'))
        report += "dt = {:.2f~}, dw = {:.2f~}\n".format(t_step.to('ps'), w_step.to('GHz'))
        return report
    
    def run(self, z, N = 2**14, self_steep = False):
        # euristic for setting the timescale
        dts = [p['dt'].to('ps').magnitude for p in self.pulses]
        timescale = max(dts)*5e2
        
        self.t = np.linspace(-timescale,timescale,N) * ps
        t_step = self.t[1]-self.t[0]
        
        self.w = fftfreq(N,t_step)*2*pi
        w_step = self.w[2]-self.w[1]
        
        self.z = pl.linspace(0,z.to('m').magnitude,10)*Q_('m')
        
        print(self.init_report())
        ## ToDo Verify all pulses are within the simulation
        
        self.a0 = np.sum(np.c_[[self.generate_pulse(**p) for p in self.pulses]],0)
        
        
        ## Generate operators
        dw = self.w
        dispersion = 1/2. *self.beta[1] * dw**2 + 1./6 *self.beta[2] * dw**3
        nlinear = self.gamma
        if self_steep:
            self_steep = self.gamma/self.w0.to('1/ps').magnitude
        else:
            self_steep = 0
        
        
        ## Start simulation
        self.sols = nl.split_step(self.a0, self.z, w_op = dispersion, nlin = nlinear,
                                  dt = t_step.to('ps').magnitude, self_steep = self_steep)
        self.results = Solution(self.sols, self.t, fftshift(self.w.to('GHz').magnitude)*Q_('GHz'), z = self.z)
        self.results.l0 = self.l0
        
        return self.sols

    
        
        
class Solution():
    def __init__(self, solution, t, w = None, z = None,
                l0 = None):
        self.solution = solution
        self.t = t.to('ps').magnitude
        self.w = w.to('GHz').magnitude
        self.z = z.to('m').magnitude
        
        self.l0 = None
        if self.w is None:
            self.w = fftshift(fftfreq(len(self.t),self.t[1]-self.t[0]))
        if self.z is None:
            self.z = linspace(0,1,len(self.solution))
            
        ## cache fft
        self.s_fft = [fftshift(fft(s)) for s in self.solution]
        
    def plot_evolution_w(self):
        for s,i in enumerate(self.solution):
            self.plot_spectrum(s)
            
    def plot_evolution(self):
        for s,i in enumerate(self.solution):
            self.plot_temporal(s)
    
    def plot_3d(self):
        pl.contourf(self.z, self.t, abs(np.array(self.solution).T)**2,
                    n = 30, cmap=pl.cm.coolwarm)
        
    def plot_temporal(self, i = -1, axis = None):
        if axis == None:
            axis = pl.gca()
        axis.plot(self.t, abs(self.solution[i])**2,
                  c = pl.cm.coolwarm(i/len(self.solution)))
        axis.set_xlabel('Time (ps)')
    
    def plot_spectrum(self, i = -1, axis = None):
        
        if i == -1:
            i = len(self.solution)-1
        if axis == None:
            axis = pl.gca()
        
        
        y = abs(self.s_fft[i])**2
        if self.l0 is not None:
            x = (self.l0.to('GHz','optics') + (self.w*Q_('GHz'))/(2*pi)).to('nm','optics')
            axis.set_xlabel('Wavelenght (nm)')
        else:
            x = self.w / (2 * pi)
            axis.set_xlabel('Frequency (GHz)')
            
        axis.plot(x, y,
                 c = pl.cm.coolwarm(i/len(self.solution)))
        
        
        