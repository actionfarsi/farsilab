""" PM100 Control 

:date: 31 Oct 2012
:author: Alessandro Farsi
"""


from visa import Instrument
#from instrument_panel import InstrumentApp


pm = Instrument("COM3")

def read():
    return float(pm.ask("POWER?"))

import instserver
server = instserver.server("", 9998)

data = [0,0,0,0,0,0,0,0,0]
wait = 0.5

while True:                              # Never stop the measurement
        step = step + 1
        # print "It %4d"%step,           # Remove comment to have visual feedback of measurement (for long wait times)
        for i in range(7):
            time.sleep(1.* wait/7)
            #print '.',
        #print ""
        s = '|'.join([" CH%d: %7.1f (%7.3f) "%(ch[k],(dats[k])[0],average(dats[k])) for k in xrange(len(ch)) ])
        data[:-1] = data[1:]
        data[-1] = read()
        print data
        server.values = dats
    
#app = InstrumentApp()
#app.addButtonValue("Read Power", read)

