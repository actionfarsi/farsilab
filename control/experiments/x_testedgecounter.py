import sys
from time import sleep,clock
from numpy import savetxt

from ctypes import *
import threading

# load DAQMX library
dll = windll.LoadLibrary("nicaiu.dll")

# CONST from NIDAQmx.h
DAQmx_Val_Rising  = 10280
DAQmx_Val_Falling = 10171
DAQmx_Val_CountUp = 10128
DAQmx_Val_FiniteSamps = 10178 # Finite Samples
DAQmx_Val_ContSamps  = 10123

DAQmx_Val_Hz =                                                     10373 # Hz
DAQmx_Val_LowFreq1Ctr                                            = 10105 # Low Frequency with 1 Counter
DAQmx_Val_HighFreq2Ctr                                           = 10157 # High Frequency with 2 Counters
DAQmx_Val_LargeRng2Ctr                                           = 10205 # Large Range with 2 Counters

DAQmx_Val_Seconds          = 10364 # Seconds
DAQmx_Val_Ticks                                                  = 10304 ## Ticks
DAQmx_Val_DoNotInvertPolarity = 0

## Shorthand for the task
class FreqTask():
    def __init__(self, channel, sampling_time = 0.01, count = False ):
        self.n_sample = int(100e4)
        self.channel = channel
        self.sampling_time = sampling_time
        
        self.handle = c_int(0)           #DAQmx TaskHandle
        self.name = "FreqCounter on ch " + str(channel)             #Task Name
        self.data = (c_double * self.n_sample)()
        
        self.lost = 0
        print "Creating the task"
        
        # dll.DAQmxResetDevice ("Dev1")
        # self.error(dll.DAQmxConnectTerms( "/Dev1/PFI15", "/Dev1/Ctr0Aux",
                    # DAQmx_Val_DoNotInvertPolarity))
        # self.error(dll.DAQmxConnectTerms( "/Dev1/PFI31", "/Dev1/Ctr0Gate",
                    # DAQmx_Val_DoNotInvertPolarity))

        #First create the task and get a handle to the task that will be used for all subsequenct operations
        #Function Prototype: int32 DAQmxCreateTask (const char taskName[], TaskHandle *taskHandle);
     
        if channel not in range(0,7): channel = 0
        self.physical_channel = "Dev1/ctr" + str(channel)    #Physical Channel: DI0 on Dev1
        self.channel_name = ""             
        
        # Create the task
        self.error(dll.DAQmxCreateTask(self.name, byref(self.handle)))
        
        # Create the frequency reading
        self.error(dll.DAQmxCreateCITwoEdgeSepChan (self.handle, self.physical_channel, self.channel_name,
                    c_double(25e-9), c_double(5e-6), DAQmx_Val_Seconds, DAQmx_Val_Rising,DAQmx_Val_Rising, None))
        
        self.error(dll.DAQmxCfgImplicitTiming(self.handle,DAQmx_Val_ContSamps,c_uint64(self.n_sample)))
        

        
    
    def read(self):
        bit_read = c_int()
        
        # self.error(dll.DAQmxStartTask(self.handle))
        self.error(dll.DAQmxReadCounterF64(self.handle, -1, c_double(11),
                    byref(self.data), self.n_sample, byref(bit_read), None))
        # self.error(dll.DAQmxStopTask(self.handle))
        
        # print "Read ",bit_read
        # print ', '.join([str(c) for c in self.data])
        # print bit_read.value
        return self.data[0:bit_read.value]

    
    def thread_read(self, callback = lambda x: x):
        def run():
            while True:
                callback(self.read())
        print "Starting Thread"
        job = threading.Thread(target = run)
        job.start()
        return job
    
    def error(self, return_value):
        try:
            # if return_value == -200089:
                # self.error( dll.DAQmxClearTask( self.handle) )
                # print ("The task was still open.. Task closed")
                # raise Exception("Error: %d"%return_value)
            
            # if return_value in [-200284,-200302]:
                # print "Timeout"
                # self.data[-1]  = c_double(0)
                # self.error( dll.DAQmxClearTask( self.handle) )
                # self.__init__(self.channel, self.sampling_time)
                # return
            
            # if return_value in [-200278]:
                # print "data lost"
                # self.data[-1]  = c_double(0)
                # dll.DAQmxStopTask(self.handle)
                # dll.DAQmxStartTask(self.handle)
                # return
            
            # if return_value in [-200140]:
                # self.lost = self.lost +1
                # return
            
            if return_value != 0:
                raise Exception("Error: %d"%return_value)
        except:
            st = (1024*c_char)()
            dll.DAQmxGetExtendedErrorInfo (byref(st), 1024)
            print ''.join([c for c in st])
            del self
            raise Exception("exit")
                       
    def __del__(self):
        print "Task claered"
        dll.DAQmxClearTask(self.handle)
        
def test(channel = 1, time = 0.8):    
    
    file = open("tmp.txt",'w')    
    ts  = FreqTask(0,0.000001)
    
    l = 0
    
    while True:
        tic = clock()
        sleep(0.3)
        toc = clock() - tic
        a = ts.read()
        
        l =  len(a)        
       
        
        
        if l > 0:
            print l/toc, toc, l
            #for i in a:
            #    file.write(str(i)+"\n")
        #file.flush()
        #if toc > 10:
        #    return
        #job = threading.Thread(target = run, args = (a,) )
        #job.start()

if __name__ == "__main__":
    test(channel = 0, time = 0.1)
    #monitor()
    #readdouble()