## Data analysis helper

import lmfit
from numpy import *
from scipy import interpolate

from matplotlib.pylab import *
from .log_conversion import convert_log, rebin

from scipy.stats import poisson, norm

## Basic helper
span = lambda t,x1,x2 : logical_and(t>=x1, t<=x2)

def movingAverage(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def rollingWindow(a, window, edge = 'copy'):
    if edge == 'copy':
        extended = zeros(a.shape[:-1] + (a.shape[-1]+window-1, ))
        extended[..., window/2.-1: -window/2.] = a[...]
        extended[..., :window/2.+1]= a[...,0]
        extended[..., -window/2.:]= a[...,-1]
        a = extended
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

def rollingAverage(a,win_size=10):
    return average(rollingWindow(a, win_size), -1)
    
## Log file analyser
def integrateLog(log_data, ranges,
    normalized = True, sigmas = False, **kwg): 
    """ """
    if isinstance(log_data, str):
        log_data = convert_log(log_data, average = not sigmas, **kwg)
    if sigmas:    
        t,(n,h) = log_data
    else:
        t,h = log_data
        
    ## Ranges could be a list or
    #ranges = reshape(ranges,size/2, 2)
    out = []
    sig = []
    for r in ranges:
        s_span = span(t,r[0],r[1])
        s_norm = sum(s_span) if normalized else 1.
        
        if sigmas:
            s_sum  = 1.*sum(h[:,s_span],1)/s_norm
        else:
            s_sum  = 1.*sum(h[s_span])/s_norm
        if sigmas:
            sig.append(std(s_sum))
            s_sum = average(s_sum)
        out.append(s_sum)
    
    if sigmas:
        return array(out), array(sig)
    else:
        return array(out)

def loadTimeLog(time_file):
    """ Load a log file
    
    it's a data file with first two entry of each line are time formatted strings
    
    returns
    array (n) time-tag in seconds from the beginning of the month
    array (n*x) of data for each line converted to float"""
    
    in_file = open(time_file)
    log_time, log_cols = [],[]
    for l in in_file.readlines():
        day, hour, cols  = l.split()[0], l.split()[1], l.split()[2:]
        d = int(day.split('-')[1])*60*60*24+int(hour.split(':')[0])*60*60 + int(hour.split(':')[1])*60 + int(hour.split(':')[2])
        if d in log_time:
            continue
        log_time.append(d)
        log_cols.append(r_[ [float(c) for c in cols] ])
    log_cols = array(log_cols).T
    return array(log_time), log_cols

def interpolateTimeLogFile(time_file, scan=False, n_average = 3):
    """ Return values every second (t assumed to be in seconds)
    if scan == True, for monitoring a noisy log (i.e. pump power or temp)
    if scan == False, for scans where parameter changes at fix intervals"""
    
    t, values = loadTimeLog(time_file)
    if scan:
        delta_t = floor(t[1]) - floor(t[0])  ## Scan has generally fixed time at the same value.
        new_t = arange(t[0],t[-1]+delta_t+1)
        new_values = [ ravel(c_[[v for i in range(delta_t)]].T) for v in values ]
    else:
        new_t = arange(floor(t[0]),floor(t[-1])+1)
        new_values = [interpolate.interp1d(movingAverage(t, n_average),
                                           movingAverage(v, n_average))(new_t) for v in values ]
    
def selectMask(scan_log, h_log, n = 10):
    """ Selects n elements from h_log
        for each scan line
        
        if n is negative, skip first n and keep the rest
    
    """
    ## Find the log entries in both h_log and scan_log
    entries = intersect1d(scan_log, h_log)
    ## Find the first occurrence
    #change_log = array([where(t == array(h_log))[0][0] for t in entries])
    
    extended_scan_log = []
    for k in range(n):
        extended_scan_log = hstack( (extended_scan_log, scan_log + k) )
    ## Find occurrences
    log_mask = in1d(h_log, extended_scan_log)
    scan_log_mask = in1d(extended_scan_log, h_log)
    
    if sum(log_mask) != len(extended_scan_log):
        print('Skipping scan_log entries N =', sum(logical_not(in1d(extended_scan_log, h_log))))
        
    
    #log_mask = zeros(len(h_log)) * False
    #for k in xrange(n):
    #    log_mask[change_log+k] = True
        
    #log_mask = log_mask == True
    return log_mask, scan_log_mask


## Generic extractors
def extractManualScan(scan_file, folder, col = 1,
                      ranges = None,  **kwg):
    """ Parameter is varied each step and different log files are acquired 
    if ranges, it integrates for each range and returns integral and sigma
    """
    scans = loadtxt(scan_file, skiprows=1).T
    
    p = scans[0]  ## Parameter
    logs = scans[col] ## Generally are 2 alice and bob, but could be more
    
    if ranges is None:
        return #convert_log(folder + '%d.txt'%i, ranges), average = not sigmas, **kwg)
    
    values = []
    sigmas = []
   
    v = array([integrateLog(folder + '%d.txt'%i, ranges, sigmas = True) for i in logs ])
    vs = [ v[:,:,i].T for i in range(len(ranges))]
    
    return p, vs
    
def extractTimeScan(time_file, log_data,
                    ranges = None,
                    n = 3, uniform_binning = True, **kwg):
                    
    """ Parameter is changed and the value is logged, while a single histogram is continuously recorded (every 1 second) """
    time_log, params = loadTimeLog(time_file)
    
    ## if time log every second, make sure there is only one entry per second
    ##if n == 1:
        
    
    if isinstance(log_data,str):
        log_data = convert_log(log_data,
                              average = False,
                              uniform_binning = uniform_binning, **kwg)
    
    
    h_t,(h_log,h) = log_data
    
    log_mask, scan_log_mask = selectMask(time_log, h_log, n)
    params_log = ravel(c_[[params[0] for i in range(n)]].T)
    
    params_log = params_log[scan_log_mask]
    h = h[log_mask]
    ## if ranges = None, just return the logs
    return params_log, (h_t if uniform_binning else (h_t[log_mask]), h)
    
    ## Now integrate the log entry
    values = []
    for i,p in enumerate(params_log):   
        t = h_t if uniform_binning else (h_t[log_mask])[i]
        values.append(integrateLog( (t,h[i]), ranges ))
        
    return params_log, array(values).T
    
## Experiments
def extractRamsey(time_file, log_file,
                  range_s, range_bkg = None,
                  n = 3, debug = False, **kwg):
                  
    log_data = convert_log(log_file,
                           average = False,
                           uniform_binning = True, **kwg)
    h_t, (h_log, h) = log_data
    
    if debug:
        figure()
        subplot(211)
        plot(h_t, h[0])
        axvspan(range_s[0],range_s[1], alpha = 0.3)

    pos, (signal,) = extractTimeScan(time_file, log_data, (range_s,), n=n)
    signal = sum(reshape(signal, (len(signal)/n,n)),1)
    pos = average(reshape(pos, (len(pos)/n,n)),1)
    
    if debug:
        subplot(212)
        plot(pos, signal)

    return pos, signal

def processLogFile(file_name, limits,
                   average = True):
    if average:
        t_a, h_a = convert_log(file_name, average = True,
            time_bins=True, limits = True, uniform_binning = True)
        savetxt( c_[t_a, h_a], file_name[:-4] + '_average.txt')
    if time:
        t_a, h_a = convert_log(file_name, average = False,
            limits = True, uniform_binning = False)
        savetxt( c_[t_a, h_a], file_name[:-4] + '_time.txt')
    
def loadG2files(file_a, file_b, file_c, limits =(-1e9,1e9), save = True):
    unif_binning = True
    t_a,h_a = convert_log(file_a, average = True, uniform_binning=unif_binning, count_rate= True, time_bins=True, limits = limits)
    t_b,h_b = convert_log(file_b, average = True, uniform_binning=unif_binning, count_rate= True, time_bins=True, limits = limits)
    t_c,h_c,n_c = convert_log(file_c, average = True, uniform_binning=unif_binning, count_rate= False, time_bins=True, limits = (-1e5,1e5))
    return (t_a, h_a), (t_b, h_b), (t_c,h_c,n_c)

def extractG2(file_names=None, log_data = None,
              count_rate = 110000, hand_dt = 0,
              dark_count_files = None, ranges = False,
              dc_rate=1e5, cc_step=1, dark_count_dt = 0,
              g2_dt = 1.1, fit_m = 'gaussian', fix_x0 = False,
              savefile = None, plot= False, bayes = False,
              fit_range = (-20,20), fix_g = False):
    
    bin_time = 0.082
    
    if ranges is False and dark_count_files == None:
        unif_binning = True
    else:
        unif_binning = False
    
    
    ## loading data
    if log_data is not None:
        (t_a, h_a), (t_b, h_b), (t_c,h_c,n_c) = log_data
    elif file_names is not None:
        (t_a, h_a), (t_b, h_b), (t_c,h_c,n_c) = loadG2files(*file_names)
    else:
        raise Exception("Missing data")
       
    bin_size = t_a[1]-t_a[0]

    if dark_count_files:
        if isinstance(dark_count_files[0],str):
            t_dca,h_dca = convert_log(dark_count_files[0], average = True, uniform_binning=True, count_rate= True, time_bins=True)
            t_dcb,h_dcb = convert_log(dark_count_files[1], average = True, uniform_binning=True, count_rate= True, time_bins=True)
        else:
            t_dca,h_dca = dark_count_files[0]
            t_dcb,h_dcb = dark_count_files[1]
            
        dark_bin_size = t_dca[1]-t_dca[0]
        if dark_bin_size < bin_size:
            h_dca = h_dca[::2]+h_dca[1::2]
            h_dcb = h_dcb[::2]+h_dcb[1::2]
            t_dca = t_dca[::2]
            t_dcb = t_dcb[::2]
            print("Dark Counts has different binsize")
        if dark_bin_size > bin_size:
            h_dca = reshape(c_[h_dca, h_dca], (len(h_dca)*2))
            h_dcb = reshape(c_[h_dcb, h_dcb], (len(h_dcb)*2))
            t_dca = reshape(c_[t_dca, t_dca+dark_bin_size/2], (len(t_dca)*2))
            t_dcb = reshape(c_[t_dcb, t_dcb+dark_bin_size/2], (len(t_dcb)*2))
            print("Dark Counts has different binsize")
            
        ## If dark counts, range can be extracted from them
        #ranges = (t_dca[0], t_dca[-1]), (t_dcb[0],t_dcb[-1])
        ## Normalize to countrate level
        h_dca *= 1. * count_rate/dc_rate
        h_dcb *= 1. * count_rate/dc_rate
        
        dark_bin_size = t_dca[1]-t_dca[0]
        
        t_dca = t_dca + int(dark_count_dt/bin_time/dark_bin_size)*dark_bin_size
        t_dcb = t_dcb + int(dark_count_dt/bin_time/dark_bin_size)*dark_bin_size
        
        
        print(bin_size, dark_bin_size)    
        
    
    if ranges:
        h_a = h_a[span(t_a, ranges[0][0], ranges[0][1])]
        h_b = h_b[span(t_b, ranges[1][0], ranges[1][1])]
        #print t_a, t_dca
        #print ranges
        t_a = t_a[span(t_a, ranges[0][0], ranges[0][1])]
        t_b = t_b[span(t_b, ranges[1][0], ranges[1][1])]
    
    ## Rebin to remove the zeros
    tt_a = arange(t_a[0], t_a[-1]+1,bin_size)
    tt_b = arange(t_b[0], t_b[-1]+1,bin_size)
    
    h_a = rebin(t_a,tt_a, h_a)
    h_b = rebin(t_b,tt_b, h_b)
    
   
    
    if dark_count_files:
        h_dca = rebin(t_dca,tt_a, h_dca)
        h_dcb = rebin(t_dcb,tt_b, h_dcb)
    else:
        h_dca = 0*tt_a
        h_dcb = 0*tt_b

    r = (t_b[0]-t_a[-1]), (t_b[-1]-t_a[0])
    print(r)
    
    
    #t_cc = arange( (r[0]-r[1]+1+hand_dt),(r[1]-r[0]-1+hand_dt),2)
    c_norm = 1.*n_c/count_rate
    
    c_c= convolve(1.*h_a,h_b)[::cc_step] * c_norm
    
     # Set the limits of the correlation
    
    # Generate a new timescale for the coincidence
    t_cc = linspace( r[0],r[1], len(c_c)) + hand_dt
    
    h_c = h_c[span(t_c,r[0],r[1])]
    t_c = t_c[span(t_c,r[0],r[1])]
    
    c_c = interp(t_c, t_cc, c_c)
    
    c_noise = c_c * 0 
    if dark_count_files:
        c_n =  convolve(1.*h_dca, 1.* h_dcb)
        c_n1 = convolve(1.*h_dca, 1.* h_b)  
        c_n2 = convolve(1.*h_a,   1.* h_dcb)
        c_noise = (c_n1 + c_n2 - c_n)* c_norm

        c_noise = interp(t_c, t_cc, c_noise)
        
    
    def fit_model_gauss(x, g0 = 1 ,x0 = 85,g = 1):
        return (1+g0* where(x>x0,   exp(-(x-x0)**2/g**2),
                                    exp(-(x-x0)**2/g**2)))
    def fit_model_lor(x, g0 = 0 ,x0 = 85,g = 1):
        return (1+ g0* where(x>x0,   exp(-(x-x0)/g),
                                     exp((x-x0)/g)))
    
    if fit_m == 'gaussian': g2Fit = fit_model_gauss
    if fit_m == 'lorentz': g2Fit = fit_model_lor
    
    
    ## now t_c can be turned into ns, and centered to zero
    if amax(h_c) > amax(c_c):
        i_max = argmax(h_c)
    else:
        i_max = argmax(c_c)
    t_c = (t_c- t_c[i_max])*bin_time 
    ## Find max
    dt = 20   
    g2_h =  1.*(h_c - c_noise)/(c_c-c_noise)
    g2_h_sigma = g2_h/sqrt(h_c)
    

    ## G2 Calculation
    g2_mod = lmfit.Model(g2Fit)
    
    ps = g2_mod.make_params()
    ps['x0'].set(t_c[i_max], min = fit_range[0], max = fit_range[1])
    ps['g'].set(.65, min = 0.1)
    ps['g'].vary = not fix_g
    ps['x0'].vary = not fix_x0
    #ps['g0'].vary = False
    ps['g0'].set(g2_h[i_max]-1, min = -1)
    print(ps['g0'])
    fit_lims = span(t_c, *fit_range)
    
    fit_result = g2_mod.fit(g2_h[fit_lims], ps,
                            weights = 1./g2_h_sigma[fit_lims]**2,
                            x = t_c[fit_lims],)

    fit_result_nodc = fit_result
    if dark_count_files:
        fit_result_nodc = g2_mod.fit(h_c[fit_lims]/c_c[fit_lims], fit_result.params,
                            weights = 1/g2_h_sigma[fit_lims],
                            x = t_c[fit_lims],)
    

    

    ## Bayesian g2
    ## Decide location and dt
    
    g2_span = span(t_c, t_c[i_max]-g2_dt/2, t_c[i_max]+g2_dt/2) 
    ## count
    h_counts = sum(h_c[g2_span])
    c_counts = sum(c_c[g2_span])
    dc_counts = sum(c_noise[g2_span])
    
    g2_sum = (h_counts-dc_counts)/(c_counts-dc_counts)
    g2_sum_sigma = g2_sum/sqrt(h_counts)
    print("Sum g2 = %.2f +/- %.2f(dt = %.2f ns)"%(g2_sum, g2_sum_sigma, dt))   
    
    g2_b, g2_b_sigma = 0, 0

    if bayes:
        # bayesian error
        p_counts = arange(h_counts*2)
        g2_counts = p_counts/c_counts
        pmf = poisson.pmf(h_counts, p_counts+dc_counts)
        pmf = pmf/sum(pmf)
        g2_b =  sum(g2_counts*pmf)

        pr_c = cumsum(pmf)
        g2_b_sigma = g2_counts[amin(where(pr_c>0.68))]
        print("Bayesian g2 = %.2f (less than %.2f)"%(g2_b,g2_b_sigma))
        
        
        #plot(p_c/c_counts, pr,'-')
        #plot(average/c_counts, poisson.pmf(h_counts,average+dc_counts)/pr_norm,'o',c=c[0])
        #fill_between(g2_counts[pr_c < 0.68], pmf[pr_c < 0.68],alpha = 0.3)
        #fill_between(g2_counts[pr_c < 0.95], pmf[pr_c < 0.95],alpha = 0.3)
        #fill_between(g2_counts[pr_c < 0.99], pmf[pr_c < 0.99],alpha = 0.3)
        #xlabel("G2")
        #xlim(0,0.15)

    fit_r = fit_result.eval(x=t_c)
    fit_r_nodc = fit_result_nodc.eval(x=t_c)
    t_c = t_c - fit_result.params['x0'].value
    g2_data = {'tt_a': tt_a, 'h_a': h_a,
                   'tt_b': tt_b, 'h_b': h_b,
                   'dark_count_files': dark_count_files, 
                   'h_dca': h_dca, 'h_dcb': h_dcb,
                   't_c': t_c, 'h_c': h_c,
                   'c_c': c_c, 'c_noise': c_noise,
                   'g2_h': g2_h, 'g2_h_sigma': g2_h_sigma,
                   'fit_r': fit_r, 'fit_r_nodc': fit_r_nodc, 
                   'g2_b': g2_b, 'g2_s': g2_sum, 'g2_f': 1+fit_result.params['g0'].value,
                   'fit_x0': fit_result.params['x0'].value,
                   'fit_g2': 1+fit_result.params['g0'].value,
                   'fit_g2_err': fit_result.params['g0'].stderr,
                   'fit_gamma': fit_result.params['g'].value,
                   'fit_gamma_err': fit_result.params['g'].stderr}

    fit_result_text =  "g2 = %.2f $\pm$ %.3f\n gamma = %.2f $\pm$ %.3f ns"%(1+fit_result.params['g0'].value,
                                                          fit_result.params['g0'].stderr,
                                                          fit_result.params['g'].value, 
                                                          fit_result.params['g'].stderr)
    if plot:
        plotG2(g2_data)
    #axvspan(t_c[i_max]-dt,t_c[i_max]+dt,alpha=0.3)    
    if savefile:
        savetxt(savefile, c_[t_c, g2_h, g2_h_sigma, fit_r],
             header = "%s\n t\t g2_h\t g2_sigma\t fit"%fit_result_text)
    return g2_data

def extractConversion(folder, scan_file,
                  signal_range, bkg_range, col=1,
                  show_histogram = False, dc_file = None):
    """ Extract from a txt scan_file, with a distinct logfile per measurement"""
    
    p, s_file, i_file = loadtxt(folder + scan_file, skiprows=1).T
    
    if col == 2:
        s_file = i_file
    s_dark = convert_log(folder + dc_file)
    s_dark = sum(s_dark[1][span(s_dark[0],signal_range[0],signal_range[1])])
    
    
    depletion = p*0
    bkg = p*0

    for pos,i in enumerate(s_file):
        t,h = convert_log(folder + '%d.txt'%s_file[pos])
        s_span = span(t,signal_range[0],signal_range[1])
        bkg_span = span(t,bkg_range[0], bkg_range[1])
        bkg_ratio = 1.*sum(s_span)/sum(bkg_span)
        
        depletion[pos] = sum(h[s_span])-s_dark
        bkg[pos] = sum(h[bkg_span])*bkg_ratio-s_dark
    
    return p, depletion, bkg


def bkg_f(x, a = 0.2, x0 = 85, y0 = .3):
    return where(x>x0, -a*(x-x0)+y0,
                          a*(x-x0)+y0)

def peak_f(x, a = 3 ,x0 = 85,g = 1):
    return where(x>x0,  a*exp(-(x-x0)/g),
                        a*exp((x-x0)/g))

bk_mod = lmfit.Model(bkg_f, prefix = 'bkg_')
peak_mod = lmfit.Model(peak_f, prefix= 'peak_')
total_mod = bk_mod + peak_mod
    
    
def extractCrossCorr(file_name, x0, rebin = 1, savefile = None):
    ## Cross correlation
    xc_t, xc_h = convert_log(file_name, average = True)
    if rebin > 1:
        xc_t = sum(reshape(xc_t[:len(xc_t)/rebin*rebin], (len(xc_t)/rebin,rebin)), axis=1)/rebin
        xc_h = sum(reshape(xc_h[:len(xc_h)/rebin*rebin], (len(xc_h)/rebin,rebin)),axis=1)/rebin
    
    ps = total_mod.make_params()
    ps['peak_x0'].set(x0)
    ps['bkg_x0'].set(x0)
    ps['peak_a'].set(amax(xc_h))
    ps['bkg_a'].set(amax(xc_h/2))
    result = total_mod.fit(xc_h, ps, x=xc_t,)
    
    
    #print(result.fit_report())
    #fit(fit_f, fit_p, xc_t, xc_h, 1, output= False)

    plot(xc_t, xc_h, label = file_name[-8:-4])
    plot(xc_t, result.best_fit,'k:')
    #print result.params
    #plot(xc_t, xc_h - bk_mod.eval(x= xc_t, **result.params),'+')
    #plot(xc_t, result.best_fit - bk_mod.eval(x=xc_t, **result.params))
    
    #plot(t_fit, bkg_f(t_fit))
    #annotate(s="Gamma = %.2f ns"%peak_p[1](), xy=(90,2.3))
    title("Crosscorrelation")
    
    dt = result.params['peak_g'].value
    dt_err= result.params['peak_g'].stderr
    bw = 1/dt/(2*pi)
    q = 193e3/bw
    
    
    data = array((xc_t,
           xc_h - bk_mod.eval(x= xc_t, **result.params),
           result.best_fit - bk_mod.eval(x=xc_t, **result.params)))
    
    pars = {'dt': dt, 'dt_err': dt_err, 'bw': bw, 'q': q}
    
    print('dt %.2f ns'%dt, 'Q = %.2e'%q)
    if savefile:
        savetxt(savefile, data, header = "%s\n t\t xcor\t fit"%repr(pars))
        
    return data, pars
    
def extractBandwith(time_file, log_file,
                        range_s, range_bkg,
                         n = 3, debug = False):
    log_data = convert_log(log_file,
                           average = False,
                           uniform_binning = True)
    h_t, (h_log, h) = log_data
    
    if debug:
        figure()
        subplot(211)
        plot(h_t, h[0])
        axvspan(range_s[0],range_s[1], alpha = 0.3)

    wl, (signal, bkg) = extractTimeScan(time_file, log_data, (range_s, range_bkg) )
    
    if debug:
        subplot(212)
        plot(wl, signal)

    return wl, signal

class Bunch(object):
    def __init__(self, adict):
        self.__dict__.update(adict)

def plotG2(g2Data):
    d = Bunch(g2Data)

    subplot(2,2,1)
    plot(d.tt_a, d.h_a)
    subplot(2,2,2)
    plot(d.tt_b, d.h_b)
    
    if d.dark_count_files:
        subplot(2,2,1)
        plot(d.tt_a, d.h_dca,"k-")
        subplot(2,2,2)
        plot(d.tt_b, d.h_dcb,"k-")
    
    
    #xlim(1800, 1820)
    
    subplot(2,2,3)
    plot(d.t_c, d.h_c-d.c_noise,'.')
    plot(d.t_c, d.c_c-d.c_noise, label = 'Normalization')
    plot(d.t_c, d.fit_r*(d.c_c-d.c_noise), 'k--', lw=3)
    
    if d.dark_count_files:
        plot(d.t_c, d.c_noise,'g--', label = 'Dark count')
    legend(fontsize = 10)
    ylim(ymin = 0)
    xlim(-25,25)
    
    subplot(2,2,4)
    errorbar(d.t_c, d.g2_h, yerr=d.g2_h_sigma,)
    plot(d.t_c, d.fit_r, 'k--',lw=2)
    if d.dark_count_files:
        plot(d.t_c, d.fit_r_nodc,'g-', label = 'Raw data', lw=2)
    xlim(-25,25)    
    #xlim(d.fit_x0-d.fit_gamma*8, d.fit_x0+d.fit_gamma*8)

    #ylim(0, d.fit_g2+1)
    ylim(ymin = -.1)
    return gca()
    #text(0.4,0.7,),fit_result_text, transform=gca().transAxes)