import visa
from numpy import *
from matplotlib.pylab import *

from instrument_panel import InstrumentApp
#ins = visa.Instrument('com5')
#ins.write('++addr 15')

data = []

def measure():
    global data
    data = []

    ins.write('form4')
    try:
        ins.write('outpform')
        while True:
            data.append( ins.read_values())
    except:
        pass
        
    return data

def save(filename):
    savetxt(filename + '.txt', array(data))
    
if __name__ == '__main__':
    app = InstrumentApp(description = "Measure from 8722es")
    
    app.addPlotPanel("Measure", measure)
    app.addValueCtr("Save", save, "temp")
    
    app.MainLoop()