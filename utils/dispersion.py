""" Dispersion from Rings Transmission Spectra

"""

from numpy import *
from scipy.ndimage import label, minimum_position
from matplotlib import pylab as pl

C = 3e8

def load_spectrum(file):
    """ Load spectrum
    
    
    filter from lowfreq noise"""
    try:
        full_spectrum = loadtxt(file+".txt")
        return full_spectrum
    except:
        full_spectrum = load(file+".npy")
        return full_spectrum

def label1d(input):
    """ Isolate and tag continuous non-zeros elements
    
    i.e. scipy.ndimage.labels
    """
    labels = zeros(asarray(input).shape)
    i = 0
    labeling = False
    for x in xrange(len(labels)):
        if labeling:
            if input[x] == 0:
                labeling = False
            else:
                labels[x] = i
        else:
            if input[x] == 0:
                pass
            else:
                labeling = True
                i += 1
                labels[x] = i      
    return labels,i
    
    
def find_minima(spectrum, threshold = None, window = 7000):
    """ Find the minima
    
    using adaptive threshold until they repeat in regular way
    """
    
    decimation = 50 # For faster approximate search of the peak
    #window = 7000   # Half size of the fitting window
    
    if threshold == None:
        limits = min(spectrum),max(spectrum)
        threshold = (limits[1]-limits[0])/4*1.6
    
    d_spectrum = spectrum[::decimation]
        
    labels,n = label1d(d_spectrum < threshold)
    locations = []
    for i in xrange(1,n):
        locations.append(argmin(d_spectrum*(labels!=i) + 20))
        
    peaks = (array(locations)+1) * decimation
    
    better_mins=[]
    for x in peaks:
        try:
            better_mins.append(x-window+ fit_minima(spectrum[x-window:x+window], 'poly'))
        except:
            pass
        
    return unique(better_mins)

def fit_minima(spectrum, mode = 'poly'):
    """ Find minima of a spectrum dip
    
    modes are 
    'min': position of minimum value
    'poly': quadratic fit
    """
    if mode == 'min':
        return argmin(spectrum)
    if mode == 'poly':
        xmin = argmin(spectrum)
        x =  arange(180)
        p = polyfit(x, spectrum[xmin-90:xmin+90], 2)
        x0 = - p[1]/(2*p[0])
        ## TODO Add Lorentz fit
        #pl.plot(spectrum)
        #pl.plot(x+xmin-100,  p[2]+x*p[1]+x**2 *p[0])
        
        #pl.plot(x0+xmin-100, 0.05,'o')
        #pl.ylim(0,0.1)
        #pl.show()
        return x0+xmin-90

def disp_w(n, l):
    beta = (2 * pi / n * C / l)[::-1]
    o = (2 * pi * C / l)[::-1]
    
    beta_i = interpolate.splrep(beta, o, k= 5)
    return (o,interpolate.splev(o,beta_i, der = 2))

def beta2(disp, l):
    return  - disp * l**2/(2 * pi * C)

        
def test():
    s = load_spectrum('ring28yael')
    w = linspace(1510e-9,1600e-9,len(s))
    
    
    
    mins = find_minima(s)
    w_p = 1510e-9 + array(mins) * 90.e-9/len(w)
    ww = 2 * pi * 3e8/w_p   
    
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
    
def expGeneratePeaks():
    files = [("ring12",0.15),
             ("ring12bis",0.12),
             ("ring13",0.25),
             ("ring13bis",0.18),
             ("ring14",0.24),
             ("ring15",0.18),
             ("ring27yael",0.12),
             ("ring28yael",0.025),
             ("ring28yael2",0.07),]
    
    for f in files:
        s = load_spectrum(f[0])
        w = linspace(1510e-9,1600e-9,len(s))
        mins = find_minima(s,f[1])
        w_p = 1510e-9 + array(mins) * 90.e-9/len(w)
        # pl.figure()
        # pl.plot(w,s)
        # pl.plot(w_p,s[mins],'o')
        # pl.title(f)
        # pl.show()
        savetxt(f[0]+'-p.txt', w_p)
    #pl.show()

def extractBeta2():
    files = [("ring12",0.15),
             ("ring12bis",0.12),
             ("ring13",0.25),
             ("ring13bis",0.18),
             ("ring14",0.24),
             ("ring15",0.18),
             ("ring27yael",0.12),
             ("ring28yael",0.025),
             ("ring28yael2",0.07),]
             
    for f in files:
        print f[0]
        w_p = unique(loadtxt(f[0]+'-p.txt'))
        
        #pl.plot(w_p, ones(len(w_p)), 'o')
        ww = 2 * pi * 3e8/w_p   
        
        
        beta2 = -1./(112e-6*2*pi)*diff(diff(ww))/(diff(ww)[:-1]**3)
        p = polyfit(w_p[1:-1], beta2, 1)
        
        pl.figure()
        pl.plot(w_p[1:-1]*1e6, beta2)
        pl.plot(w_p[1:-1]*1e6, p[1]+ p[0]*w_p[1:-1], label="q=%.2e"%p[0])
        pl.legend()
        
        pl.title(f[0])
        pl.show()
    
def special():
        f1 = "ring28yael"
        f2 = "ring28yael2"
        w_p = unique(loadtxt(f1+'-p.txt'))
        w_p2 = unique(loadtxt(f2+'-p.txt'))
        ww = 2 * pi * 3e8/w_p
        ww2 = 2 * pi * 3e8/w_p2
        
        beta2 = -1./(112e-6*2*pi)*diff(diff(ww))/(diff(ww)[:-1]**3)
        #p = polyfit(w_p[1:-1], beta2, 1)
        beta22 = -1./(112e-6*2*pi)*diff(diff(ww))/(diff(ww)[:-1]**3)
        #p = polyfit(w_p[1:-1], beta2, 1)
        
        pl.subplot(211)
        pl.plot(w_p)
        pl.plot(w_p2)
        pl.subplot(212)
        pl.plot(diff(w_p))
        pl.plot(diff(w_p2))
        pl.subplot(313)
        pl.plot(w_p[1:-1]*1e6, beta2*1e24)
        pl.plot(w_p[1:-1]*1e6, beta22*1e24)
        #pl.plot(w_p[1:-1]*1e6, p[1]+ p[0]*w_p[1:-1], label="q=%.2e"%p[0])
        pl.show()

dataplot = array([[1511.8290999999997, 2.17765524209419], 
     [1513.3862000000001, 10.678119494629788], 
     [1514.947, -13.550734670402475], [1516.5104000000001, 
      -2.829417700813818], [1518.0769000000005, 9.991156803814016], 
     [1519.6471, 16.19421778794016], [1521.2213000000002, 
      -27.272443244474527], [1522.7975000000001, 17.90891390214846], 
     [1524.3778000000004, -3.9404982532261372], [1525.9612000000002, 
      -21.300206238564073], [1527.5469, 23.616316819572642], 
     [1529.1370000000002, 14.655893631147485], [1530.7311000000002, 
      -26.123440043210508], [1532.3273, 7.827081826287114], 
     [1533.9272, 3.3040848794977533], [1535.5306000000003, 
      -5.413368296503639], [1537.1370999999997, -11.949777620427849], 
     [1538.7464000000002, 6.903697350136288], [1540.3594000000003, 
      8.73945178372568], [1541.9762, -12.55619337124013], 
     [1543.5958, -6.419255394795827], [1545.2184999999997, 
      5.966224826554063], [1546.8449000000003, 7.790009971324561], 
     [1548.4751, -0.827869551163275], [1550.1087, -1.0493834163868274], 
     [1551.7457000000002, -1.2700079468814176], [1553.3861000000002, 
      6.797153850058591], [1555.0303, -14.139085163411535], 
     [1556.6772999999998, -1.9098371689878182], 
     [1558.3277, 8.174239751662723], [1559.9819999999997, 
      -4.439580683691432], [1561.6396, -10.795748117210222], 
     [1563.3002, 13.613528527737422], [1564.9649999999997, 
      -19.38662626368043], [1566.6324, 41.69565582891367], 
     [1568.3054, -34.02584361139783], [1569.9803000000002, 
      6.471836258821391], [1571.6591000000005, 2.143343832213203], 
     [1573.3416000000002, -4.165825180822651], 
     [1575.0275, 11.760746220707427], [1576.7176, -2.634903627801233], 
     [1578.4112000000002, -20.913626915448543], [1580.1074000000003, 
      9.037662765303617], [1581.8077000000005, 8.736382424163958], 
     [1583.5121, -21.477629771720537], [1585.2191000000003, 
      14.27127223689176], [1586.9305000000002, 61.61116933853038], 
     [1588.6486999999997, -83.3095861264017]])

        
#expGeneratePeaks()        
#extractBeta2()
special()
    

