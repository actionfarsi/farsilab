""" OSA Controller

:date: 31 Oct 2012
:author: Alessandro Farsi

ANDO GPIB-4

""" 

import time
from visa import Instrument
from scipy.io import savemat
from numpy import savetxt, linspace, c_
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
#inst = Instrument('COM5')
#inst.write('++addr %d'%addr)

def andoAskData():
    """
 ANDO 
 Read command LDATA, LDATB, LDATC

    """
    raw_data = inst.ask('LDATA').split(',')
    n = raw_data[0]
    data = [float(i) for i in raw_data[1:]]

    assert len(data) != n
    return linspace(0,n, n), data

    
def Hp8563AskData():
    """
 HP Spectrum Analyzer
 Read command TRA, TRB

    """
    raw_data = inst.ask('TRA').split(',')
    #n = raw_data[0]
    data = [float(i) for i in raw_data[1:]]

    assert len(data) != n
    return linspace(0,n, n), data

def AgilentAskData():

    raw_data = inst.ask('TRACE? tra').split(',')
    data = [float(i) for i in raw_data]
    n = len(data)#raw_data[0]
    #assert len(data) == n
    
    w_start = inst.ask("sens:wav:star?")
    w_stop = inst.ask("sens:wav:stop?")
    w = linspace(float(w_start), float(w_stop), n) 
    return w, data

print inst.ask("*IDN?")
## savefile
w, data = AgilentAskData()
pylab.plot(w, data)
pylab.show()
namefile = raw_input('Save data in file (name) -> ')
savetxt(namefile + '.txt', c_[w, data] )
