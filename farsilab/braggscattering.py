""" Bragg Scattering simulations """

import numpy as np
from numpy import pi, linspace, sqrt, sin, r_, conj, exp
from numpy.fft import fftfreq, fft, fftshift, ifft

from matplotlib import pylab as pl

## Farsilab Package
from .units import *
from .dispersion import Dispersion


fwhm = np.sqrt(8*np.log(2))

    
def k_bs(dispersion, wl_s, wl_p1, wl_p2, p_eff = 1 * Q_('1/km'), z = Q_(1,'m')):
    """ Bragg scattering Phasematching for a set of pump wavelength and signal
    for a given Dispersion()
    returns idler wl, k mismatch and conversion efficiency""" 

    wp1,wp2,ws1 = (2*pi*wl_p1.to('THz', 'optics'),
                  2*pi*wl_p2.to('THz', 'optics'),
                  2*pi*wl_s.to('THz', 'optics'))
            
    ws2 = wp1-wp2+ws1
    ls2 = (ws2/(2*pi)).to('nm', 'optics')
    
    beta = dispersion.beta()
    
    k = (beta(wp1)-beta(wp2)+beta(ws1)-beta(ws2))
    kappa = (2* p_eff)
    k_bs = sqrt(k**2 + kappa**2)
    gain = (kappa.to('1/m').magnitude**2/(k.to('1/m').magnitude**2 + kappa.to('1/m').magnitude**2)) \
            * sin(k_bs*z)**2
    return ls2, k, gain

def optimal_bs(d, wl_p1, wl_p2):
    wl = linspace(1200, 1300, 20000) * nm
    wl_i, dk, gain = k_bs(d, wl, wl_p1, wl_p2)
    wl_s = wl[np.argmax(gain)]
    wl_i = wl_i[np.argmax(gain)]
    return wl_s, wl_i


def BS_evolution(t, A, length,
                 dispersion, gamma, p1_wl, p2_wl, s_wl,
                 steps_number = 200):
    ## Calculate parameters
    i_wl, dk, gain = k_bs(dispersion, s_wl, p1_wl, p2_wl, z = length, p_eff = gamma)
    print('Idler wl = {:.2f}'.format(i_wl.to('nm')))
    print('expected gain = {:.2f}'.format(gain.magnitude))
    print('dk = {:.3e}'.format( (dk*length).magnitude))

    sim_wl = [s_wl, i_wl, p1_wl, p2_wl]
    beta2 = [ dispersion.beta2(wl) for wl in sim_wl]

    vgref = (dispersion.beta1(p1_wl) + dispersion.beta1(p2_wl))/2
    beta1 = [ dispersion.beta1(wl) - vgref for wl in sim_wl]

    print("Signal-pump Walk-off {:~.2}".format((beta1[0]*length).to('ps')))
    print("Signal-idler Walk-off {:~.2}".format(((beta1[0]-beta1[1])*length).to('ps')))

    ## Init the simulation
    dt = t[1]-t[0]
    w = fftfreq(len(t), dt.to('ps'))*2*pi
    z0 = 0
    sol = []

    ## Remove units
    ## for faster calculation
    t = t.to('ps').magnitude
    w = w.to('THz').magnitude
    length = length.to('m').magnitude

    beta1 = [b.to('ps/m').magnitude for b in beta1]
    beta2 = [b.to('ps**2/m').magnitude for b in beta2]

    gamma = gamma.to('1/m').magnitude
    dk = dk.to('1/m').magnitude

    ## 
    def f_w(z, A,w):
        return np.c_[ -1.j * (beta1[0]*w + beta2[0]/2* w**2),
                      -1.j * (beta1[1]*w + beta2[1]/2* w**2),
                      -1.j * (beta1[2]*w + beta2[2]/2* w**2),
                      -1.j * (beta1[3]*w + beta2[3]/2* w**2),]

    def f_bs(z, A):
        a,b,p1,p2 = A.T
        return   np.c_[ 2*gamma*1j*p1*conj(p2)*b * exp( 1j * dk* z),
                        2*gamma*1j*conj(p1)*p2*a * exp(-1j * dk* z),
                        0*p1,
                        0*p2]


    def f_xph(z,A):
        a,b,p1,p2 = A.T
        return   np.c_[ 2*gamma*1j*(abs(p1)**2+abs(p2)**2)*a,
                        2*gamma*1j*(abs(p1)**2+abs(p2)**2)*b,
                        2*gamma*1j*(0.5*abs(p1)**2+abs(p2)**2)*p1,
                        2*gamma*1j*(abs(p1)**2+0.5*abs(p2)**2)*p2]

    f_t = f_bs
    f_t = lambda z,A: f_bs(z,A) + f_xph(z,A)

    ## Run the simuluation
    sim_grid = linspace(0, length, steps_number)
    for i,z in enumerate(sim_grid):
        h = z-z0
        if z in sim_grid:
            sol.append(1*A)
        ## Splitstep 1
        A = ifft(fft(A,axis = 0)*exp( h/2 * f_w(z, A, w)), axis = 0)

        ## runge kutta
        k1 = f_t(z, A)
        k2 = f_t(z + h/2, A+h/2*k1)
        k3 = f_t(z + h/2, A+h/2*k2)
        k4 = f_t(z + h,   A+h*k3)
        A += h/6 * (k1+2*k2+2*k3+k4)

        ## Splitstep 2
        A = ifft(fft(A,axis = 0)*exp( h/2 * f_w(z, A, w)), axis = 0)
        z0 = z

    return(t * ps,
           np.array(sol))


def plot_t(t, sol, axes = None):
    if axes is None:
        fig_t, (ax_s, ax_i) = pl.subplots(1,2, sharey=True)
        fig_t.subplots_adjust(wspace=0)
    else:
        ax_s, ax_i = axes

    a_sol = abs(sol)**2       
    ## Plot time evolution
    
    # Pump Envelope
    ax_s.plot(t, a_sol[0,:,2],'--')
    ax_s.plot(t, a_sol[0,:,3],'--')

    ax_i.plot(t, a_sol[0,:,2],'--')
    ax_i.plot(t, a_sol[0,:,3],'--')

    selection = np.linspace(0, sol.shape[0]-1, 15, dtype = np.int32)
    for i in selection:
        ax_s.plot(t, a_sol[i,:,0], c = pl.cm.coolwarm(i/sol.shape[0]))
        ax_i.plot(t, a_sol[i,:,1], c = pl.cm.coolwarm(i/sol.shape[0]))

    #ax_s.set_xlim(-75,75)
    #ax_i.set_xlim(-75,75)
    ax_s.set_ylim(0,1.1)
    ax_i.set_ylim(0,1.1)
    ax_s.set_title('Signal')
    ax_i.set_title('Idler')

def plot_e(t, sol, ax = None):
    if ax is None:
        ax = pl.gca()
    a_sol = abs(sol)**2       
    ## Plot propagation evolution
    
    power = np.sum(a_sol, axis=1)

    t_power = power[0,0]+power[0,1]
    ax.plot(power[:,0]/t_power, label = 'Signal')
    ax.plot(power[:,1]/t_power, label = 'Idler')


def BS_plot(t, sol):
    def plot_p():
        ## Plot pump evolution
        fig_p, ax_p = pl.subplots() 
        for s in a_sol:
            ax_p.plot(t, s[:,2])
            ax_p.plot(t, s[:,3])

    ax_e = pl.subplot2grid((2,2),(1,0), colspan=2)
    ax_s = pl.subplot2grid((2,2),(0,0))
    ax_i = pl.subplot2grid((2,2),(0,1))
    
    plot_t(t, sol, (ax_s,ax_i))
    plot_e(t, sol, ax_e)
    #plot_p()
