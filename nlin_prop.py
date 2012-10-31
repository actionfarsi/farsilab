""" Non linear propagation
A module for time-split integration both linear and
non-linear Schroedinger, in the context of beam propagation.

for convention A(t,z) is the field
"""

from res.units import *
from numpy import *
from numpy.fft import fft, ifft, fftfreq, fftshift, ifftshift
from scipy.special import erf
from scipy.integrate import trapz
from scipy.io import loadmat, savemat

import matplotlib.pyplot as pl

import pdb

def split_step(A0, z_array,       # Array for solution points
                t_op = 0, w_op = 0, nlin = 0,  # Constant operators
                dt = 1,           # sampling time
                t_nl_op = None,   # Additional operator f(A, dt, z)
                apod = True,      # Boundary conditition
                varying_operator = False, # Do operators vary in x
                dynamic_predictor = True,
                plot_hook = None, n_plots = 3,  # not used anymore
                tollerance = 0.04, ):
    """ Perform Split step integration of nl Schroedinger eq
    
    :arg A0: initial array (len should be a power of 2)
    
    :arg z_array: (must contains 0 and final point. If intermediate points are given
        the integration will give the solution at that given point, and will try
        to use integration step smalle than the distance of 2 subquent z points
        
    :arg t_op: Operator for time-evolution
    :arg w_op: Operator for the Fourie domain
    :arg nlin: Non-linear operator, nlin * |A|^2
    
    :arg t_nl_op: Addional operator in the form f(A, dt, z)
    :arg apod: Apodization at the boundaries
    
    :arg varying_operator: Boolean, doeas any operator vary in z
    
    :arg dynamic_predicto: def False, implement predictor for z_step
    :arg tollerance: relative error to be used to chose the dynamic z_step
    
    """
    ## Initialization
    ## Extract information from input field (n points)
    n_points = A0.shape[0]
    # w = fftfreq(npoints, dx) * 2 * pi
    A_t = A0[:] + 0.j   # Force the array to complex
    A_w = fft(A_t) * dt
    
    ## Apodization (AKA boundary conditions)
    ## TODO maki it smooth
    apod_array = ones(n_points, dtype = complex64)
    apod_array[0:n_points/50] = 0
    apod_array[-n_points/50:-1] = 0

    ## Beginning and end array
    z0 = z_array[0]
    zf = z_array[-1]
    
    delta_z = 1.*(z_array[1]-z_array[0])/4
    done_once = False

    ## Evaluate the solution with current values at delta_z step
    ## separated so that can be re-used for error prediction
    ## contains some lazy eveluation just to be CUDA-implementation ready
    ## in sense of reducing the number of function creation
    
    def f(A_t, A_w, dz=delta_z):
        
        f.w_exp = exp(-1j * delta_z/2 * w_op)
    
        if f.delta_z != dz:
            f.initF()
            f.delta_z = dz
        
        ## Dispersion (I pass)
        f.A_w = A_w * f.w_exp
        f.A_t = ifft(f.A_w) / dt        
        
        ## Constant potential term
        f.A_t = f.A_t * f.t_exp

        ## Nonlinear operator as intensity dependency
        if nlin != 0:
            f.A_t *= exp(-1j * delta_z * nlin * absolute(f.A_t)**2)
            
        ## Additional nonlinear terms as a function t_nl_op(A(t),dt,z)
        if t_nl_op != None:
            f.A_t *= exp(-1j * delta_z * t_nl_op(f.A_t, dt, z0+delta_z/2) )

        ## Apodization
        if apod:
            f.A_t *= apod_array

        f.A_w = fft(f.A_t) * dt
        
        ## Dispersion (II pass)
        f.A_w *= f.w_exp
        f.A_t = ifft(f.A_w) / dt
        
        return f.A_t[:], f.A_w[:]

    def initF():
            # Init the f function
                
            ## Extract information from the operators
            ## if it comes in a list, it must be associated
            ## to a varying potential.
            if varying_operator:
                # Verify the lenght are correct
                if len(t_op) != len(z_array):
                    raise Exception("Varying operator has wrong size") 
                f.t_exp = exp(-1j * delta_z * t_op[0])
            else:
                f.t_exp = exp(-1j * delta_z * t_op)
    
    f.initF = initF
    f.delta_z = 0
    f.A_t = ones(n_points) + 0.j
    f.A_w = ones(n_points) + 0.j
    error = tollerance
    
    print "Ready for integration"
    
    ## Loop variable init
    sol_i = 0    
    sols  = [A_t]
    iters = 0
    
    ## Integration loop
    while z0 <= zf:
        ## Cycle check
        if z0 >= z_array[sol_i]:
            #plot_hook(A_x,A_w,x,w)
            #print "dz = %.2e error=%.2f z = %.2e"%(delta_z,error,z0)
            sols.append(A_t)
            sol_i +=1
            f.initF()
                
        try:  ## Force to have steps smaller than the distance between 2 solutions
            while z0 + delta_z >= z_array[sol_i + 1]:
                delta_z /= 2.
        except:
            pass
        
        ## Dynamical correction
        while dynamic_predictor:
            A_coarse = f(A_t[:],
                         A_w[:],
                         dz = 2 * delta_z)[0]
            A_fine = f(*f(A_t[:],
                          A_w[:], delta_z),dz=delta_z)[0]
            delta = A_fine-A_coarse
            error = sqrt( trapz(delta*delta.conj())/ \
                          trapz(A_fine*A_fine.conj()))
            #print "Error : ",error, " dz :", delta_z
            if error < 2 * tollerance:
                done_once = True
                break  ## Error is less then the tollerance, proceed
            delta_z = delta_z / 2.
        
        ## Calculate next step
        A_t, A_w = f(A_t, A_w, delta_z)
        ## Update steps
        z0 += delta_z
        iters += 1
        
        # Dynamic correction to the step
        if (dynamic_predictor or not (done_once or dynamic_predictor) ):
            if error > tollerance:
                delta_z = delta_z / 1.23
            if error < 0.5/tollerance:
                delta_z = delta_z * 1.23
                
        if iters % 200 == 0:
            print "Iter %8d (to end %8d) %4.2f %%"%(iters,
                        (z_array[-1]-z0)/delta_z,
                        100.*iters/(iters+(z_array[-1]-z0)/delta_z))
                
    print "Total iterations: ", iters
    return sols

from ctypes import *
import sys
    #sys.path.append("C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v4.0\bin")
dll = windll.LoadLibrary("cufft32_40_17")

def split_step_GPU(A0, z_array,       # Array for solution points
                t_op = 0, w_op = 0, nlin = 0,  # Constant operators 
                dt = 1,           # sampling time
                t_nl_op = None,   # Additional operator f(A, dt, z)
                apod = True,      # Boundary conditition
                varying_operator = False, # Do operators vary in x
                dynamic_predictor = True,
                plot_hook = None, n_plots = 3,  # not used anymore
                tollerance = 0.04, ):
    
    import pycuda.autoinit

    from pycuda.tools import make_default_context, dtype_to_ctype
    import pycuda.gpuarray as gpuarray
    from pycuda import cumath
    from pyfft.cuda import Plan
    from pycuda.compiler import SourceModule
    from pycuda.driver import Context
    from pycuda.elementwise import get_axpbyz_kernel, get_axpbz_kernel, get_binary_op_kernel, get_elwise_kernel,ElementwiseKernel
            
    ## Initialization
    n_points = A0.shape[0]
    # w = fftfreq(npoints, dx) * 2 * pi
    A_t = A0[:] +0.j
    #A_t.dtype = complex64
    A_w = fft(A_t) * dt
    
    
    # Apodization (AK boundary conditions)
    # TODO making it smooth
    apod_array = ones(n_points, dtype = complex64)
    apod_array[0:n_points/50] = 0
    apod_array[-n_points/50:-1] = 0

    z0 = z_array[0]
    zf = z_array[-1]
    
    delta_z = 1.*(z_array[1]-z_array[0])/4
    done_once = False

    #plan = c_uint()
    #dll.cufftPlan1d(byref(plan), n_points, 0x29, 1)
    #fft_g  = lambda x, y: dll.cufftExecC2C(plan, x.ptr, y.ptr, -1)
    #ifft_g = lambda x, y: dll.cufftExecC2C(plan, x.ptr, y.ptr, 1)
    
    ## GPU modules #####
    if pycuda.autoinit.context:
        context = pycuda.autoinit.context
    else:
        context =  make_default_context()
    block = (16,1,1)
    grid  = (n_points/block[0], 1)

    ## Init GPU kernels ####
    ## fft, scale dx is included in the definition here
    plan = Plan(n_points,wait_for_finish = True, scale = dt)   
    fft_g  = lambda ain, aout: plan.execute(ain, aout,)
    ifft_g = lambda x, y: plan.execute(x, y, inverse = True)

    ## Multiplication
    prod  = ElementwiseKernel(
            "pycuda::complex<float> *x, pycuda::complex<float> *y, pycuda::complex<float> *z",
            """
            z[i] = x[i] * y[i];
            """,
            "product",
            preamble = "")
    #prod  = lambda x,y,z: prod(x,y,z, block, grid)
    
    ## Non-linearity
    nonLinear = ElementwiseKernel(
            "pycuda::complex<float> *x, pycuda::complex<float> nlin, pycuda::complex<float> *y, pycuda::complex<float> *z",
            """
            pycuda::complex<float> I_UNIT(0.,1.);
            float I = pycuda::abs(y[i]);
            z[i] = x[i] * pycuda::exp(I_UNIT * I * nlin);
            """,
            "nonLinear",
            preamble = "")
    
    ## Evaluate the solution with current values at delta_z step
    ## separated so that can be re-used for error prediction
    ## contains some lazy eveluation just to be CUDA-implementation ready
    ## and reducing the number of array creation
    
    def f(A_t, A_w, dz = delta_z):
        if f.delta_z != dz:
            f.w_exp = cumath.exp(-1j * dz/2. * w_op)
            f.t_exp = cumath.exp(-1j * dz * t_op)
            f.delta_z = dz
        
        ## Dispersion (I pass)
        f.A_t = A_t
        f.A_w = A_w
        
        #print A_w.get()[n_points/2],     
        prod(A_w, f.w_exp, A_w)
        #A_w = f.w_exp*A_w
        #print A_w.get()[n_points/2],
        ifft_g(f.A_w, f.A_t)  ## Scale factor included in fft_g
        
        
        ## Constant potential term
        prod(f.A_t, f.t_exp, f.A_t)

        ## Nonlinear operator as intensity dependency
        if nlin != 0:
            f.A_t = f.A_t * cumath.exp(-1j * delta_z * nlin * f.A_t * f.A_t.conj())
        ## Additional nonlinear terms as a function t_nl_op(A(t),dt,z)
        if t_nl_op != None:
            f.A_t = f.A_t * cumath.exp(-1j * delta_z * t_nl_op(f.A_t, dt, z0+delta_z/2) )
        ## Apodization
        if apod:
            prod(f.A_t, apod_array, f.A_t)
            
        fft_g(f.A_t, f.A_w) ## Scale factor included in fft_g
        
        ## Dispersion (II pass)
        prod(f.A_w, f.w_exp, f.A_w)
        
        ifft_g(f.A_w, f.A_t)  ## Scale factor included in fft_g
        
        
        return f.A_t, f.A_w

    ## Init the f function
    f.delta_z = 0 # The rest will be evaluated lazily

    ## Convert to GPU arrays
    f.A_t = gpuarray.to_gpu(ones(n_points, complex64))
    f.A_w = gpuarray.to_gpu(ones(n_points, complex64))
    A_t   = gpuarray.to_gpu(A_t.astype(complex64))
    A_w   = gpuarray.to_gpu(A_w.astype(complex64))
    
    
    
    apod_array  = gpuarray.to_gpu(apod_array.astype(complex64))
    if hasattr(w_op,'__len__'):
        w_op = gpuarray.to_gpu(w_op.astype(complex64))
    else:  ## Use array even if it's a single values, othewise error when updating dz
        w_op = gpuarray.to_gpu(w_op*ones(n_points).astype(complex64))
    if hasattr(t_op,'__len__'):
        t_op = gpuarray.to_gpu(t_op.astype(complex64))
    else:
        t_op = gpuarray.to_gpu(t_op*ones(n_points).astype(complex64))
    error = tollerance
    
    print "Ready for integration"
    
    ## Init loop variables
    sol_i = 0    
    sols  = [A0]
    iters = 0
    
    ## Integration loop
    while z0 <= zf:
        ## Cycle check
        if z0 >= z_array[sol_i]:
            #print "dz = %.2e error=%.2f z = %.2e"%(delta_z,error,z0)
            sols.append(A_t.get())
            sol_i +=1
            
        try:  ## Force to have steps smaller than the distance between 2 solutions
            while z0 + delta_z >= z_array[sol_i + 1]:
                delta_z /= 2.
        except:
            pass
    
        ## Dynamical correction
        while dynamic_predictor:
            A_coarse = f(gpuarray.to_gpu(A_t.get()),
                         gpuarray.to_gpu(A_w.get()),
                         dz=2*delta_z)[0].get()
            A_fine = f(*f(gpuarray.to_gpu(A_t.get()),
                          gpuarray.to_gpu(A_w.get()),
                         delta_z), dz=delta_z)[0].get()
            delta = A_fine-A_coarse
            error = sqrt( trapz(delta*delta.conj())/ \
                          trapz(A_fine*A_fine.conj()))
            #print "Error : ",error, " dz :", delta_z
            if error < 2 * tollerance:
                done_once = True
                break  ## Error is less then the tollerance, proceed
            delta_z = delta_z / 2.
        
        # update step        
        A_t, A_w = f(A_t, A_w, delta_z)
        z0 += delta_z
        iters += 1
        
        # Dynamic step (additional correction for faster convergence)
        if (dynamic_predictor or not (done_once or dynamic_predictor) ):
            if error > tollerance:
                delta_z = delta_z / 1.23
            if error < 0.5/tollerance:
                delta_z = delta_z * 1.23
                
        # Show the state of the loop every 200 loops (approx every few secs)
        if iters %200 == 0:
            print "Iter %8d (to end %8d) %4.1f %%"%(iters, 
                            (z_array[-1]-z0)/delta_z,
                            100.*iters/(iters+(z_array[-1]-z0)/delta_z))
    
    ## Integration is over
    print "Total iterations: ", iters
    ## Return array with solutions (and their ftt)
    return sols

## Helper functions

# Pulse generation
def square_pulse(t, delta_t, t0 = 0, steep = 0.01):
    """ Returns a square pulse centered of lenght dt, centered in t0
    (in respect of time_array t)
    """
    return (erf((t-(t0-delta_t/2.))/(steep*delta_t)) + erf(-(t-(t0+delta_t/2.))/(steep*delta_t)))/2

def gaussian_pulse(t, delta_t, t0 = 0, n = 1):
    """ Returns a gaussian pulse centered of lenght delta_t, centered in t0
    (in respect of time_array t)
    """
    # Gaussian Pulse
    sigma = delta_t/sqrt(8*log(2))
    return exp(-0.5*((t-t0)/sigma)**(2*n) ) #+  exp(-(t/dt)**2/2.)# * exp(1.j * dw * 300 * t )

## TODO need more work
def generate_noise(t, rms = 1.):
#    dt = t[1]-t[0]
#    n = len(t)
#    t = arange(-n/2,n/2)*dt
#    corr = exp(-(0.5*(t/rms)**2))
#    s = sqrt(fft(corr))*exp(1j*random.rand(n)*2*pi)
#    return(ifft(s).real)
    
    x,y = meshgrid(t, t)
    corrmatrix = exp(-0.5*((x-y)/rms)**2)
    pl.matshow(corrmatrix)
    c = linalg.cholesky(corrmatrix)
    return dot(random.rand(len(t)),c)
    
## Stub
def correlation(a):
    return [ sum(a*roll(a,i))/len(a) for i in xrange(len(a)) ]

## Stub
def disperd(e, dt, w):
    return ifft( fft(e)*exp( 1j * w**2 * dt*abs(dt)*(1./pi)**2))


#### Area and momentum
def normalize_pulse(a, t):
    return a/trapz(absolute(a)**2,x = t, dx = dt)

def init_pulse(delta_t,t):
    gaussian_pulse(t, delta_t)    
    
def momentum(y, x, n = 2):
    """ Computes momentum order n centered at the mean value """
    # Normalize
    norm = trapz(absolute(y),x)
    y = y / norm
    x0 = trapz(x*absolute(y),x)
    d0 = trapz( (x-x0)**2 * absolute(y),x)

    print "mean %.3e - momentum %dth order = %.3e"%(x0,n,d0)

    return d0

def disperd(e, dt, w):
    return ifft( fft(e)*exp( 1j * w**2 * dt*abs(dt)*(1./pi)**2))

## Plotting functions
def plot_fft(A, t = None, w = None):
    
    if w is None:
        npoints = A.shape[0]
        w = fftfreq(npoints) * 2 * pi
    
    A_w = fft(A)
    A_w = A_w /amax(A_w)
    
    pl.subplot(121)
    if t is not None:
        pl.plot(t,abs(A))
    else:
        pl.plot(abs(A))
    
    pl.subplot(122)
    pl.plot(w,abs(A_w))
    pl.semilogy()
    pl.ylim(0.001,2)
    
def plot_pulse(A_t,A_w,t,w, l0 = 1.550 * micr, t_zoom = pico, l_zoom = 10*nano):
        ## Fix maximum
        if 'A_max' not in plot_pulse.__dict__:
            plot_pulse.A_max = amax(A_t)
            plot_pulse.A_w_max = amax(A_w)

        w0 = 2 * pi * C_SPEED / l0

        ## Plot Time domain
        fig = pl.gcf()
        fig.add_subplot(211)
        pl.plot(t / t_zoom, absolute(A_t/plot_pulse.A_max), hold = False)
        pl.axis([amin(t) / t_zoom*0.4,amax(t) / t_zoom*0.4, 0, 1.1])
        pl.xlabel(r'$time\ (%s s)$'%units[t_zoom])

        atten_win = 0.01
        npoints = len(w)
        apod = arange(npoints)
        apod = exp(-apod/(npoints*atten_win)) + exp(-(npoints-apod)/(npoints*atten_win))
        apod = ifftshift(apod)

        ## Plot Freq domain
        fig.add_subplot(212)
        pl.plot((2 * pi * C_SPEED)/(w+w0)/micr, log10(absolute(A_w)**2/absolute(plot_pulse.A_w_max)**2) * 10, hold=False)
        #pl.plot((2 * pi * C_SPEED)/(w+w0) / micr, log10(absolute(apod)**2/absolute(amax(apod))**2 ) *10, hold=True)
        #pl.semilogy()
        pl.axis([(l0-l_zoom)/micr, (l0+l_zoom)/micr, -60, 5])
        pl.xlabel(r'$wavelength\ (\mu m)$')
        pl.ylabel(r'$spectrum (db)$')

        pl.show()
        
def animation_window(sols, other = None, xaxis = None):
    import wxmpl, wx
    class AnimatedPlot(wx.App):
        def __init__(self, **arg):                
            wx.App.__init__(self, redirect = False, **arg)
            self.timer = wx.PyTimer(self.onTimer)
             #wx.EVT_CLOSE(self, self.OnClose)
            
            self.frame = wx.Frame(None, id = wx.ID_ANY,
                                            title = wx.EmptyString, pos = wx.DefaultPosition,
                                            size = wx.Size( 500,300 ),
                                            style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
                                            
            self.panel = wxmpl.PlotPanel(self.frame, -1)
            #self.frame.Close = closing
            self.frames = sols
            self.frame_i = 0
            
            bSizer = wx.BoxSizer( wx.VERTICAL )
            bSizer.Add( self.panel, 1, wx.EXPAND |wx.ALL, 5 )

            self.m_slider = wx.Slider( self.frame, wx.ID_ANY, 0, 0, len(self.frames), wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
            bSizer.Add( self.m_slider, 0, wx.ALL|wx.EXPAND, 5 )
            self.frame.SetSizer( bSizer )
            self.frame.Layout()
            
            self.figure = self.panel.get_figure()
            if xaxis != None:
                if other != None:
                    self.figure.gca().plot(xaxis,other,"k-")
                self.line, = self.figure.gca().plot(xaxis,abs(self.frames[0]))
            else:
                if other != None:
                    self.figure.gca().plot(other,"k-")
                self.line, = self.figure.gca().plot(abs(self.frames[0]))
            self.figure.gca().set_title("Frame %4d"%self.frame_i)
            self.timer.Start(50)
            self.frame.Show()
            
        def onExit(self):
            self.timer.Destroy()       
            
        def onTimer(self):
            self.line.set_ydata(abs(self.frames[self.frame_i]))
            self.figure.gca().set_title("Frame %4d"%self.frame_i)
            self.m_slider.SetValue(self.frame_i)
            self.panel.draw()    
            self.frame_i = (self.frame_i + 1)%len(self.frames)
            #self.panel.frame
        
            
            
    AnimatedPlot().MainLoop()

def plotSolution3D(solutions):
    pl.contourf(abs(array(solutions).T), aspect = 'auto')
    #pl.contour(abs(array(solutions).T), colors = 'gray',
    #                                    aspect = 'auto',
    #                                    linewidths = 1)

#def spectrogram(e, t, filtre):
#    spectra = []
#    for t0 in linspace(min(t),max(t),50):
#        spectra.append(fft(e * gaussian_pulse(t, delta_t = filtre, t0=t0)))
#    plot
#    




def visualizer(data):
    """ Stand Alone app to analize solution
    
    data are a dictionary with
    
    :sol: solution
    
    """
    
    # Used to guarantee to use at least Wx2.8
    import wxversion
    wxversion.ensureMinimal('2.8')

    import matplotlib
    matplotlib.use('WXAgg')

    from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
    from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as Toolbar
    from matplotlib.figure import Figure

    import wx
    import wx.xrc as xrc

    class PlotPanel(wx.Panel):
        """ Inspired by example "embedding_in_wx3.py"
        
        Bare matplotlib panel
        """
        def __init__(self, parent):
            wx.Panel.__init__(self, parent, -1)

            self.fig = Figure((3,2))
            self.canvas = FigureCanvasWxAgg(self, -1, self.fig)
            self.toolbar = Toolbar(self.canvas) #matplotlib toolbar
            self.toolbar.Realize()
            #self.toolbar.set_active([0,1])
            
            ## Now put all into a sizer
            sizer = wx.BoxSizer(wx.VERTICAL)
            ## This way of adding to sizer allows resizing
            sizer.Add(self.canvas, 1, wx.ALL | wx.EXPAND)
            ## Best to allow the toolbar to resize!
            sizer.Add(self.toolbar, 0, wx.ALL)
            self.sizer = sizer
            self.SetSizer(sizer)
            self.Fit()

        def GetToolBar(self):
            # You will need to override GetToolBar if you are using an
            # unmanaged toolbar in your frame
            return self.toolbar

        def onEraseBackground(self, evt):
            # this is supposed to prevent redraw flicker on some X servers...
            pass
    
    class InstrumentFrame(wx.Frame):
        def __init__(self, title = "Visualizer GUI",
                           parent = None,):
                           
            ## A Frame is a top-level window
            wx.Frame.__init__(self, parent, wx.ID_ANY, title, size = (700,600))
            self.Show(True)     # Show the frame.
            
            self.stdF = wx.Font(14, wx.FONTFAMILY_DEFAULT,
                                      wx.FONTSTYLE_NORMAL,
                                      wx.FONTWEIGHT_NORMAL)
                                      
            self.buttonF = wx.Font(16, wx.FONTFAMILY_DEFAULT,
                                        wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_BOLD)
                                      
            self.SetFont( self.stdF )
            
            self.buttons = []
            
            ## Set Sizer and Automatic Layout
            ##- 4 boxes 1) 3d/contour
            ##          2) slice/animation
            ##          3) Open/save
            ##          4) parameters..
            
            self.box = wx.FlexGridSizer(2,2)
            self.box.SetFlexibleDirection(wx.BOTH)
            
            ### Info ######
            ### ==== ######
            self.info = wx.StaticText(self, label = "blah blah")
            #self.description.SetSize((300,-1))
            self.box.Add(self.info, 0, wx.ALL , border = 4)   
            
            ### 3d/contour ######
            ### ========== ######
            self.contour_plot = PlotPanel(self)
            bSizer = wx.BoxSizer( wx.VERTICAL )
            
            ## Slider to select the frame
            self.m_slider = wx.Slider( self, wx.ID_ANY, 0,
                                        0, 100,   # Size
                                        wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
            
            def onslider(evt):
                self.line.set_ydata( abs(self.data['sol'][self.m_slider.GetValue()])**2 )
                self.vline.set_xdata( [self.z[self.m_slider.GetValue()], self.z[self.m_slider.GetValue()]])
                self.contour_plot.canvas.draw()
                self.slice_plot.canvas.draw()
                
            self.Bind(wx.EVT_SCROLL, onslider, self.m_slider)
            
            bSizer.Add(self.contour_plot,  1,wx.ALL | wx.EXPAND, border = 2)
            bSizer.Add( self.m_slider, 0, wx.ALL|wx.EXPAND, border= 2 )
            
            self.box.Add(bSizer,  1,wx.ALL | wx.EXPAND, border = 2)
            
            
            
            ### Button Box ######
            ### ========== ######
            buttonbox = wx.BoxSizer(wx.VERTICAL)
            ## Load
            btn = wx.Button(self, label= "Load")
            btn.SetFont( self.buttonF )
        
            ## Bind the event
            def callbackWrap(evt):
                dlg = wx.FileDialog(None, style = wx.OPEN, wildcard = "*.mat")
                if dlg.ShowModal() == wx.ID_OK:
                    # User has selected something, get the path, set the window's title to the path
                    filename = dlg.GetPath()
                    try:
                        data = loadmat(filename, appendmat = False)
                        self.setData(data)
                    except:
                        print filename,"  - File error"

                ##v = callback()
                ##txt.SetLabel(str(v))
            
            ## Bind the event
            self.Bind(wx.EVT_BUTTON, callbackWrap, btn) 
            buttonbox.Add(btn,  0, wx.ALL | wx.EXPAND, border = 4)
            
            ## Save
            btn = wx.Button(self, label= "Save")
            btn.SetFont( self.buttonF )
        
            def callbackWrap(evt):
                dlg = wx.FileDialog(None, style = wx.SAVE, wildcard = ".mat")
                if dlg.ShowModal() == wx.ID_OK:
                    # User has selected something, get the path, set the window's title to the path
                    filename = dlg.GetPath()
                    try:
                        savemat(filename, self.data, appendmat = False)
                    except:
                        print filename,"  - File error"
            
            ## Bind the event
            self.Bind(wx.EVT_BUTTON, callbackWrap, btn) 
            buttonbox.Add(btn, 0, wx.ALL | wx.EXPAND, border = 4)
            
            self.box.Add(buttonbox)
            
            ### Slice      ######
            ### ========== ######
            self.slice_plot = PlotPanel(self)
            self.box.Add( self.slice_plot, 1, wx.EXPAND |wx.ALL, 2 )
            
            ## Flexible Grid ####
            ## ------------- ####
            self.box.AddGrowableRow(0,1)
            self.box.AddGrowableRow(1,1)
            self.box.AddGrowableCol(0,1)
            self.box.AddGrowableCol(1,3)
            self.SetSizer(self.box)
            self.Layout()
        
        def setData(self, data):
            """ Update with new data """
            self.data = data
            
            ## Data ###
            solutions = data["sol"]
            
            self.z = data.get("z", linspace(0,1, len(solutions)) ).flatten()
            t = data.get("t", linspace(0,1, len(solutions[0]))).flatten()
            w = data.get("w", linspace(-1,1, len(solutions[0]))).flatten()
            pot = data.get("pump", None)
            
            
            title = data.get("title", ["Beam propagation"])[0]
            notes = data.get("notes", [""])[0]
            date = data.get("date",[""])[0]
            
            info = "%s\n%s\n%s"%(title,date, notes)
            
            ## Notes ##
            self.info.SetLabel(info)
            
            ## Plot ###
            axis = self.contour_plot.fig.add_subplot(111)            
            axis.hold(False)
            axis.contourf(self.z,t,abs(array(solutions).T)**2, 20, aspect = 'auto')#, cmap = matplotlib.cm.autumn)
            self.vline = axis.axvline(self.z[-1], linewidth=3, color='k')
            
            
            axis = self.slice_plot.fig.add_subplot(111)            
            axis.hold(False)
            axis.plot(t,abs(array(solutions[0]))**2, label = "Start", color="grey")
            axis.hold(True)
            self.line, = axis.plot(t,abs(array(solutions[-1]))**2, label = "Final")
            if pot==None:
                axis.plot(t,abs(pot)**2, label = "Potential", color="red")
            axis.legend()
            
            ## Slider ###
            self.m_slider.SetRange(0,len(solutions)-1)
            self.m_slider.SetValue(len(solutions)-1)
            
            self.contour_plot.canvas.draw()            
            self.slice_plot.canvas.draw()
            
    app = wx.App(False)
    f = InstrumentFrame()
    f.setData(data)
    app.MainLoop()
    
## Optical analogue helper functions
def getABC(l0, disp, gamma, p, reprate, deltat):
    """
    Calculate the nonlinear parameter

    gamma   = 300.5         # effective nonlinearity [1/(W*km)]

    w0 = 2 * pi * C_SPEED / l0
    x_win = 50e-12
    npoints = 2**10

    l_prop = 1e1          # Lenght propagation

    deltat = 1 * 1e-12    # Gaussian initial spread (time)
    p = 100e-6            # average pump power [W]
    reprate = 75e6        # laser rep rate [1/s] """
    

    w0 = 2 * pi * C_SPEED / l0
    beta2  =  - disp * l0**2/(2 * PI * C_SPEED) # GV
    #gamma   = gamma / 1e3 # in MKS
    
    p0  =  p/(reprate*deltat) # Peak power
    ld = deltat*deltat/abs(beta2) # Diffraction Length

    nlinear = gamma * p0 # Non linear parameter
    lnl = abs(1/nlinear) # Non linear length


    print "Omega0 = %.2e"%w0
    print "Dispersion Length = %.2e"%ld
    print "NonLinear  Length = %.2e"%lnl

    return (nlinear,beta2,0)

def nlin_prop():
    """

    l0    - Lambda Carrier [m]
    disp  - dispersion [ps/(nm * km)]
    gamma - effective nonlinearity

    """

    disp = -0.285
    gamma = 300.5
    l0 =  1535e-9

    disp   =    disp * 1e-12 / ( 1e-9 * 1e3 ) # in MKS
    beta2  =  - disp * l0**2/(2 * PI * C_SPEED) # GV

    #gamma   = 300.5         # effective nonlinearity [1/(W*km)]
    gamma   = gamma / 1e3 # in MKS

    w0 = 2 * pi * C_SPEED / l0
    x_win = 50e-12
    npoints = 2**10

    l_prop = 1e1          # Lenght propagation

    deltat = 1 * 1e-12    # Gaussian initial spread (time)
    p = 100e-6            # average pump power [W]
    reprate = 75e6        # laser rep rate [1/s]

    p0  =  p/(reprate*deltat) # Peak power
    ld = deltat*deltat/abs(beta2) # Diffraction Length

    nlinear = gamma * p0 # Non linear parameter
    lnl = abs(1/nlinear) # Non linear length

    t = linspace(-x_win/2., x_win/2., npoints)
    field = init_pulse(deltat, t) + 0.01 * init_pulse(deltat, t) * exp( 1j * w0*0.4 * t)

    nl_schroedinger(field ,t, a = nlinear, b = beta2, c = 0, t_max = l_prop,
                n_cycles = 20000, plot_hook = plot_pulse, n_plots = 50)
    #pl.figure()
    #nl_schroedinger2(field,t, a, b, c, t = linspace(0,l_prop, 20000),
    #            plot_hook = plot_pulse, n_plots = 100)

def cavity():
    def plot_pulse(A_t,A_w,t,w):
        if 'A_max' not in plot_pulse.__dict__:
            plot_pulse.A_max = amax(A_t)
            plot_pulse.A_w_max = amax(A_w)
        ## Plot Time domain
        pl.subplot(211)
        pl.plot(t, absolute(A_t/plot_pulse.A_max))
        pl.axis([amin(t),amax(t), 0, 1.1])

        ## Plot Freq domain
        pl.subplot(212)
        pl.plot((w, log(absolute(A_w)**2/absolute(plot_pulse.A_w_max)**2))/0.1)
        #pl.semilogy()
        pl.axis([amin(w), amax(w), 1e-8, 3])
        pl.xlabel('wavelength [microns]')
        pl.ylabel('spectrum [db]')


    t = linspace(-5,5,1024)
    a = init_pulse(1, t)# + 0.01 * init_pulse(deltat, t) * exp( 1j * w0*0.4 * t)

    a = nl_schroedinger(a,t,a = 1,b = 1, c = 0, t_max = 5,
                n_cycles = 10000)
    a = nl_schroedinger(a[0], t, a = 0, b = 0.3, c = 0, t_max = 5,
                n_cycles = 10000)
    a = nl_schroedinger(a[0], t, a = 1,b = -0.3, c = 0, t_max = 5,
                n_cycles = 10000, plot_hook = plot_pulse)

## Unit Test
import unittest
import time
class SplitStepCPUGPU(unittest.TestCase):
    """ Test the split_step and compare between GPU and CPU implementation
    
    """
    def setUp(self):
        self.z = linspace(0,3,20)
        self.t = linspace(-1,1,2**10)
        self.A = gaussian_pulse(self.t,0.3,0.1)
    
    
    def runTimeSplit(self,options):
        s1 = split_step(self.A, self.z, **options)[-1]
        s2 = split_step_GPU(self.A, self.z, **options)[-1]
        
        assert  sum(abs(s1-s2)**2)/sum(abs(s2)**2) < 0.05
    
    
    def test_functions_call(self):
        gaussian_pulse(self.t, 0.3, 0.1)
        gaussian_pulse(self.t, 0.3, n = 10)
        square_pulse(self.t,0.3,0.1)
        
    def test_timesplit(self):
        w = fftfreq(len(self.t),2./len(self.t))*2*pi
        options = { 't_op': 1*self.A**2,
                    'w_op': 0.01*w**2,
                    'nlin': 1,
                    'dynamic_predictor': True,
                    'apod': True   }
        self.runTimeSplit(options)
            
    def test_timesplit_nl(self):
        options = { 't_op': 0.0,
                    'w_op': 0.0,
                    'nlin': 10,
                    'dynamic_predictor': True,
                       }
        self.runTimeSplit(options)
        
    def test_timesplit_disp(self):
        w = fftfreq(len(self.t),2./len(self.t))*2*pi
        options = { 't_op': 0.0,
                    'w_op': 0.01*w**2,
                    'nlin': 0,
                    'dynamic_predictor': True,
                       }
                    
        self.runTimeSplit(options)
    
    def test_timesplit_time(self):
        w = fftfreq(len(self.t),2./len(self.t))*2*pi
        
        options = { 't_op': 1*self.A**2,
                    'w_op': 0.0,
                    'nlin': 0,
                    'dynamic_predictor': True,
                       }
                    
        self.runTimeSplit(options)



if __name__ == '__main__':
    unittest.main(verbosity = 2)
    
    
    