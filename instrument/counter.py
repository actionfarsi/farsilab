"""
Counts edges for a given time

"""

from freqtask import FreqTask
from time import clock,sleep
from matplotlib.pylab import *

## Parameters
channels = [2,4] # Channels to measure
time_d  = 60      # Duration of acquisition in seconds

tasks = [ FreqTask(ch, 100e3, count= True, debug = True) for ch in channels ]
counts_t = [ 0 for ch in channels ]
counts_0 = counts_t[:]

tic = clock()
while True:
    counts_r = [ task.read(1) for task in tasks ]
    print counts_r
    counts_t = [ counts_t[i] + (counts_r[i]-counts_0[i]) for i in range(len(channels))]
    counts_0 = counts_r[:]
    
    s = "|".join([ " CH%d %8d "%(channels[i], counts_t[i]) for i in range(len(channels))])
    print s,
    sleep(0.3)
    if clock()-tic > time_d: break
    print "time remaining %3.0f"%(time_d-(clock()-tic))

input_raw()