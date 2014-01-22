### Extract datafrom TT log files

from numpy import *
from matplotlib import pylab as pl

import sys

def convertLog(filename):
    hist = {}
    start_time = 0
    stop_time = 10  
    # loop over log entries
    with open(filename) as stream:
        while True:
            ## first line contains time info
            try:
                line = stream.readline()
                
                    
                entry_t = line.split()[-1]
            except:
                break
            entry_t = [int(s) for s in entry_t.split(':')]
            ## in seconds
            entry_t = entry_t[2]+entry_t[1]*60+entry_t[0]*3600
            if start_time == 0:
                start_time = entry_t
            else:
                stop_time = entry_t
            
            ## second line knows if "Recent' or 'Global'. Trash the former
            line = stream.readline()
            while ('Recent Freq. Table' not in line):
                line = stream.readline()
            
            
            ## now sequence of histogram bins (not consecutive)
            context = 'histogram'
            while context == 'histogram':
                l = stream.readline().split(':')
                try:
                    key = int(l[0])
                    value = int(l[-1])
                    #print (key, value)
                    if key in hist:
                        hist[key] += value
                    else:
                        hist[key] = value
                except ValueError:
                    #print "Value error", l
                    context = 'other'
             
            line = stream.readline()             
            while (line[0] is not "-") and (line is not " ") :
                    line = stream.readline()
            
            
            

    ## Convert the dictionary to list of delay (ns) and counts/s    
    hist = array(hist.items())
    t = array(hist[:,0])
    v = array(hist[:,1])
  
    t = t * 0.082  ## Bin size
    v = 1. * v / (stop_time-start_time)  ## Counts per sec
    print (stop_time-start_time)

    return t,v

if __name__ == "__main__":
    ## work from command line/ dragdrop
    #filename = sys.argv[1]
    for filename in sys.argv[1:]:
        t,v = convertLog(filename)    
        savetxt( filename[:-4]+"-hist.txt", c_[t,v]) 
        ## Plot result
        pl.plot(t,v, label="Time Tagging")
    
    # data = loadtxt('concidenceTDC.txt')
    # hist, bin_edges = histogram(data, 500,(min(x),max(x)))
    # pl.plot(bin_edges[:-1]+1,1.*hist/amax(hist), 'r', linewidth = 2, label="TDC")
    # hist, bin_edges = histogram(data, 1800, (min(x),max(x)))
    # pl.plot(bin_edges[:-1]+1,1.*hist/amax(hist), '--g', linewidth = 2, label="TDC - small bins")
    # pl.legend()
    # pl.xlim(161,166)
    # pl.ylim(-0.1,1.2)
    pl.show()
    #print hist
    
    #raw_input()
