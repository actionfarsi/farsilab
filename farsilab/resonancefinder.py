""" Dispersion from Rings Transmission Spectra

"""

from numpy import *
import numpy as np
from scipy.ndimage import label, minimum_position
from matplotlib import pylab as pl

C = 3e8

from scipy.signal import savgol_filter
def oddify(x):
    if x%2==0:
        return x+1
    else: 
        return x


def rollingWindow(a, window, edge = 'copy'):
    if edge == 'copy':
        extended = zeros(a.shape[:-1] + (a.shape[-1]+window-1, ))
        extended[..., window//2-1: -window//2] = a[...]
        extended[..., :window//2+1]= a[...,0]
        extended[..., -window//2:]= a[...,-1]
        a = extended
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)


def load_spectrum(file):
    """ Load spectrum and do not worry about the format"""
    try:
        full_spectrum = loadtxt(file+".txt")
        return full_spectrum
    except: pass
    try:
        full_spectrum = loadmat(file+".mat")
        return full_spectrum
    except: pass
    try:
        full_spectrum = load(file+".npy")
        return full_spectrum
    except: 
        print("Cannot open file " + file)
        
def label1d(input):
    """ Isolate and tag continuous non-zeros elements
    
    returns an array of zeros and and integers, each integer indicating a different segment of continuous 0
    
    i.e. scipy.ndimage.labels
    """
    labels = zeros(asarray(input).shape)
    label_i = 0
    labeling = False
    
    for x in range(len(labels)):
        if labeling:
            if input[x] == 0:
                labeling = False
            else:
                labels[x] = label_i
        else:
            if input[x] == 0:
                pass
            else:
                labeling = True
                label_i += 1
                labels[x] = label_i      
    return labels, label_i
    
    
def find_minima(spectrum, threshold = None,
                window = 7000, decimation = 50):
    """ Find the minima/peak
        returns in array number
    
    window = Half size of the fitting window (in points)
    
    
    TODO using adaptive threshold until they repeat in regular way
    """

    decimation = 50 # For faster approximate search of the peak
    
    if threshold == None:  # Set a threshold at 40%
        limits = min(spectrum), max(spectrum)
        threshold = (limits[1]-limits[0])*0.4
    
    d_spectrum = spectrum[::decimation]
        
    labels, n_labels = label1d(d_spectrum < threshold)
    locations = []
    for i in range(1,n_labels):
        locations.append(argmin(d_spectrum*(labels!=i) + 20))
        
    approx_peaks = (array(locations)+1) * decimation
    
    fitted_peaks=[]
    for x in approx_peaks:
        try:
            fitted_peaks.append(x-window+fit_minima(spectrum[x-window:x+window], 'poly'))
        except: # In case the minima is too close to the edge
            pass
        
    return unique(fitted_peaks) ## Using unique to avoid cases where two peaks appear as one (e.g. when TE and TM modes are close)

def fit_minima(spectrum, mode = 'poly', fit_win = 90):
    """ Find minima of a spectrum dip
    
    modes are 
    'min': position of minimum value
    'poly': quadratic fit
    """
    if mode == 'min':
        return argmin(spectrum)
    if mode == 'poly':
        xmin = argmin(spectrum)
        x =  arange(2 * fit_win)
        p = polyfit(x, spectrum[xmin-fit_win:xmin+fit_win], 2)
        x0 = - p[1]/(2*p[0])
        ## TODO Add Lorentz fit
        return x0+xmin-fit_win
    if mode == 'lorenz':
        raise Exception("Lorenzian fit not implemented")
        
    raise Exception("fit mode not specified")	

def find_peaks(data, win_size = 15, threshold = 3):
    d1 = savgol_filter(diff(data/average(data)),win_size,3)
    d2 = diff(d1)
    thr = std(d2)*threshold

    th_d2 = d2*(d2>thr)

    labels, n_labels = label1d(th_d2)
    locations = [ where(labels==i)[0] for i in range(1,n_labels+1) ]
    locations = array([ (l[0]+l[-1])//2 for l in locations ])
    return locations
    
    
def find_resonances(wl, data, threshold = 0.8, dl_win = 2e-3, block = 5000):
    
    dw = (wl[1]-wl[0])
    
    win_size = oddify(int(dl_win/dw))

    locs = concatenate([find_peaks(data[x*block:(x+1)*block],win_size,threshold)+x*block \
                        for x in range(data.shape[0]//block)])
    locs = locs.astype(int64)

    w_p = wl[0] + array(locs) * (wl[-1]-wl[0])/len(wl)
    
    ## remove duplicates
    a, i = unique(around(w_p, 2), return_index = True)
    
    
    return w_p[i]
    
### Dispersion Helper
def disp_w(n, l):
    beta = (2 * pi / n * C / l)[::-1]
    o = (2 * pi * C / l)[::-1]
    
    beta_i = interpolate.splrep(beta, o, k= 5)
    return (o,interpolate.splev(o,beta_i, der = 2))

def beta2(disp, l):
    return  - disp * l**2/(2 * pi * C)

        
def test():
	## Load files
    s = load_spectrum('ring28yael')
    w = linspace(1510e-9,1600e-9,len(s))
    
	## Process
    mins = find_minima(s)
    w_p = 1510e-9 + array(mins) * 90.e-9/len(w)
    ww = 2 * pi * 3e8/w_p   
    
	## Plot
    pl.plot(w,s)
    pl.plot(w_p,s[mins],'o')
    pl.show()
    
    beta2 = -1./(112e-6*2*pi)*diff(diff(ww))/(diff(ww)[:-1]**3)
    p = polyfit(w_p[1:-1], beta2, 1)
    
    savetxt('ring28yael-p.txt', w_p)
    
    pl.subplot(211)
    pl.plot(w,s)
    pl.plot(w_p,s[mins],'o')
    
    pl.subplot(212)
    pl.plot(w_p[1:-1]*1e6, beta2)
    pl.plot(w_p[1:-1]*1e6, p[1]+ p[0]*w_p[1:-1], label="q=%.2e"%p[0])
    pl.legend()
        
    pl.show()
