"""
 Measures and averages on some time
 ch2, ch4, ch6
 
"""

## Frequency counter
from freqtask import FreqTask
from numpy import *
import sys, os, time

## Echo server program 
# To connect from outside
import socket
sys.path.append('E:\Utilities')
import instserver
server = instserver.server()
    
## Parameters
wait = 1       # measurement time
ch  = [2,4,6]  # channel to acquire  (max 4)
n_aver = 10    # sample to average

## Initialization

# complicate initialization because of threaded measurement
def rolldata(x,i):
    (dats[i])[1:] = (dats[i])[:-1]
    (dats[i])[0] = x
    
calls = [ lambda x: rolldata(x,0),
          lambda x: rolldata(x,1),
          lambda x: rolldata(x,2),
          lambda x: rolldata(x,2)]

ts = [FreqTask(c,wait) for c in ch]          # Create a task for each channel
dats  = [zeros(n_aver) for c in xrange(ch)]  # Create the buffer for previus measurement
for i in xrange(len(ch)):                    
    ts[i].thread_read(calls[i])              # Start the measurement on different threads

step = 0

while True:                              # Never stop the measurement
        step = step + 1
        # print "It %4d"%step,           # Remove comment to have visual feedback of measurement (for long wait times)
        for i in range(7):
            time.sleep(1.* wait/7)
            #print '.',
        #print ""
        s = '|'.join([" CH%d: %6.1f (%6.3f) "%(ch[k],(dats[k])[0],average(dats[k])) for k in xrange(len(ch)) ])
        print s
        server.log = s                   # For connecting from outside
        