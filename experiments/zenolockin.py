""" Measurement 

 - Set up laser sweep (VISA)
 - Set up voltage acquisition (NiDAQ)
 - Open Shutter (NiDAQ)
 - Start sweep
 - Stop Shutter (NiDAQ)

The same trigger starts voltage acquisiton and shutter
 
"""

import sys
sys.path.append(r"D:\Cornell\farsilab")

import visa  ## PyVisa
import instrument.daq   ## PyDaq (from 

from numpy import *
from matplotlib import pylab as pl

## Init
laser_i = visa.Instrument('GPIB::10')

w_range = (1545, 1555)
sweep_time = 1

def run():
    ## Setup the sweep
    laser_i.write('TSWM1') # Continuous Trig
    laser_i.write('TSTAWL%8.3f'%w_range[0])
    laser_i.write('TSTPWL%8.3f'%w_range[1])
    laser_i.write('TSWEINT%5d'%sweep_time)
    laser_i.write('TWL%8.4f'%w_range[0])  # Set frequency at start
    
    ## Setup V acquisition task
    dev = daq.Device('Dev2')
    readvolt_t = daq.InputTask(dev)
    
    readvolt_t.add_analog_voltage_channel('ai2', terminal_config = 'rse')
    readvolt_t.configure_sample_clock_timing(sample_rate=10000,
                                             samples_per_channel=50000)
 
    ## Setup shutter pulse
    shutter_t = OutputTask(dev)
    shutter_t.configure_implicit_timing('finite', 1)  # One pulse
    shutter_t.add_co_pulse_channel_time('ao0', lowTime = 0., highTime = 3.)
    
    ## Use shutterpulse to start voltage acquisiton?
    
    ## Start the run
    shutter_t.start() # Open Shutter
    laser_i.write('TSGL') # Start Sweep
    readvolt_t.start() # Start acquisiton
    
    voltage = readvolt.read_analog_scalar_float64()
    wavelength = linspace(w_range[0],w_range[1], len(voltage) )# hopefully start and stop are synced
    
    return c_[wavelength, voltage]
    
if __name__ == '__main__':
    w,v = run()
    pl.plot(w,v)
    pl.show()
    
    
    
    
    