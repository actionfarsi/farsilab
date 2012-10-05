""" Laser Scan """

## Parameters
sample_rate = 100e3
speed = 5 # nm/s
total_points = 100 /speed * sample_rate

## Init GPIP
import visa
gpib = visa.instrument("GPIB::20") # Set Laser Address

## Init NIDAQmx
dll = windll.LoadLibrary("nicaiu.dll")
from nidaq import *   # Contains constants

## Setup laser
pre = "WAVELENGTH:SWEEP:"
gpib.write(pre + "START 1500")
gpib.write(pre + "STOP 1600")
gpib.write(pre + "SWEEP %fnm/s"%speed)

## Prepare acquisition
## -------------------
n_samples = 50000                                  # Buffer size (only one reading at time)
sampling_time = sampling_time

handle = c_int(0)                                 # DAQmx TaskHandle
name = "Voltage reading"        # Task Name generated on the fly
buffer = (c_double * n_samples)()              # Buffer on disk for acquisition

physical_channel = "Dev1/ai0"      # Physical Channel: DI0 on Dev1
channel_name = ""                                 # Useless

## First create the task and get a handle to the task 
## that will be used for all subsequenct operations
dll.DAQmxCreateTask(name, byref(handle))
dll.DAQmxCreateAIVoltageChan(handle, physical_channel, channel_name,
                    -1, # Ground Reference 
                    c_double(0),c_double(5). # Min Max in V
                    DAQmx_Val_Volts, None)

dll.DAQmxCfgSampClkTiming(handle, "", sample_rate, ## Samples per s
                            DAQmx_Val_Rising, DAQmx_Val_FiniteSamps,
                            n_samples)                    
                    
## Set trigger from laser to NIdaq 
dll.DAQmxCfgEdgeStartTrig(handle, "/Dev1/PFIO",DAQmx_Val_Rising)

## Start acquisition
dll.DAQmxStartTask(handle)
gpib.write("WAVELENGTH:SWEEP:START")

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
    samples_read += bit_read
    data.append(float(buffer))
    print "%f3.1"%(1.*samples_read/total_samples)
    
## Save data
print data