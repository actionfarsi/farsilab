## Freq Monitor

# Frequency counter
from freqcounter import FreqTask
from numpy import *
import sys

channels = [2,4,6]

# init frequency reader
ts = []
for ch in channels:
    ts.append(FreqTask(ch,0.5))

while True:
    timestamp = 0
    for t in ts:
        ## t.start() # TODO
    row = []
    for t in ts:
        row.append(t.read())
    
    print '  ,'.join(['%6d'%d for d in row])
    ## save or write row.. down
