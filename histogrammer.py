
from numpy import *
from matplotlib import pylab as pl
import sys




if __name__ == "__main__":
    
    filename = sys.argv[1]
    try:
        d1,d2 = loadtxt(filename)
        d1 = d2-d1
    except:
        d1 = loadtxt(filename)
        
    range = (-80,80)
    bins = 100

    hist, bin_edges = histogram(d1, bins, range)
    pl.bar(bin_edges[:-1], hist )
    hist, bin_edges = histogram(d1, bins*3, range)
    pl.plot(bin_edges[:-1], hist*3, 'g')
    hist, bin_edges = histogram(d1, bins*5, range)
    pl.plot(bin_edges[:-1], hist*5, 'b')
    hist, bin_edges = histogram(d1, bins*100, range)
    pl.plot(bin_edges[:-1], hist*100, 'k')
    hist, bin_edges = histogram(d1, bins*25, range)
    pl.plot(bin_edges[:-1], hist*25, 'r')
    
    
    pl.show()