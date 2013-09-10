# Tec Station

import visa
from matplotlib import pylab as pl
import matplotlib.animation as animation

import time

## Import latest version of farsi-lab
import sys
sys.path.append("C:\\Users\\Action Farsi\\Documents\\farsi-lab")

from control.inst_panel import InstrumentApp

apd = 0

def init():
    global apd
    apd = visa.SerialInstrument("COM13", baud_rate = 28800)
    time.sleep(2)

    apd.write('A\n')

    

hist_size = 10

tec1_hist = [ [0]*hist_size, [0]*hist_size, [0]*hist_size ]
tec2_hist = [ [0]*hist_size, [0]*hist_size, [0]*hist_size ]


tec1_lines = 0
tec1_lines = 0
    

def readTec():
    # Read
    try:
        apd.clear()
        tec1 = apd.read().split()
        tec2 = apd.read().split()
        
        print "TEC1 ",
        for s in tec1[6:]:
            print s, ' ',
        print '\nTEC2 ',
        for s in tec2[6:]:
            print s, ' ',
        print ''
    
        tec1_hist[0].append(float(tec1[1]))
        tec1_hist[0] = tec1_hist[0][1:]
        tec1_hist[1].append(float(tec1[3]))
        tec1_hist[1] = tec1_hist[1][1:]
        tec1_hist[2].append(float(tec1[5]))
        tec1_hist[2] = tec1_hist[2][1:]
        
        tec2_hist[0].append(float(tec1[1]))
        tec2_hist[0] = tec2_hist[0][1:]
        tec2_hist[1].append(float(tec1[3]))
        tec2_hist[1] = tec2_hist[1][1:]
        tec2_hist[2].append(float(tec1[5]))
        tec2_hist[2] = tec2_hist[2][1:]
        
    except:
        pass
    
    return [ tec1_hist[0], tec1_hist[1],
             tec2_hist[0], tec2_hist[1]]
    

def setT1(t):
    apd.write('t%f\n'%(float(t) + 273))

def setT2(t):
    apd.write('T%f\n'%(float(t) + 273))
    
def setPID1(t):
    t = t.split(',')
    apd.write('kP%s \nkI%s \nkD%s'%(t[0], t[1], t[2]))
    
def setPID2(t):
    t = t.split(',')
    apd.write('KP%s \nKI%s \nKD%s'%(t[0], t[1], t[2]))

def powerTec():
    return [ tec1_hist[2], tec2_hist[2] ]
    
init()

app = InstrumentApp()
app.addValueCtr("Set T1 (C)", setT1, default = "-20.1")
app.addValueCtr("Set T2 (C)", setT2, default = "-20.1")

app.addValueCtr("Set PID1", setPID1, default = "1,1,1")
app.addValueCtr("Set PID2", setPID2, default = "1,1,1")

app.addColumn()
app.addPlotPanel("Tec1 (start/stop)", readTec, 0.3, multichannel = True)
app.addColumn()
app.addPlotPanel("Plot Power", powerTec, 0.3, multichannel = True)

app.MainLoop()
