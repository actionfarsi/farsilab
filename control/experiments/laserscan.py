""" Scan with the laser and record from the scope """

import visa
from matplotlib.pylab import *
from scipy.io import savemat
import os, re
from time import sleep

def readscope():
    ## ask for data
    a = scope.ask('curve?')
    data = [int(i) for i in a.split()[1].split(',')]

    ## ask for 
    a = scope.ask('horizontal:main:scale?')
    scale = float(a.split()[-1])
    t = linspace(0,10,len(data))*scale
    
    return t,a

if __name__ == "__main__":

    ## Init the scope
    scope = visa.Instrument("GPIB::1")

    ## Init and verify device
    scope.write('SELECTED DEVICE CLEAR')
    print scope.ask('*idn?')
    
    ## Set Encoding do ascii
    scope.write('data:encdg ascii')
    ## Be Sure transfer all the points
    scope.write('data:stop 4000')
    
    
    ## Init the laser (AGILENT)
    laser = visa.Instrument("GPIB::20")
    laser.write('SELECTED DEVICE CLEAR')
    print laser.ask('*idn?')
    
    laser.write('WAv:SWEEP 0')
    sleep(0.5)
    laser.write('WAV:SWEEP:START 1510e-9')           # <---- Set Wavelength
    laser.write('WAV:SWEEP:MODE man')     # <---- Set step
    laser.write('WAV:SWEEP:STOP 1600e-9')
    laser.write('WAV:SWEEP:STEP 1e-9')    # <---- Set step
    laser.write('WAv:SWEEP 1') # Start the sweep
    sleep(0.5)
    
    laser_step = lambda : laser.write('WAV:SWEEP:STEP:NEXT')
    laser_wl = lambda: laser.ask_for_values('WAV?')[0]
    
    filename = "delay"
    i = 1
    freqfile = open("delayvsfreq-"+filename+str(i)+".txt", 'w')
    freqfile.write("## Delay\tFreq\n")
    
    for j in xrange(20):
        time, data = readscope()
        freq = laser_wl()
        print i, freq
        savemat(filename+"%d"%i+ '.mat',
                {'data':data, 'time':time , 'freq':freq},
                oned_as='row')
        freqfile.write("%i\t%f\n"%(i,freq*1e9))
        i += 1
        laser_step()
        sleep(0.2)
    freqfile.close()
    
        
        
    