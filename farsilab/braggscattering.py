""" Bragg Scattering simulations """

import numpy as np
from numpy import pi, linspace, sqrt, sin, r_, c_, conj, exp, array, linspace, zeros
from numpy.fft import fftfreq, fft, fftshift, ifft

from scipy.integrate import odeint, complex_ode
import lmfit

from itertools import combinations, permutations

from matplotlib import pylab as pl

## Farsilab Package
from .units import *
from .dispersion import Dispersion


fwhm = np.sqrt(8*np.log(2))



    
def k_bs(p1_wl, p2_wl, s_wl, dispersion, 
         p_eff = 1 * Q_('1/km'), z = Q_(1,'m')):
    """ Bragg scattering Phasematching for a set of pump wavelength and signal
    for a given Dispersion()
    returns idler wl, k mismatch and conversion efficiency""" 

    k_unit = Q_('1/m')
    wp1,wp2,ws1 = (2*pi*Q_('c')/p1_wl,
                   2*pi*Q_('c')/p2_wl,
                   2*pi*Q_('c')/ s_wl)
            
    ws2 = wp1-wp2+ws1
    ls2 = (2*pi*Q_('c')/ws2)
    
    beta = dispersion.beta
    dbeta = (beta(wp1)-beta(wp2)+beta(ws1)-beta(ws2))
    kappa = dbeta/2 # dipsersive wavevector 
    
    r = (2*p_eff)
    kappa_bs = sqrt((kappa)**2 + r**2)

    gain =     (r.to(k_unit).magnitude**2 \
          /((kappa.to(k_unit).magnitude)**2 + r.to(k_unit).magnitude**2)) \
          * sin(kappa_bs*z)**2
    return ls2, dbeta, gain.magnitude

def eta_vs_p_f(x, k, p_eff, a ):
    r = 2*x/p_eff
    k_bs = sqrt(k**2 + r**2)
    return a*(1-(r**2/(k**2 + r**2))* sin(k_bs)**2)

def eta_vs_wl_f(x, d_wl, wl0, r ):
    k = (x - wl0)/d_wl
    k_bs = sqrt(k**2 + r**2)
    return (r**2/(k**2 + r**2))* sin(k_bs)**2


def optimal_bs(p1_wl, p2_wl, d, 
               gamma, length, 
               limits = (1200, 1400)):

    wl = linspace(limits[0], limits[1], 20000)
    i_wl, dk, gain = k_bs(p1_wl, p2_wl, wl * nm, d, p_eff= gamma, z =length)

    s_wl = wl[np.argmax(gain)]
    #i_wl = wl_i[np.argmax(gain)]

    res = lmfit.Model(eta_vs_wl_f).fit(gain,
                       x = wl,
                       d_wl = 1, r = 1, wl0 = s_wl)
    #pl.plot(wl, gain)
    #print(gain, s_wl, wl)
    #pl.plot(wl, lmfit.Model(eta_vs_wl_f).fit(gain,
    #                   x = wl,
    #                  d_wl = .1, r = 1, wl0 = s_wl))

    print(res.fit_report())
    res.plot_fit()

    
    
    return s_wl, i_wl


def BS_evolution(t, A,
                 p1_wl, p2_wl, s_wl,
                 dispersion,
                 gamma, length,
                 n_steps = 200):
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

    ## Define the functions
    def f_w(z, A,w): # Dispersion (f_w)
        return np.c_[ -1.j * (beta1[0]*w + beta2[0]/2* w**2),
                      -1.j * (beta1[1]*w + beta2[1]/2* w**2),
                      -1.j * (beta1[2]*w + beta2[2]/2* w**2),
                      -1.j * (beta1[3]*w + beta2[3]/2* w**2),]

    def f_bs(z, A): # BS FWM
        a,b,p1,p2 = A.T
        return   np.c_[ 2*gamma*1j*p1*conj(p2)*b * exp( 1j * dk* z),
                        2*gamma*1j*conj(p1)*p2*a * exp(-1j * dk* z),
                        0*p1,
                        0*p2]


    def f_xph(z,A): # Cross Phase modulation
        a,b,p1,p2 = A.T
        return   np.c_[ 2*gamma*1j*(abs(p1)**2+abs(p2)**2)*a,
                        2*gamma*1j*(abs(p1)**2+abs(p2)**2)*b,
                        2*gamma*1j*(0.5*abs(p1)**2+abs(p2)**2)*p1,
                        2*gamma*1j*(abs(p1)**2+0.5*abs(p2)**2)*p2]

    f_t = f_bs
    f_t = lambda z,A: f_bs(z,A) + f_xph(z,A)

    ## Run the simulation Splitstep with a f_w and a f_t
    sim_grid = linspace(0, length, n_steps)
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

def BS2_evolution(t, A, length,
                 dispersion, gamma, p_wl, s_wl,
                 n_steps = 200):
    """ Bragg using two fields NOT implemented"""

    ## Calculate parameters
    i_wl, dk, gain = k_bs(p1_wl, p2_wl, s_wl,  dispersion, z = length, p_eff = gamma)
    print('Idler wl = {:.2f}'.format(i_wl.to('nm')))
    print('expected gain = {:.2f}'.format(gain))
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
    sim_grid = linspace(0, length, n_steps)
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



### Multichannel
def generateCoefficients(phasematching, A_p = [1,1],
                         n_order = 3, kappa_limit = 1e3):
    """ For every combination of pump, generate the coupling coefficients 
        phasematching is a dimensionless function of channel number (not channel index)
        p1, p2, s1, s2.

        returns a dictionary containing the phasematching kappa and the coupling strenght r
        for each energy-matched and phase-matched 4-plet
        """
    
    k_list = {}
    
    # For each pair of pumps that is not 0
    for p in permutations(np.where(A_p)[0], 2):
        s_index = np.arange(-n_order, n_order+1,1)
        p_index = np.array(p) - len(p)/2 + 1/2
       
        s_I1, s_I2 = np.meshgrid(s_index, s_index)

        # energy conservation
        e_c = p_index[0]-p_index[1] + s_I1 - s_I2
        e_c = np.where(e_c == 0, 1, 0)

        kappa = phasematching(p_index[0], p_index[1], s_I1, s_I2)
        # limit phasematching term to not be too big, accuracy
        e_c = np.where(abs(kappa) < kappa_limit, e_c, 0) 
        kappa = kappa * e_c

        r = 2*e_c * (A_p[p[0]] * conj(A_p[p[1]]))  # coupling term

        k_list[p] = (kappa, r)
    return k_list

def generatePhasematching(p_w, s_w, dw, dispersion, k_unit = Q_('1/m')):    
    """ Generate a dimensionless phasematching function,
    depending only on the channel number (not channel index!!) """
    beta = dispersion.beta
    return lambda p1,p2,s1,s2: ( beta((p1*dw+p_w) ) - beta((p2*dw+p_w) ) \
             +beta((s1*dw+s_w) ) - beta((s2*dw+s_w) )).to(k_unit).magnitude


def interactionMatrixZ(kappa_dict, z, N):
    """ Interaction matrix with z-dependency due to phasematching terms
    It is obtained adding up all the possible combinations
    it is dimensionless.
    """
    y_p = np.zeros( (N,N), dtype=np.complex64 )
    for kappa, gamma in kappa_dict.values():
        y_p += 1j*exp(1j*kappa*z)*gamma
    return y_p

def BS_mc_evolution( p0, gamma, length, dispersion,
                     s_wl, p1_wl, p2_wl,
                     s_0 = np.array([0,1,0], dtype=np.complex64),
                     a_p = r_[1,1],
                    
                     ## Losses terms (for completeness)
                     alpha_l  = Q_('0 1/m'), # Loss
                     alpha_2p = Q_('0 1/(W m)'), # NL loss
                     s_fca    = Q_('0 m**2'), t_fca = Q_(1, 'as'), # TPA
                     w0_wl = 1550 * nm,    ## FCA defined at 1550 nn
                     
                     vary_pump = False,
                     grid_size = 100):
    
    """ Bragg Scattering MultiChannel Simulation 

    requires Units and Dispersion

    wl1, wl2: define the pump frequency comb (i.e. p_w and dw)
    s_wl: is the input signal wavelength.
    dispersion: is the dispersion (Dispersion)

    s_0: input fields. Size of the array determines the channels
    a_p: are the pump fields amplitudes normalized to p0
    
    """

    # Simulation units
    u_l = Q_('mm')
    u_p = Q_('W')

    # Obtain angular frequency
    p_w = 2*pi*c_light*(1/p1_wl + 1/p2_wl)/2
    s_w = 2*pi*c_light/s_wl
    dw = (1/p1_wl - 1/p2_wl)*2*pi*c_light  # Channel separation

    z = length.to(u_l).magnitude
    dz = z/grid_size
    
    # signal is centered at len(s_0)/2
    n_ch = len(s_0)
    n_order = np.floor(n_ch / 2)
    a_s = s_0
    
    # Generate a dimensionless phasematching function.
    phasematching = generatePhasematching(p_w, s_w, dw,
                                          dispersion, k_unit = 1/u_l)
    
    # Effective nonlinearity
    nl_eff = gamma * p0
    a_p = a_p * sqrt(nl_eff.to(1/u_l).magnitude)
    
    p_out = np.zeros((gridsize + 1, len(a_p)), dtype= np.complex64)
    
    if varying_pump:
        ## Simulate pumps
        ode_pump = complex_ode(f)
        ode.set_initial_value(a_p)
        i = 1
        for zi in np.arange(dz, z, dz):
            output [i,:] = ode.integrate(zi)
            i += 1
            if not ode.successful():
                raise Exception()
    
    # Use it to generate the coupling matrix coefficients
    k_dict = generateCoefficients(a_p = a_p, phasematching = phasematching, 
                                  n_order= n_order, kappa_limit = 1e3/dz)
    
    
    
    
    # Losses
    #a2p_eff = alpha_2p * p0
    
    #h_nup = Q_('h*c')/w0_wl
    #fca = [alpha_2p*t_fca/(2*h_nup)*s_fca*(wl/w0_wl)**2 * p0**2 \
    #                      for wl in [s_wl, i_wl, p1_wl, p2_wl]]
    
    #fca = zeros(4) * Q_('1/m') # FCA formula may be wrong
    
    ## There is a BUG in scipy for functions accepting external arguments in complex_ode.
    ## I just make them global and unitless
    #args =          ( dk.to(1/u_l).magnitude,
    #              nl_eff.to(1/u_l).magnitude,
    #             alpha_l.to(1/u_l).magnitude,
    #             a2p_eff.to(1/u_l).magnitude,
    #              r_[ [f.to(1/u_l).magnitude for f in fca] ] )

    
    ## Compute simulation parameters ###
    print(k_dict)

    # Define a f(z, x) = dx/dz
    f = lambda z, x: np.dot(x, interactionMatrixZ(k_dict, z, n_ch))
    
    # Build the output array
    output = np.zeros((grid_size+1, n_ch), dtype= np.complex64)
    output[0,:] = a_s

    # Finally, simulate
    ode = complex_ode(f)
    ode.set_initial_value(a_s)
    i = 1
    for zi in np.arange(dz, z, dz):
        output [i,:] = ode.integrate(zi)
        i += 1
        if not ode.successful():
            raise Exception()

    return (output, dz)



## Multichannel Plotting
def plot_mc_phasematching(p1_wl, p2_wl, s_wl, d,
                         gamma, length, n_order=3,
                         ax = None):
    
    if ax is None:
        ax = pl.gca()

    p_w = 2*pi*c_light*(1/p1_wl + 1/p2_wl)/2
    s_w = 2*pi*c_light*(1/s_wl)
    dw =  2*pi*c_light*(1/p1_wl - 1/p2_wl)
    
    s_r = 2*pi*c_light/(np.linspace(-n_order-1, n_order+2, 1000) * dw + s_w)
    s = 2*pi*c_light/(np.arange(-n_order, n_order+1,1) * dw + s_w)

    i_wl, dk, gain = k_bs(p1_wl, p2_wl, s_r, d, p_eff = gamma, z = length)
    ax.plot(s_r, gain)
    for w in s:
        ax.axvline(w.magnitude, ls='--', c = 'green', lw = 2)



## Plot the result
def plot_mc_results(output, dz = 1):
    Z,N = output.shape
    x = dz*np.arange(Z)
    f, ax = pl.subplots(figsize=(12,4))
    ax.imshow(abs(output.T)**2, aspect='auto', interpolation='none', cmap='Reds')
    ax.set_xlabel('Propagation dx')
    f, [ax1, ax2] = pl.subplots(1,2, figsize=(12,3))
    
    ax1.plot(x,abs(output[:,N//2])**2)  # Plot few channels
    ax1.plot(x,abs(output[:,N//2-1])**2)
    ax1.plot(x,abs(output[:,N//2+1])**2)  # Plot few channels
    ax1.plot(x,abs(output[:,N//2-2])**2)
    ax1.plot(x,abs(output[:,N//2+2])**2)  # Plot few channels
    ax1.plot(x,abs(output[:,N//2-3])**2)
    ax1.plot(x,abs(output[:,N//2+3])**2)  # Plot few channels

    ax1.plot(x,np.sum(abs(output)**2,1), c = 'k', ls = '--') # Total Energy
    ax1.set_xlabel('Propagation dx')
    
    ax2.bar(pl.arange(N)-N/2,abs(output[-1])**2)


## Output Class Helper
class BS_simulation_results():
    pass

class BS_mc_simulation():
    pass


#out = r_[[bsSimulation(l_1, l_2, l_s, d, length = length, a_p = a_p * p, n_order=n_order)[0][-1,:] for p in powers]]