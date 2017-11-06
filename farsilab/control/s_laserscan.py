# -*- coding: utf-8 -*-
"""
Laser Scan (continuos)


"""
from time import sleep
import warnings
## Agilent Laser Instrument
#from pyvisa import constants
#from Agilent8164 import Agilent8164

import numpy as np
from scipy.io import savemat

## Init NIDAQmx
import daq

from visa import ResourceManager
from lantz import Q_

# GUI import
from PyQt4 import QtGui, QtCore  
import pyqtgraph as pg


## Parameters
options = { 'laser_gpib': "GPIB::20",#1600 GPIB::20 1550 GPIB::4 #1400 GPIB::1919
    'daq_channel': "ai1",
    'wrange': (1565,1615),
    'offsetWL': 0.00,
    'sample_rate': 5e3,
    'speed': .5 } # nm/s (only options are .5 5 40)


def laser_scan(laser_gpib = "GPIB::19", #1600 GPIB::20 1550 GPIB::4 #1400 GPIB::19
                daq_channel = "dev1/ai1",
                wrange = (1560,1600),
                offsetWL = 0.00,
                sample_rate = 5e3,
                speed = .5, # nm/s (only options are .5 5 40)
                plot_hook = None):
    

    # calculate the output
    total_samples = ((wrange[1] - wrange[0]) /speed * sample_rate )
    wl = np.linspace(wrange[0],wrange[1], total_samples)
    print('Total Samples {:}'.format(total_samples))
    ## Configure task
    voltage_task = daq.InputTask()
    voltage_task.add_analog_voltage_channel(daq_channel,
                                        terminal_config = "rse")
                                        
    voltage_task.configure_sample_clock_timing( sample_rate,
                                            source=b"",
                                            sample_mode=daq.DAQmx_Val_FiniteSamps,
                                            samples_per_channel = int(total_samples))

    ## Set trigger from laser to NIdaq 
    voltage_task.set_digital_trigger(b"PFI0")
    daq.nidaq.DAQmxSetReadReadAllAvailSamp(voltage_task.task_handle, daq.bool32(True))

    ## Connect to laser
    rm = ResourceManager()
    inst =  rm.open_resource(laser_gpib)
    sleep(.1)   
    print('The identification of this instrument is : ' + inst.query("*idn?"))

    ## configure and set to start wl
    inst.write("wav %f nm"%wrange[0])
    inst.write("wav:sweep:start %f nm"%wrange[0])
    inst.write("wav:sweep:STOP %f nm"%wrange[1])
    inst.write("wav:sweep:speed %f nm/s"%(0.5))
    inst.write("TRIGGER:OUTPUT SWStart")
    inst.write("wav:sweep:mode Cont")
    sleep(5)
    

    with voltage_task: # start the task (to avoid lockdown of the nidaq in case of crash)
        ## Start acquisition
        voltage_task.start()
        ## Start scan
        inst.write("WAV:SWEEP:STATE 1")

        # To avoid warnings when the we rea
        warnings.filterwarnings('ignore', 'Read')
    
        ## reading loop. Scan is longer than a second, so we keep
        ## probing to have faster update

        samples_read = 0
        data_buffer = np.zeros(total_samples)
        while samples_read < total_samples:
            b = voltage_task.read()
            if len(b)> 0:
            	data_buffer[samples_read:samples_read+len(b)] = b

            # give an update
            print(len(b), samples_read/total_samples)
            if plot_hook is not None:
            	plot_hook(wl, data_buffer)

            samples_read += len(b)    
            sleep(.3)

    return wl, data_buffer


from scipy.io import savemat



if __name__ == "__main__":
    ## Switch to using white background and black foreground
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')

    app = QtGui.QApplication([])
    win = pg.GraphicsWindow()
    win.setWindowTitle('Laser Scan')

    win.show()
    pw = win.addPlot()
    pw.enableAutoRange()

    ## Prepare Plot
    scan_data = np.zeros(5), np.zeros(5)
    curve = pw.plot(scan_data[0], scan_data[1], pen = pg.mkPen('b', witdth=3))
    pw.addLine(y = 0)

    ## put data from global var to plot
    timer = pg.QtCore.QTimer()
    def update():
    	curve.setData(scan_data[0], scan_data[1])

    timer.timeout.connect(update)
    timer.start(100)

    ## put data into a global var
    def update_hook(wl, data):
	    global scan_data
	    scan_data = (wl, data)

    ## Start aquisition on a thread
    class LaserScan(QtCore.QThread):
        def __init__(self, options):
            QtCore.QThread.__init__(self)
            self.options = options

        def run(self):
            wl, data = laser_scan(plot_hook = update_hook, **self.options)
            pw.enableAutoRange()
            ## Add save file
            print ("File name (matlab file) -> ",)
            n = input() 
            savemat(n + ".mat", {'data': data, 'wl': wl})
            print('File saved')
    
    worker = LaserScan(options)
    worker.start()
    QtGui.QApplication.instance().exec_()


#print ("File name (matlab file) -> ",)
#n = input() 
# 
#savemat(n + ".mat", {'data': buffer, 'range': wrange,
#                     'speed': speed, 'wl': wl})
