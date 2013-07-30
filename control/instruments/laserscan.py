""" Laser Scan """

from time import sleep

## Parameters
range = ( 1510, 1590)
sample_rate = 100e3
speed = 5 # nm/s
total_samples = ((range[1] - range[0]) /speed * sample_rate )

## Init GPIP
import visa
gpib = visa.instrument("GPIB::20") # Set Laser Address

## Init NIDAQmx
from ctypes import *
dll = windll.LoadLibrary("nicaiu.dll")
from nidaq import *   # Contains constants

## Setup laser
pre = "wav:sweep:"
gpib.write(pre + "MODE CONT")
gpib.write(pre + "START %f nm"%range[0])
gpib.write(pre + "STOP %f nm"%range[1])
gpib.write(pre + "SPEED %fnm/s"%speed)
## Set the laser at 0
gpib.write("wav %f nm"%range[0])

sleep(2)

## Prepare acquisition
## -------------------
n_samples = int(50000)                           # Buffer size (only one reading at time)
#sampling_time = sampling_time

handle = c_int(0)                                 # DAQmx TaskHandle
name = "Voltage reading"        # Task Name generated on the fly
buffer = (c_double * n_samples)()              # Buffer on disk for acquisition

physical_channel = "Dev2/ai0"      # Physical Channel: AI0 on Dev1
channel_name = ""                                 # Useless

## First create the task and get a handle to the task 
## that will be used for all subsequenct operations
dll.DAQmxCreateTask(name, byref(handle))
dll.DAQmxCreateAIVoltageChan(handle, physical_channel, channel_name,
                    DAQmx_Val_RSE , # Ground Reference 
                    c_double(-5),c_double(2), # Min Max in V
                    DAQmx_Val_Volts, None)

dll.DAQmxCfgSampClkTiming(handle, "",
                            c_double(sample_rate), ## Samples per s
                            DAQmx_Val_Rising,
                            DAQmx_Val_FiniteSamps,
                            c_ulonglong(int(total_samples)))
                            #c_ulonglong(n_samples))                    
                    
## Set trigger from laser to NIdaq 
dll.DAQmxCfgDigEdgeStartTrig(handle, "/Dev2/PFI0",DAQmx_Val_Rising)

## Start acquisition
dll.DAQmxStartTask(handle)
gpib.write("WAV:SWEEP:STATE 1")

## Start tdc
data = []
samples_read = 0
while samples_read < total_samples:
    ## Read in chunks
    bit_read = c_int()
    dll.DAQmxReadAnalogF64(handle, -1, # numSamps
                        c_double(3),  # Timeout
                        DAQmx_Val_GroupByChannel,
                        byref(buffer), n_samples, # Size of buffer
                        byref(bit_read), None)
    samples_read += bit_read.value
    data.extend(buffer[:bit_read.value])
    print "%4.2f"%(1.*samples_read/total_samples)
    
## Save data
print len(data)

from matplotlib.pylab import *
from scipy.io import savemat 
print "File name (matlab file) -> ",
n = raw_input() 

savemat(n + ".mat",{'data': data, 'range': range, 'speed': speed})
#np.savetxt("test.txt",data)
plot(linspace(range[0],range[1],len(data)), data)
show()