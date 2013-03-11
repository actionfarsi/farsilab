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
instrument_list = {'ANDO': 4,
                   'HP8563': 18,
                   'AGILENT': 25,}

addr = instrument_list['AGILENT']

## If using Usb2Gpib
inst = Instrument('GPIB::%d'%addr)

## If using pixlogic
## Set the right com
#
# inst = Instrument('COM6')
# inst.write('++ %d'%addr)

def andoAskData():
    """
 ANDO 
 Read command LDATA, LDATB, LDATC

    """
    raw_data = inst.ask('LDATA').split(',')
    n = raw_data[0]
    data = [float(i) for i in raw_data[1:]]

    assert len(data) != n
    return data

    
def Hp8563AskData():
    """
 HP Spectrum Analyzer
 Read command TRA, TRB

    """
    raw_data = inst.ask('TRA').split(',')
    n = raw_data[0]
    data = [float(i) for i in raw_data[1:]]

    assert len(data) != n
    return data

def AgilentAskData():

    raw_data = inst.ask('TRACE? tra').split(',')
    n = raw_data[0]
    data = [float(i) for i in raw_data[1:]]

    assert len(data) != n
    return data
    
## savefile
data = AgilentAskData()
pylab.plot(data)
pylab.show()
namefile = raw_input('Save data in file (name) -> ')
savetxt(namefile + '.txt',data)
