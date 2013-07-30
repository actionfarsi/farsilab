"""
Perform frequency and coincindence measurement with counting

It need sources in channel 0 and 1 and the triggering gate on
PFI37
"""

from nidaq import *
from numpy import *
import visa

from ctypes import *
import threading, sys
from time import sleep,clock

sys.path.append('E:\Utilities')
import instserver
server = instserver.server()

#Pulse generator

# load DAQMX library
dll = windll.LoadLibrary("nicaiu.dll")

## Shorthand for the task
class CountTask():
    def __init__(self, channel, sampling_time = 0.01, count = False ):
        self.n_sample = 10000000
        self.channel = channel
        # self.sampling_time = sampling_time
        
        self.handle = c_int(0)           #DAQmx TaskHandle
        self.name = "CountCounter on ch " + str(channel)             #Task Name
        self.data = (c_double * self.n_sample)()
        
        self.lost = 0
        
        print "Creating the task"
        
        #First create the task and get a handle to the task that will be used for all subsequenct operations
     
        if channel not in range(0,7): channel = 0
        self.physical_channel = "Dev1/ctr" + str(channel)    #Physical Channel: DI0 on Dev1
        self.channel_name = ""             
        
        # Create the task
        self.error(dll.DAQmxCreateTask(self.name, byref(self.handle)))
        
        # Create the counter reading
        self.error(dll.DAQmxCreateCICountEdgesChan(self.handle, self.physical_channel,"", DAQmx_Val_Rising, 0, DAQmx_Val_CountUp))
        #self.error(dll.DAQmxCfgDigEdgeAdvTrig(self.handle, "/Dev1/PFI37", DAQmx_Val_Rising))
        

        #self.error(dll.DAQmxCfgImplicitTiming(self.handle,DAQmx_Val_ContSamps,c_uint64(self.n_sample)))
        self.error(dll.DAQmxCfgSampClkTiming(self.handle, "/Dev1/PFI37",
                                            c_double(2e6), DAQmx_Val_Rising, DAQmx_Val_ContSamps, c_uint64(self.n_sample)))
        

    def start(self):
        self.error(dll.DAQmxStartTask(self.handle))
    
    def read(self, to_read = -1):
        bit_read = c_int()

        self.error(dll.DAQmxReadCounterF64(self.handle, c_int(to_read), c_double(11),
                    byref(self.data), self.n_sample, byref(bit_read), None))
        
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
            if return_value != 0:
                raise Exception("Error: %d"%return_value)
        except:
            st = (1024*c_char)()
            dll.DAQmxGetExtendedErrorInfo (byref(st), 1024)
            print ''.join([c for c in st])
            del self
            raw_input()
            raise Exception("exit")
                       
    def __del__(self):
        print "Task cleared"
        dll.DAQmxClearTask(self.handle)
        
def test(channel = 1, time = 0.8):    
    def rolldata(data, x):
        data[1:] = data[:-1]
        data[0] = x
    
    samp_t  = 0.5     ## Sampling time
    reprate = 300000  ## Hardcoded!!!
    file = open("tmp.txt",'w')    
    
    n = 40
    counts = int(reprate*samp_t)
    
    data_a = zeros(n)
    data_b = zeros(n)
    data_c = zeros(n)
    
    
    ts1  = CountTask(0)
    ts2  = CountTask(1)
    
    ## TODO Start with a trigger
    ts1.start()
    ts2.start()
    
    l = 0
    a0, b0 = 0,0
    tic = clock()
    while True:
    #gpib = visa.instrument("GPIB::15")

    #for t in linspace(-100,200,80):
        #gpib.write("DLAY 4,2,%.2e"%(t*1e-9))
        for i in xrange(n):
            a = array(ts1.read(counts))
            b = array(ts2.read(counts))
            toc = clock() - tic
            tic = clock()
            
            l =  len(a)        
            if l == 0: continue
            
            # Data analysis (maybe can be even faster)
            a00, b00 = a[-1],b[-1]
            a = a-a0
            b = b-b0
            a_counts, b_counts = (a[-1]-a[0]), (b[-1]-b[0])
            a[:] = hstack((a[0],a[1:]-a[:-1]))
            b[:] = hstack((b[0],b[1:]-b[:-1]))
            c = logical_and(a,b)
            acc = logical_and(a[1:],b[:-1])
            
            rolldata(data_a, a_counts/samp_t)
            rolldata(data_b, b_counts/samp_t)    
            rolldata(data_c, sum(c)/samp_t)
            
            s = "%8.2f %8.2f %6.2f   (%8.4f) acc = %6.2f"%(average(data_a), average(data_b), data_c[0],average(data_c), sum(acc)/samp_t)
            server.log = s
            print s
            file.write(s)
            file.write('\n')
            #print l/toc, toc, l
            #for i in xrange(len(a)):
            #    file.write("%d %d %d\n"%(a[i],b[i],c[i]))
            #file.flush()
            
            a0,b0 = a00,b00
            #if toc > 10:
            #    return
            #job = threading.Thread(target = run, args = (a,) )
            #job.start()
        file.write("%f, %f, %f"%(average(data_a),average(data_b),average(data_c)))

if __name__ == "__main__":
    test(channel = 0, time = 0.1)
    