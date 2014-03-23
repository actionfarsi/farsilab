""" Laser Scan """

from time import sleep

## Parameters
range = ( 1510, 1590)
sample_rate = 100e3
speed = 5 # nm/s
step_size = 0.01 #nm
step_time = 0.1


## Init GPIP
import visa
gpib = visa.instrument("GPIB::20") # Set Laser Address

## Init NIDAQmx
import daq

def scan_and_read( w_range,
                  step_time, step_size, samples_per_step,
                  mode = "step",):
    ## Setup laser
    pre = "wav:sweep:"
    gpib.write(pre + "MODE STEP")
    gpib.write(pre + "START %f nm"%w_range[0])
    gpib.write(pre + "STOP %f nm"%w_range[1])
    #gpib.write(pre + "SPEED %fnm/s"%speed)
    gpib.write(pre + "STEP %f nm"%step_size)
    gpib.write(pre + "DWELL %f "%step_time)

    ## Set the laser at 0
    gpib.write("wav %f nm"%range[0])

    sleep(2)

    total_samples = ((range[1] - range[0]) /step_size * samples_per_step)

    physical_channel = "Dev2/ai0"      # Physical Channel: AI0 on Dev1

    ## First create the task and get a handle to the task 
    ## that will be used for all subsequenct operations
    voltage_task = daq.InputTask('Dev2')
    voltage_task.add_analog_voltage_channel(physical_channel)
    voltage_task.configure_sample_clock_timing(1.*samples_per_step/step_time,
                                                source='',
                                                sample_mode=DAQmx_Val_FiniteSamps,
                                                samples_per_channel = total_samples)
                                        
    ## Set trigger from laser to NIdaq 
    voltage_task.set_digital_trigger("/Dev2/PFI0")

    ## Start acquisition
    voltage_task.start()
    gpib.write("WAV:SWEEP:STATE 1")

    ## Start tdc
    data = []
    samples_read = 0
    while len(data) < total_samples:
        data.extend(voltage_task.read_analog_float64())
        print "%4.2f"%(1.*len(data)/total_samples)
        
    ## Save data
    print len(data)
    return data

from matplotlib.pylab import *
from scipy.io import savemat 

data = scan_and_read(range, step_time, step_size, samples_per_step = 10)

print "File name (matlab file) -> ",
n = raw_input() 

savemat(n + ".mat",{'data': data, 'range': range, 'speed': speed})
#np.savetxt("test.txt",data)
plot(linspace(range[0],range[1],len(data)), data)
show()