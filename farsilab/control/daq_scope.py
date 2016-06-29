# -*- coding: utf-8 -*-
"""
Daq Scope

@author: Action Farsi
"""
import numpy as np
import warnings
## Agilent Laser Instrument
#from pyvisa import constants
#from Agilent8164 import Agilent8164

## Init NIDAQmx
import daq

# GUI import
from PyQt4 import QtGui, QtCore  
import pyqtgraph as pg


daq_channel = "ai0"
sample_rate = 10e3

task = daq.InputTask()
task.add_analog_voltage_channel(daq_channel,
                                terminal_config = "rse")

task.configure_sample_clock_timing(sample_rate,
                                   source=b"",
                                   sample_mode= 'continuous',
                                   samples_per_channel = int(sample_rate*10))

## Set trigger from laser to NIdaq
daq.nidaq.DAQmxSetReadReadAllAvailSamp(task.task_handle, daq.bool32(True))

def update():
    global data, curve, ptr1
    r_data = task.read()
    samples_read = len(r_data)
    data = np.roll(data, -samples_read)
    data[-samples_read:] = r_data
    curve.setData(data_x, data)




if __name__ == "__main__":
    app = QtGui.QApplication([])
    win = pg.GraphicsWindow()
    win.setWindowTitle('pyqtgraph example: Scrolling Plots')
    win.show()
    pw = win.addPlot()

    data = np.zeros(sample_rate*20)
    data_x = np.arange(len(data), dtype = np.float64) / sample_rate
    curve = pw.plot(np.arange(len(data), dtype = np.float64) / sample_rate, data )

    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(100)

    QtGui.QApplication.instance().exec_()

    #wl, data = laser_scan(**options)
    #plot(wl, data)
    #show()

#print ("File name (matlab file) -> ",)
#n = input() 
# 
#savemat(n + ".mat", {'data': buffer, 'range': wrange,
#                     'speed': speed, 'wl': wl})
