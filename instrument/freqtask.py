"""
based on NiDAQmx (nicaiu.dll)

Create instance with 
FreqTask(channel, [sampling time, count, debug])
 
Get values with 
FreqTask.read()

If you want a threaded job
job = FreqTask.read_thread(callback)
 
See test() for example of usage
 
""" 


import sys
from time import sleep
from numpy import savetxt

from ctypes import *
import threading

# load DAQMX library
dll = windll.LoadLibrary("nicaiu.dll")
from nidaq import *   # Contains constants

def printf(x):
    print x

## Shorthand for the task
class FreqTask():
    def __init__(self, channel, sampling_time = 0.5, count = False, debug = False):
        self.n_samples = 4000                                  # Buffer size (only one reading at time)
        self.channel = channel
        self.sampling_time = sampling_time
        self.sample_rate = 1000
        
        self.handle = c_int(0)                                 # DAQmx TaskHandle
        self.name = "FreqCounter on ch " + str(channel)        # Task Name generated on the fly
        self.data = (c_double * self.n_samples)()              # Buffer on disk for acquisition
        
        if channel not in range(0,7): channel = 0              # Check that physical channel exist
        self.physical_channel = "Dev1/ctr" + str(channel)      # Physical Channel: DI0 on Dev1
        self.channel_name = ""                                 # Useless
        
        self.debug = debug
        self.count = count
        
        # Create the task
        if debug: print "Creating the task  ", 
        
        # First create the task and get a handle to the task that will be used for all subsequenct operations
        self.error(dll.DAQmxCreateTask(self.name, byref(self.handle)))
        
        if not count:
            # Create the frequency reading
            self.error(dll.DAQmxCreateCIFreqChan(self.handle, self.physical_channel, self.channel_name,
                    c_double(5), c_double(500000), DAQmx_Val_Hz, DAQmx_Val_Rising, DAQmx_Val_HighFreq2Ctr,
                    c_double(self.sampling_time), c_uint32(10), None) )
                    
            # Use implicit timing (generated from sampling_time)
            self.error(dll.DAQmxCfgImplicitTiming(self.handle,DAQmx_Val_FiniteSamps,c_uint64(self.n_samples)))
        
        else: ## TODO Check if it's properly woriking
            # Create counting reading
            self.error(dll.DAQmxCreateCICountEdgesChan(self.handle, self.physical_channel,
                                                       self.channel_name,
                                                       DAQmx_Val_Rising ,
                                                       c_uint32(0),
                                                       DAQmx_Val_CountUp) )
                
            #####
            #self.error(dll.DAQmxCfgSampClkTiming (self.handle, "",
            #                                      c_double(self.sample_rate),
            #                                      DAQmx_Val_Rising,
            #                                      DAQmx_Val_ContSamps,
            #                                      c_ulonglong(self.n_samples)) )
                    
            
                            
            # self.error(dll.DAQmxCfgImplicitTiming(self.handle,
                                                  # DAQmx_Val_ContSamps,c_uint64(self.n_samples)))

    def read(self, to_read = -1):
        bit_read = c_int()
        
        self.error(dll.DAQmxReadCounterF64(self.handle, to_read, c_double(10),
                    byref(self.data), self.n_samples, byref(bit_read), None))
        if self.debug:
            print " .... "
            for v in self.data: print v,
            print ""
        #if self.count:
        #    return [float(i) for i in self.data]
        return [float(i) for i in self.data[:bit_read.value] ]
    
    def thread_read(self, callback = printf, to_read = -1):
        """ To execute the reading in a thread for parallel acquisition """
        ## TODO Check if internal DAQmx callback method is better
        def run():
            while True:
                callback(self.read(1))
        if self.debug: print "Starting Thread for %s"%self.name
        job = threading.Thread(target = run)
        job.start()
        return job
    
    def error(self, return_value):
        """ Exceptions manager """
    ## TODO add special cases
        try:
            if return_value == -200089:
                ## TODO if it was during initialiation, re-init
                self.error( dll.DAQmxClearTask(self.handle) )
                print "The task was still open.. Task closed"
                raise Exception("Error: %d"%return_value)
            
            if return_value in [-200284,-200302]:
                print "Timeout"
                self.data[-1]  = c_double(0)
                self.error( dll.DAQmxClearTask( self.handle) )
                self.__init__(self.channel, self.sampling_time)
                return
            
            if return_value in [-200278]:
                print "Data lost"
                self.data[-1]  = c_double(0)
                dll.DAQmxStopTask(self.handle)
                dll.DAQmxStartTask(self.handle)
                return
            
            if return_value != 0:
                raise Exception("Error: %d"%return_value)
                
        except:
            st = (1024*c_char)()
            dll.DAQmxGetExtendedErrorInfo (byref(st), 1024)
            print ''.join([c for c in st])
            del self
            raise Exception("exit")
                       
    def __del__(self):
        if self.debug: print "Task cleared"
        dll.DAQmxClearTask(self.handle)
        
def test(channel = 2, time = 0.8):
    """ Test task first with both modal and threaded methods """
    
    task = FreqTask(channel, time, debug = True)     ## Frequency task
    
    ## 1st method
    print "Main thread method"
    for i in xrange(10):
        print task.read()
    
    ## 2nd method
    print "Threaded method"
   
    ## Define a function to call everytime it reads
    def printx(x):                    
        print x
    job  = ts.thread_read(printx)
	
    while True:
        print "Press return to interrupt"
        raw_input()
        del job
    

if __name__ == "__main__":
    test(channel = 2, time = 1)
    