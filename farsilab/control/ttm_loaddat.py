# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 11:07:42 2016

@author: mw482
"""

import ctypes
import ttm
import os
import numpy as np
from matplotlib import pylab
from scipy.io import savemat, loadmat

def block_it(size, block_size):
    if block_size > size:
        yield size
        return
    #split in equal blocks and add the last block.
    l = size//block_size
    for i in range(l):
        yield block_size
    yield l % block_size

def rebase(time, channel, start):
    """ Time - time tags array
        channel - Channel number array
        start - Channel # to use as timebase"""
        
    def start_it():  # Use a generator to
        start_ar = np.where(channel == start, time, 0)
        t0 = start_ar[0]
        for t in start_ar:
            if t != 0:
                t0 = t
            yield t0
            
    st = np.fromiter(start_it(),np.uint64, count = len(time))
    return(time[channel != start], (time-st)[channel != start], channel[channel != start])

span = lambda t,x1,x2 : np.logical_and(t>=x1, t<=x2)

def process_file(filename = 'TimeTagsOut[8].dat', ranges = (15000, 16100)):
    f= open(filename, 'rb')
    size = os.fstat(f.fileno()).st_size -30
    m1 = f.read(30)  ## FIrst 30 byte are the header
    
    #hh = ctypes.cast(m1, ttm.timetag_header_p).contents
    
    #z = hh.magicA
    #print(hh.magicA.to_bytes(2,'big'), hh.magicB.to_bytes(2,'big'),
    #      hh.magicC.to_bytes(2,'big'),hh.magicD.to_bytes(2,'big'),
    #      hh.packet_version.to_bytes(2,'little'), hh.data_size,
    #      hh.data_format % 2**4)
    
    #    ttm.decodePacket(f.read(4),packet_mode = 'i64c')
    n =  size
    block_size = 3000000*4
    #print(size/block_size)
    
    data =[]
    
    for i,l in enumerate(block_it(n,block_size)):
        print("{:.1f}%".format(100*i / (size/block_size)),)
        t,c = ttm.ttm_c.decodePacket(f.read(l), data_size = l//4, packet_mode = 'i64c', track_t0 = False)
        #print(t, c)
        t,dt,c = ttm.ttm_c.rebase(t, c, 5)
        s = span(dt, ranges[0], ranges[1])
        data.append((t[s],dt[s],c[s]))
    
    #join all the blocks 
    s = sum((len(d[0]) for d in data))
    t = np.hstack((d[0] for d in data))
    dt = np.hstack((d[1] for d in data))
    ch = np.hstack((d[2] for d in data))
    
    savemat(filename[:-4] + '_r[{:},{:}]'.format(ranges[0], ranges[1]),
            {'t': t, 'dt': dt, 'ch': ch})
    f.close()


def speed_test_c(filename, n = 100000):
    f= open(filename, 'rb')
    size = os.fstat(f.fileno()).st_size -30
    m1 = f.read(30)  ## FIrst 30 byte are the header

    t,c = ttm.ttm_c.decodePacket(f.read(n*4), data_size = n,
                     packet_mode = 'i64c', track_t0 = False)
    t,dt,c = ttm.ttm_c.rebase(t, c, 5)

def speed_test_c(filename, n = 100000):
    f= open(filename, 'rb')
    size = os.fstat(f.fileno()).st_size -30
    m1 = f.read(30)  ## FIrst 30 byte are the header

    t,c = ttm.decodePacket(f.read(n*4), data_size = n,
                     packet_mode = 'i64c', track_t0 = False)
    t,dt,c = rebase(t, c, 5)

#process_file()

data = loadmat('TimeTagsOut[4]_r[15000,16100]', squeeze_me = True)
t, dt, ch = data['t'], data['dt'], data['ch']

def my_hist(diffs):
    histogram_d = {}
    h_local = np.unique(diffs, return_counts = True)
    for k,v in zip(*h_local):
        histogram_d[k] = histogram_d.get(k,0) + v
    x = np.sort(np.fromiter(histogram_d.keys(), dtype = np.int64))
    y = np.fromiter((histogram_d[xx] for xx in x), dtype= np.int64, count = len(x))
    return x,y
    
def coinc(time, start, shift = 10000):
    dt = np.diff(time)-np.where(start[1:], shift,0)+shift
    return dt[np.diff(start)]

cc = coinc(t, ch == 1)
print(t, dt,ch)
#h = my_hist(dt[ch==1])
#h = my_hist(cc)
#pylab.plot(h[0], h[1])
pylab.hist(cc, range=(200,400), bins=50)   




#t,dt,channel = rebase(time, channel, 5)
#

#s = span(dt, 15900, 16100)



#pylab.hist(dt[ch==1], bins=1000)
#pylab.hist(cc, bins=1000, range=(-100,1000))
#pylab.hist(dt[channel==2], bins=1000, range=(15000, 17000))
pylab.show()




## fillup 
        
    