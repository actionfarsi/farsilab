## Very simple matplotlib / instrument_panel based plotter and logger
## Connect and read

import sys
sys.path.append(r"C:\dropbox\Gaeta-lab\farsilab")  # Append farsilab library

# Import from farsilab
from control import inst_panel
from numpy import *

data = zeros(100)
log_file = None

def acquire():
    return random.random(15)

def plotData():
    d = acquire()
    try:
        n = len(d)
    except:
        n = 1
        
    if len(data)< n:
        global data
        data = zeros(4*n)
    
    data[:-n] = data[n:]
    data[-n:] = d
    
    if log_file:
        try:
            for value in d:
                log_file.write("%f\n"%value)
            
        except:
            log_file.write("%f\n"%d)
            
    return [data]
    

## Connect to COM
def connectCom(com):
    import visa
    instrument = visa.Instrument("COM"+com)
    global acquire
    acquire = instrument.read_values
    print "Connected to COM"+com
    
## Connect to VISA
## Connect to Remote

def toggleLog(filename):
    global log_file
    if log_file:
        log_file.close()
        log_file = None
    else:
        log_file = open(filename,'w')
        print "Started logging"
    

## Init the app
app = inst_panel.InstrumentApp("Logger","Logger\n Connect to any COM, VISA \nor TCIP and plot the values")
app.addValueCtr("Connect to com ", connectCom, default = "1")
app.addValueCtr("LOG", toggleLog, "log.txt")
app.addColumn()
app.addPlotPanel("Start/stop", plotData, multichannel = True, timed = 0.1)
app.MainLoop()
