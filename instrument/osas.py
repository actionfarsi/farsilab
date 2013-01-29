""" OSA Controller

:date: 31 Oct 2012
:author: Alessandro Farsi

ANDO GPIB-4

""" 

import time
from visa import Instrument
from scipy.io import savemat
from numpy import savetxt
from matplotlib import pylab

## Instrument and address
instrument_list = {'ANDO': 4}

addr = instrument_list['ANDO']

## If using Usb2Gpib
inst = Instrument('GPIB::%d'%addr)


## ANDO 
## Read command LDATA, LDATB, LDATC
##

raw_data = inst.ask('LDATA').split(',')
n = raw_data[0]
data = [float(i) for i in raw_data[1:]]

assert len(data) != n

## savefile
pylab.plot(data)
pylab.show()
namefile = raw_input('Save data in file (name) -> ')
savetxt(namefile + '.txt', data)
