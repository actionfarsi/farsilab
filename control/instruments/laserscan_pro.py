""" Laser Scan """

from time import sleep

## Parameters
range = ( 1549.25, 1549.35)
sample_rate = 100e3
speed = 5 # nm/s
step_size = 0.001 #nm
step_time = 0.3


## Init GPIP
import visa
gpib = visa.instrument("GPIB::20") # Set Laser Address

## Init NIDAQmx
import daq

def scan_and_read( w_range,
                  step_time, step_size,
                  mode = "step",):
    ## Setup laser
    pre = "wav:sweep:"
    gpib.write(pre + "MODE STEP")
    gpib.write(pre + "START %f nm"%w_range[0])
    gpib.write(pre + "STOP %f nm"%w_range[1])
    #gpib.write(pre + "SPEED %fnm/s"%speed)
    gpib.write(pre + "STEP %f nm"%step_size)
    gpib.write(pre + "DWELI %f "%step_time)
    #gpib.write("TRIGGER:OUTPUT SWSTarted:")
    gpib.write("TRIGGER:OUTPUT STFINISHED")
    
    ## Set the laser at 0
    gpib.write("wav %f nm"%range[0])

    sleep(2)

    total_samples = ((range[1] - range[0]) /step_size )

    physical_channel = "dev2/ai0"      # Physical Channel: AI0 on Dev1

    voltage_task = daq.InputTask('Dev2')
    voltage_task.add_analog_voltage_channel(physical_channel, terminal_config = "rse")
     
    #voltage_task.configure_sample_clock_timing(1.*samples_per_step/step_time,
    #                                           source='',
    #                                           sample_mode=daq.DAQmx_Val_FiniteSamps,
    #                                           samples_per_channel = int(3000))
    
    ## Everytime recieve a step trig from the laser, generate a burst
    #triggering_task = daq.OutputTask('Dev2')
    #triggering_task.add_co_pulse_channel_time(lowTime = 0.01, highTime = 0.01)
    
    ## Syncronize reading with laser trigger
    voltage_task.configure_sample_clock_timing( .1,
                                                source="/dev2/PFI0",
                                                sample_mode=daq.DAQmx_Val_FiniteSamps,
                                                samples_per_channel = int((w_range[1] - w_range[0]) /step_size))
    
    
    ## Set trigger from laser to NIdaq 
    #voltage_task.set_digital_trigger("/Dev2/PFI0")

    ## Start acquisition
    voltage_task.start()
    gpib.write("WAV:SWEEP:STATE 1")

    ## Start tdc
    data = []
    samples_read = 0
    print "Total samples expected to read %d at reprate %.1e"%(voltage_task.samples_per_channel,
                                                                voltage_task.sample_rate)
    while len(data) < voltage_task.samples_per_channel:
        data.extend(voltage_task.read())
        sleep(0.4)
        print "%4.2f read"%(1.*len(data)/voltage_task.samples_per_channel)
        
    ## Save data
    print len(data)
    
    voltage_task.clear()
    
    return data

from matplotlib.pylab import *
from scipy.io import savemat 
from fitting import Parameter, fit

a = Parameter(-0.09 ,'a')
l0 = Parameter(1550, 'lo')
gamma = Parameter(0.001,'gamma')
y0 = Parameter(0.2, 'y0')

parameters = [a,l0,gamma, y0]
f = lambda x: a() /(1 + ((x-l0())/gamma())**2) + y0()

def scan_and_fit(l, step_size = step_size):
    range = r_[l-0.015, l+0.015]
    y = scan_and_read(range,
                      step_time, step_size)
                        
    x = linspace(range[0],range[1],len(y))
    ## Expected values for parameters
    l0.set(l)
    y0.set(amax(y))
    a.set(amin(y)-amax(y))
    
    fit(f,parameters, x, y, 1,)
    figure()
    title("$\lambda_0 = %.4f$"%l0())
    xt = linspace(range[0],range[1],100) 
    plot(x,y,'o')
    plot(xt, f(xt),'-')
    
    return l0(), gamma()
    
scan_and_fit(1549.31)   
#data = scan_and_read(range, step_time, step_size, samples_per_step = 10)
#data3 = scan_and_read(range, step_time, step_size, samples_per_step = 10)

#print "File name (matlab file) -> ",
#n = raw_input() 

#savemat(n + ".mat",{'data': data, 'range': range, 'speed': speed})
#np.savetxt("test.txt",data)
#plot(linspace(range[0],range[1],len(data)), data)

show()