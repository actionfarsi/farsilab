""" Few Test routines for single photon detector based on Arduino

"""

import visa
from numpy import *
from matplotlib.pylab import *

com = visa.SerialInstrument("COM13")

def testTemperature():
    """ Test the temperature controller
    
    Start temperature test routine, read and plot results"""
    
    com.write('T') # Temperature test
    
    data = []
    
    try:
        while True:
            l = com.read()
            l = l.split()
            print l
            # Line must start with a 'T'
            if l[0] != 'T':
                break
            data.append(int(l[1]), int(l[2]), int(l[3]))
                
    except visa.TimeoutException:
        pass
        
    data = array(data)
    plot(data[0], data[1])
    plot(data[0], data[2])
    show()
    

