""" DAQ Scope

Use any NiDaq as a simple realtime scope
"""

import visa
from matplotlib import pylab as pl
import time

## Import latest version of farsi-lab
import sys
sys.path.append("C:\\dropbox\\Gaeta-lab\\farsilab")
sys.path.append("D:\\Dropbox\\Gaeta-lab\\farsilab")

from control.inst_panel import InstrumentApp

from control.daq import InputTask

def init():
    global apd
    apd = visa.SerialInstrument("COM3", baud_rate = 28800)
    time.sleep(2)
    

    
init()

app = InstrumentApp()
app.addBotton("Toggle Trigger Mode", setT1)

app.addColumn()
app.addPlotPanel("Tec1 (start/stop)", readTec, 0.3, multichannel = True,
                 before_callback = apd.write('A\n'),
                 after_callback = apd.write('0\n'))

app.MainLoop()
