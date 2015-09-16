""" Laser Scan """


from time import sleep
import sys, os
from time import time,strftime, sleep

## Set the path to the farsilab directory (if not installed) #######
sys.path.append(r'C:\\dropbox\\Gaeta-lab\\farsilab\\')
sys.path.append(r'E:\\ActionDropbox\\Dropbox\\Gaeta-lab\\farsilab\\')
sys.path.append(r'E:\\farsilab\\')

from matplotlib.pylab import *


try:
    ## Init GPIP
    import visa
    ## Init NIDAQmx
    import control.daq  as daq 
except ImportError:
    error_log = error_log + "Import error: verify libraries\n"
    error_visa = True
 
try:    
    gpib_laser = visa.Instrument("GPIB::11") # Set Laser Address
    print gpib_laser.ask('*IDN?')
except e:
    print e
    error_log = error_log + "Laser not connected\n"
    error_visa = True


def scan_and_read(wl, step_time = 0.6,meas_time = 10):
    ## set laser at starting freq and wait
    gpib_laser.write("ch1:l=%f"%wl[0])
    sleep(15)
    
    physical_channel = "dev2/ai0"      # Physical Channel: AI0 on Dev1

    voltage_task = daq.InputTask('Dev2')
    voltage_task.add_analog_voltage_channel(physical_channel, terminal_config = "rse")
    
    data = []
    samples_read = 0
    
    for i,l in enumerate(wl):
        print l, 
        gpib_laser.write("ch1:l=%f"%l)
        print 1. * samples_read/len(wl) #ratio of scan progress
        sleep(step_time)
        log_time = strftime('%m-%d %H:%M:%S')
        data.append((log_time,l))
        sleep(meas_time)
        samples_read=samples_read+1
        
    ## Save data
    voltage_task.clear()
    return data
    
wl = linspace(1299,1302,30)
data = scan_and_read(wl,1.5)

from matplotlib.pylab import *
from scipy.io import savemat 
print "File name (matlab file) -> ",

f = open("Bw.txt",'w')
for log_time, wl in data:
    f.write("%s %.2f\n"%(log_time,wl))
f.close()
#savemat(n + ".mat",{'data': data, 'range': range, 'speed': speed})
#np.savetxt("test.txt",data,)
#plot(wl, data,'-o')
#show()