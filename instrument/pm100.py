""" PM100 Control 

:date: 31 Oct 2012
:author: Alessandro Farsi
"""

import time
from visa import SerialInstrument
#from instrument_panel import InstrumentApp

## Connectiong to the instrument
pm = SerialInstrument("COM5")
pm.term_chars = '\t\n'


def read():
	## Ask for power and convert it to a float number
    return float(pm.ask(":POWER?"))

import instserver
server = instserver.server("192.168.5.113", 9998)

data = [0,0,0,0,0,0,0,0,0,0,0]
wait = 0.3

while True:                              # Never stop the measurement
	time.sleep(wait)
	# Shift the history
	data[1:] = data[:-1]
	# Read the new value and put as first of the history
	data[0] = read()
	print data[0]
	# Place list of values to the server so it can be broadcasted
	# (list of list)
	server.values = [data]
