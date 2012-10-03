# -*- coding: utf-8 -*-
"""
:author: Action Farsi
:date: 13 July 2012

The script is composed by 4 parts

* Serial Communication
* Low-level comunication
* High-level comunication routines
* Acquisition routines

"""

from matplotlib import pylab as pl
import matplotlib.animation as animation
from numpy import savetxt, random

from ctypes import *

## Using this driver because better control over the stream
dll = windll.LoadLibrary('FTD2XX.DLL')

class FT_DEVICE_LIST_INFO_NODE(Structure):
    _fields_ = [("Flags", c_ulong),
                ("Type", c_ulong),
    ("ID", c_ulong),
    ("LocId", c_ulong),
    ("SerialNumber", c_char*16),
    ("Description", c_char*64),
    ("FT_HANDLE", c_ulong),]


## Variables for serial comunication    
lists = c_ulong()
bytes_read = c_ulong()
buff1 = create_string_buffer(1024*4)
buff2 = create_string_buffer(1024*4)
bin_buff = (c_ulong *(1024*4)) ()

def initSerial():
    dll.FT_CreateDeviceInfoList(byref(lists))
    devices_list = (FT_DEVICE_LIST_INFO_NODE*4)()
    dll.FT_GetDeviceInfoList (devices_list,  byref(lists))

    handle = c_ulong()

    dll.FT_Open(0,byref(handle))
    dll.FT_SetTimeouts(handle, 500, 500)
    dll.FT_SetBaudRate(handle, 38600*4*4)
#   dll.FT_GetDeviceInfo (handle, None, 
#       byref(n_devices), byref(buff1),
#       byref(buff2), None)
    return handle
    
## Init serial and find device    
## handle is a global varaible
handle = initSerial()

## Serial port functions (adapted for our TDC system)
    
def read():
    """ Read from serial 
    
    return a c_type array"""
    dll.FT_Read(handle, buff1, 1024, 
                byref(bytes_read))
    return buff1[:bytes_read.value]
    
def write(text):
    """ Write to serial a text string"""
    dll.FT_Write(handle, text, len(text), 
                byref(bytes_read))

def ask(text):
    """ Write to serial and immediately read"""
    write(text)
    return read()   

def read_b(n):
    """ Read the next n long (4 bytes)
    
    return a c_type array of longs (4bytes) """
    dll.FT_Read(handle, bin_buff, 4 * n, 
                byref(bytes_read))
    
    return bin_buff[:bytes_read.value/4] 
   
##
##  TDC 
## ======================

## values to go from TDC to ps
## This is hard-coded (measured once)
conversion = 0.0038

status_codes ={ 1 << 9: "Timeout Error",
                1 << 10: "Timeout Precounter",
                1 << 11: "Error Open",
                1 << 12: "Error Short",}
                
status_values = {}

## Registry values: (reg, LSBit, lenght, default)
# initRegistry() generate and writes them on the TDC
# using the default value  
# TODO, better interface

registry_values = {"NEG_START"  : (0,0,1,0),
            "NEG_STOP1"  : (0,1,1,0),
            "NEG_STOP2"  : (0,2,1,0),
            "MRange2"    : (0,3,1,0),
            "DisAutoCal" : (0,4,1,0),
            "Calibrate"  : (0,5,1,1),
            "SelClkT"    : (0,6,1,1),
            "FAKE#"      : (0,7,1,0),
            "TCycle"     : (0,8,1,0),
            "Port#"      : (0,9,1,1),
            "Start_ClkHs": (0,10,2,1),
            "ClkHSDiv"   : (0,12,2,0),
            "CALRES#"    : (0,14,2,0),
            "DIV_FIRE"   : (0,16,4,0),
            "FIRE#"      : (0,20,4,0),

            "HITN1"      : [1,8,3,1],   # Expected Hit1
            "HITN2"      : [1,11,3,0],  # Expected Hit2
            "En_Fast_ini": [1,15,1,0],
            "Hit1"       : [1,16,4,1],  # ALU 1
            "Hit2"       : [1,20,4,0],  # ALU 2

            "DELVAL1"    : (2,0,18,0),
            "RFEDGE1"    : (2,19,1,0),
            "RFEDGE2"    : (2,20,1,0),
            "EN_INIT"    : (2,21,3,0b110),

            "DELVAL2"    : (3,0,18,0),
            "SEL_TIMO_MR2":(3,19,2,3),
            "EN_ERR_VAL" : (3,21,1,0),

            "DELVAL3"    : (4,0,18,0),

            "PHASE_FIRE" : (5,0,15,0),
            "REPEAT_FIRE": (5,16,3,0),
            "DIS_PhaseNoise": (5,19,1,0),
            "EnStartNoise": (5,20,1,0),
            "Conf_Fire"  : (5,21,3,0),
}

##    
##  Basic comunication
## =====================

def writeRegistry(addr,reg):
    """ Write registry (as long) at the given address
    
    :arg add: address number from 0 to 5
    :arg reg: value to write (int, 4 bytes)
        
    TDC command is ''w + add + value''"""
    
    write((c_ubyte*7) (ord('w'), addr, 
                     reg >> 24,reg >> 16,reg >> 8,reg))
    return read()

def readRegistry(addr):
    """ Write registry (as long) at the given address
    
    :arg addr: address, from 0 to 5
    
    TDC command is "s + add" """

    write((c_ubyte*2)(ord('s'), addr))
    return read()
    
def readBuffer(ch2 = False, conversion = conversion,):
    """ Return the measured time delay from the TDC buffer
    
    :arg ch2: set true if TDC measures 2 channels (False)
    :arg conversion: conversion between int and picoseconds (hardcoded)
        
    Reads from the buffer of the TDC, converts them in picosecond
    If ch2, it expects to receive two seqeuences, one for each
    channel.
    
    Read buffer = command 'r' """
    
    write('r')  
    try:
        size = read_b(1)[0]
        data = [ d * conversion for d in read_b(size)]
        if ch2:
            size2 = read_b(1)[0]
            if size != size2:
                print "Ch1 %d !=  Ch2 %d"%(size,size2)
            data = [data,[ d * conversion for d in read_b(size)] ]
        return data
    except:
        print "No buffer"
        if ch2:
            return [[],[]]
        return []

def restartTDC():
    """ Reset the tdc 
    
    TDC command is "p" 
    """
    
    write('p')
    return read()
        
def testComm():
    """ Test that comunication with TDC are working

    It prints the raw status register and the first register
    it also decodes the status register.
    
    TDC command is "t" 
    """
    
    write('t')
    r = read_b(2)
    r[0] = r[0]>>16
    b = c_byte(r[1])
    print "Status %04x First Register %8x"%(r[0], r[1])
    for bit in status_codes:
        if (r[0]) & bit:
            print status_codes[bit]
    print "Pointer = ",r[0]%8
    print "Hit 1 = " ,(r[0]>>3)%8
    print "Hit 2 = " ,(r[0]>>6)%8
    
def initRegistry():
    """ Initialiaze the GP2 registry
    
    It generates values from :py:data:'registry_values' and
    writes them on TDC. It prints the written values
    
    The :py:data:'registry_values' is a dictionary
    used to simplify GP2 configuration.
    It contains all the possible options for the GP2,
    the location of the bit, and the default value.
    
    In order to init the chip:
    
    1 set the correspondent option on :py:data:'registry_values'
    2 call initRegistry()
    """
    
    regs = [0,0,0,0,0,0]
    for i in registry_values.values():
        regs[i[0]] = (regs[i[0]]) | (i[3] << i[1])
    print "Writing registry: "
    for i in xrange(6):
        print "Reg %d = %08x"%(i, regs[i]<< 8)
        writeRegistry(i,regs[i] <<8)

def initTdc(channels = 1):
    """ Reset board and start measurement

    :arg channels: 1,2     
    """
    dll.FT_Purge(handle,0b11)
    registry_values['HITN1'][3] = 1
    registry_values['HITN2'][3] = 0
        
    if (channels == 2):
        registry_values['HITN1'][3] = 1
        registry_values['HITN2'][3] = 1
        write('2')
    else:
        write('1')
        
    print ask('a')
    time.sleep(0.01)
    initRegistry()
    time.sleep(0.01)
    ## Reset and start measurement
    restartTDC()  

##
##  Helper functions
## ==============================    
def reverseBit(byte, n=32):
    rbyte = 0
    for i in xrange(n):
        if (byte & (1<<i)):
            rbyte |= (1<<(n-1-i))
    return rbyte
        

import time

def test():
    """ Test reading channel 1 
    
    Read the buffer 50 times and display some info
    """
    initTdc(channels = 1)
    testComm()
    data = []
    tic = time.time()
    ## Start reading loop
    for x in xrange(50):
        time.sleep(0.5)
        data.extend(readBuffer())
    # print data 
    toc = time.time()-tic
    print "Total data taken = ", len(data)
    print "Last data measured was %f ps"%(data[-1])
    print "Counts / sec = %.2f"%(1.*len(data)/toc)
    raw_input()

def test2ch():
    """ Test reading 2 channels 
    
    Read the buffer 50 times and display some info
    """
    initTdc(channels = 2)
    testComm()
    time.sleep(0.01)
    data = [[],[]]
    tic = time.time()
    ## Start reading loop
    for x in xrange(50):
        time.sleep(0.5)
        d = readBuffer(True)
        data[0].extend(d[0])
        data[1].extend(d[1])
    # print data 
    
    print "Total data taken = ", len(data[0])
    print "Last data measured was ch1: %.2f ps, ch2: %.2f ps"%((data[0][-1]*conversion),
                                                               (data[1][-1]*conversion))
    print "Counts / sec = %.2f"%(1.*len(data[0])/toc)

def generateHist(data, bins = 20, rnge = None,
                       histogram = None):
    """ Generate an histogram of data
    
    :arg data: Array-like
    :arg bins: Number of bins
    :arg rnge: 2-tuple with min and max values,
               if None it is calculated from the data
    :arg histogram: Array-like updated histogram rather then create new one
                    If histogram is not None, also a range must be given
    """
    
    if histogram == None:
        histogram = [0]*bins
    else:
        if rnge == None:
            raise Exception("Histogram given but not range")
        bins = len(histogram)
    if rnge == None:
        rnge = [min(data),max(data)]
    delta_bin = 1.*(rnge[1] - rnge[0])/bins
    
    for d in data:
        if (d>=rnge[0]) and (d<rnge[1]):
            histogram[ int((d-rnge[0])/delta_bin) ] += 1
    return ( (pl.arange(bins)+ 0.5)*delta_bin + rnge[0]), histogram
    
##
##  Acquisition routines
## ==========================

import threading, time, sys

#sys.path.append('E:\Utilities')
#import instserver
#try:
    #server = instserver.server()
#except:
server = None
    
## Threads for the acquisition and elaboration. 
class AcquisitionWorker(threading.Thread):
    """ Thread for acquire data from 1 channel
    
    To use it
    
    1. Initialize the TDC
    2. Create the thread
    3. Start the thread
    4. The thread will store the acquisition in the variable self.data
    5. Once acquisition is done, stop the threads, and save the data on file.
    
    It can also save a temporary file on disk (in case of accident).
    Optionally it updates an histogram for real-time visualization.
    
    It **does not** initialize, only read the buffer.
    """
    
    def __init__(self, bins = 10, rnge = (0,100), temp_file = 'temp.txt',
                       do_histograms = True):
        """ Thread constructor
        
        :arg temp_file: Name of the temporary file
        :arg do_histogram:
        :arg bins:
        :arg rnge:
        
        """
        threading.Thread.__init__(self)
        self.bins = bins
        self.rnge = rnge
        self.data = []
        self.hist = generateHist([], self.bins, rnge= self.rnge)
        if temp_file != None:
            self.temp_file = open(temp_file,'w')
        else:
            self.temp_file = None
        self.do_histograms = do_histograms
        
            
        
    def run(self):
        """ Thread loop
        
        In an infinite loop, it reads the TDC buffer,
        converts it in time, and optionally create the histogram
        
        To stop the loop, set self.kill = True
        """
        
        self.kill = False
        self.demon = True
        
        tic = time.time()
        
        new_data = []
        i = 0
        
        while not self.kill:
            i += 1
            time.sleep(0.1)
            d = readBuffer()
            print 'len ', len(d)
            #d = random.rand(10)*100
            new_data.extend(d)
            
            if i %5 == 0:
                toc = time.time()-tic
                self.data.extend(new_data)
                print "\nStarts / sec = %8.2f"%(1.*len(new_data)/toc)
                
                ## Remove timeouts
                new_data = new_data[pl.nonzero(new_data[:] < 3000)[0]]
                
                print "  Stops / sec = %8.2f"%(1.*len(new_data)/toc)
                
                ## Generate channels histogram
                if self.do_histograms:
                    self.hist = generateHist(new_data, self.bins, rnge= self.rnge,histogram = self.hist[1])                  
                    #print "Ch1 ",self.hist[1]
                    
                ## Save a tempfile and flush (just to be sure)
                if self.temp_file != None:
                    for d in new_data:
                        self.temp_file.write( "%12.3f \n"%(d) ) 
                tic = time.time()
                new_data = []
                
                
class AcquisitionWorker2ch(threading.Thread):
    """ Thread for acquire data from 2 channels
    
    To use it
    
    1. Initialize the TDC
    2. Create the thread
    3. Start the thread
    4. The thread will store the acquisition in the variable self.data
    5. Once acquisition is done, stop the threads, and save the data on file.
    
    It can also save a temporary file on disk (in case of accident).
    Optionally it updates an histogram for real-time visualization.
    
    It **does not** initialize, only read the buffer.
    """
    
    def __init__(self, bins = 10, rnge = (0,100), temp_file = 'temp.txt',
                       do_histograms = True, do_coincidences = False):
        """ Thread constructor
        
        :arg temp_file: Name of the temporary file
        :arg do_histogram:
        :arg bins:
        :arg rnge:
        :arg do_coincidences: Generate an additional 
                              histogram with the coincidences t2-t1
        """
        threading.Thread.__init__(self)
        self.bins = bins
        self.rnge = rnge
        self.data = [pl.array([]),pl.array([])]
        self.hist = [generateHist([], self.bins, rnge= self.rnge),
                     generateHist([], self.bins, rnge= self.rnge)]
        self.n_starts = 0
        if temp_file != None:
            self.temp_file = open(temp_file,'w')
        else: 
            self.temp_file = None
        self.do_coincidences = do_coincidences
        self.do_histograms = do_histograms
        if do_coincidences:
            self.rnge_c = (self.rnge[0] - self.rnge[1], self.rnge[1] - self.rnge[0])
            self.hist_c = generateHist([], 2*self.bins, rnge= self.rnge_c)
            
        
    def run(self):
        """ Thread loop
        
        In an infinite loop, it reads the TDC buffer,
        converts it in time, and optionally create the histogram
        
        To stop the loop, set self.kill = True
        """
        self.kill = False
        self.demon = True
        
        tic = time.time()
        
        new_data = [ [],[] ]
        i = 0
        
        while not self.kill:
            i += 1
            time.sleep(0.1)
            d = readBuffer(True)
            #d = random.rand(2,10)*100
            new_data[0].extend(d[0])
            new_data[1].extend(d[1])
            if i %5 == 0:
                toc = time.time()-tic
                self.n_starts += len(new_data[0])
                print "\nStarts / sec = %8.2f   "%(1.*len(new_data[0])/toc),
                new_data = pl.array(new_data)
                ## Remove timeouts
                t1 = pl.nonzero(new_data[0,:] < 3000)[0]
                t2 = pl.nonzero(new_data[1,:] < 3000)[0]
                
                try:
                    new_data = new_data[:, pl.union1d(t1,t2)]
                except IndexError:
                    pass
                    
                self.data[0]= pl.concatenate((self.data[0],new_data[0,:]))
                self.data[1]= pl.concatenate((self.data[1],new_data[1,:]))
                
                
                ## Generate channels histogram
                if self.do_histograms:
                    self.hist[0] = generateHist(new_data[0], self.bins, rnge= self.rnge,histogram = self.hist[0][1])
                    self.hist[1] = generateHist(new_data[1], self.bins, rnge= self.rnge,histogram = self.hist[1][1])
                    #print "Ch1 ",self.hist[0][1]
                    #print "Ch2 ",self.hist[1][1]
                    
                ## Generate coincidences histogram
                if self.do_coincidences:
                    try:
                        coinc = new_data#[:,pl.intersect1d(t1,t2)]
                        coinc = coinc[1]-coinc[0]
                        self.hist_c = generateHist(coinc, 2*self.bins, rnge = self.rnge_c, histogram = self.hist_c[1])
                        #print "Coincidences ", self.hist_c[1]
                        print "Coinc Rate %8.2f"%(1.*len(coinc)/toc),
                    except IndexError:
                        print "Coinc Rate %8.2f"%(0),
                        
                        
                    
                ## Save a tempfile and flush (just to be sure)
                if self.temp_file != None:
                    for i in xrange(len(new_data[0])):
                        self.temp_file.write( "%12.3f %12.3f\n"%(new_data[0][i],new_data[1][i]) ) 
                tic = time.time()
                new_data = [[], []]
                
##
##  Monitor
## ====================
## Uses matplotlib v1.1

from matplotlib.widgets import Button

def monitorTDC(bins = 100, rnge = (0,100) ):
    """ Realtime acquisition and monitor
    
    :arg bins:
    :arg rnge:
    
    When done, close first the Gui.
    Then the prompt will ask how to save the data.
    
    It creates an AcquisitionWorker thread, and an animated
    matplotlib window that updates with data coming from the
    acquisiton
    """
    ## TODO check version of Matplotlib
    
    ## Initialize the measurement
    initTdc()
    
    ## Start thread for 1 channel acquisition
    aWorker = AcquisitionWorker(bins = bins, rnge = rnge)
    aWorker.start()

    ## Init the figure for displaying the histogram
    
    def update_line(num, line):
        line.set_data(aWorker.hist)
        if max(aWorker.hist[1]) > update_line.scale *0.85:
            update_line.scale *= 2
            pl.ylim(0, update_line.scale)
            fig.canvas.draw()
        
        return line,
        
    fig = pl.figure()
    ax = pl.gca()
    l, = pl.plot(aWorker.hist[0], aWorker.hist[1], 'r-')
    pl.xlabel('Time (ps)')
    pl.title('TDC Channel 1')
    update_line.scale = 25
    pl.ylim(0, update_line.scale)
    
    ## Start the animation, that is a loop were 
    line_ani = animation.FuncAnimation(fig, update_line, 1,repeat = True,
                                        fargs=(l,),
                                        interval=500, blit=False)    
    
    pl.show()
    
    ## When the window is closed, stop acquisition and save data
    aWorker.kill = True
    time.sleep(0.5)
    n = raw_input('Save data in file name -> ')
    savetxt(n + '.txt', aWorker.data)

def monitorTDC2(bins = 100, rnge = (0,100) ):    
    """ Realtime acquisition and monitor
    
    :arg bins:
    :arg rnge:
    
    When done, close first the Gui.
    Then the prompt will ask how to save the data.
    
    It creates an AcquisitionWorker thread, and an animated
    matplotlib window that updates with data coming from the
    acquisiton
    """
    
    ## TODO check version of Matplotlib
    
    ## Initialize the measurement
    initTdc(2)
    time_start = time.time()
    ## Start thread for 1 channel acquisition
    aWorker = AcquisitionWorker2ch(bins = bins, rnge = rnge,
                                    do_coincidences = True)
    aWorker.start()

    ## Init the figure for displaying the histogram
    
    def update_line(num):
        l1.set_data(aWorker.hist[0])
        l2.set_data(aWorker.hist[1])
        if max(aWorker.hist[0][1]) > update_line.scale1 *0.85 or \
           max(aWorker.hist[0][1]) > update_line.scale1 *0.85:
            update_line.scale1 *= 3
            ax1.set_ylim(0, update_line.scale1)
            fig.canvas.draw()
        l3.set_data(aWorker.hist_c)
        if max(aWorker.hist_c[1]) > update_line.scale2 *0.85:
            update_line.scale2 *= 3
            ax2.set_ylim(0, update_line.scale2)
            fig.canvas.draw()
        if server != None:
            server.values = [aWorker.hist_c[1]]
        return l1,l2,l3
    
    fig = pl.figure()
    ax1 = pl.subplot(121)
    l1, = pl.plot(aWorker.hist[0][0], aWorker.hist[0][1], 'r-')
    l2, = pl.plot(aWorker.hist[1][0], aWorker.hist[1][1], 'b-')
    pl.xlabel('Time (ps)')
    pl.title('TDC Channel 1,2')
    update_line.scale1 = 25
    ax1.set_ylim(0, update_line.scale1)
    ax2 = pl.subplot(122)
    l3, = pl.plot(aWorker.hist_c[0], aWorker.hist_c[1], 'g-')
    pl.xlabel('Time (ps)')
    pl.title('TDC Coincidences')
    update_line.scale2 = 25
    ax2.set_ylim(0, update_line.scale2)
    
    
    ## Start the animation, that is a loop were 
    line_ani = animation.FuncAnimation(fig, update_line, 1,repeat = True,
                                        interval=500, blit=False)    
    
    pl.show()
    
    ## When the window is closed, stop acquisition and save data
    aWorker.kill = True
    time_stop = time.time()
    time.sleep(0.5)
    #print aWorker.hist_c[1]
    print "Time acquisition = %.2f\nN Starts = %d"%(time_stop-time_start,aWorker.n_starts) 
    n = raw_input('Save data in file name -> ')
    savetxt(n + '.txt', aWorker.data)  # header = "Time acquisition = %.2f\nN Starts = %d"%(time_stop-time_start,aworker.n_starts) 
    
    
    
def simpleThreadedAcquisition():
    """ Realtime acquisition using thread
    
    This is mostly an example that uses the threaded acquisition
    """
    ## Initialize the measurement
    ## Default 1 channel
    initTdc()
    
    ## Start thread for 1 channel acquisition
    aWorker = AcquisitionWorker()
    aWorker.start()

    ## Press return to stop
    try:
        raw_input()
    except KeyInterrupt:
        pass
    aWorker.kill = True
    time.sleep(0.5)
    ## Save the acquired data
    n = raw_input('Save data in file (name) -> ')
    savetxt(n + '.txt', aWorker.data)


    
def simpleAc():    
    """ Read and print from TDC
    
    Very simple acquisition procedure
    """
    initTdc()
    write('1')
    time.sleep(0.01)
    
    ## Init variables
    tic = time.time()
    data = []
    new_data = []
    hist = [0] * 10
    i = 0        
    
    while True:
        i += 1
        time.sleep(0.01)
        new_data.extend(readBuffer())
        if i %10 == 0:
            data.extend(new_data)
            toc = time.time()-tic
            print "Counts / sec = %.2f"%(1.*len(new_data)/toc)
            hist = generateHist(new_data, 10, rnge= [0,100],histogram = hist)[1]
            print hist
            tic = time.time()
            new_data = []

def simpleAc2():    
    """ Read and print from TDC from 2 channels
    
    Very simple acquisition procedure
    """
    ## Init TDC
    initTdc()
    write('1')
    time.sleep(0.01)
    
    bins = 10
    rnge = (0,100)
    
    ## Init variables
    tic = time.time()
    data = [[],[]]
    new_data = [[],[]]
    hist = [[0] * bins, [0]* bins]
    i = 0
    
    ## Start reading loop
    while True:
        i += 1
        time.sleep(0.01)
        d = readBuffer()
        new_data[0].extend(d[0])
        new_data[1].extend(d[1])
        if i %10 == 0:
            data[0].extend(new_data[0])
            data[1].extend(new_data[1])
            toc = time.time()-tic
            print "Counts / sec = %.2f"%(1.*len(new_data[0])/toc)
            hist[0] = generateHist(new_data[0], bins, rnge= rnge,histogram = hist[0])[1]
            hist[1] = generateHist(new_data[1], bins, rnge= rnge,histogram = hist[1])[1]
            print hist[0]
            print hist[1]
            tic = time.time()
            new_data = [[],[]]
            
    # print data 

#test()
#simpleThreadedAcquisition()
#monitorTDC(bins = 200, rnge = (100,200) )
#monitorTDC2(bins = 200, rnge = (100,200) )
