## Detector analisys ##
""" Detector analisys

    Loops over properties and measures counts using FreqTask
"""


# Voltage Supply
from ps178x import PS178x
# Frequency counter
from freqtask import FreqTask
# GPIB wrapper module
import visa

from numpy import *
import time

## Initialization instruments (be sure that the addresses are correct)

gpib = visa.instrument("GPIB::15")  # Pulse generator

vs = PS178x()                       # Voltage supply (from original python wrapper)
vs.Initialize(4, 9800)              # Open a serial connection
vs.SetRemoteControl()

ts = FreqTask(6,0.5)                # Frequency reader task from NIDAQmx

data = []                           # Init list to save the results into

## relevant properties to change
# Delay     - gpib.write("DLAY 2,0,%.2e"%(dt*1e-9))
# Reprate   - gpib.write("TRAT %e"%rep)
# Amplitude - gpib.write("LAMP 1,%.2f"%ac)
# DC Bias   - vs.SetOutVoltage(dc)

## TODO smart way to write the loop

## List of values to loop in
rac = [5]#linspace(1,5,10)
rdc = [59.5]#linspace(59,62,40)
rdt = [3,4,6,8,10,12,15,18,20,25,30,35,40,45,50,60,70] #3,
rrep = [50e3,100e3,200e3,300e3,400e3,500e3,
        700e3,900e3,1e6,1.5e6,2e6,2.5e6]

## Loop(s) on the properties to change
for dt in linspace(165,195,200): #rdt:
    gpib.write("DLAY 2,0,%.2e"%(dt*1e-9))

    ## Inner-most group (read and save)
    time.sleep(0.01)                                          # Wait a bit to let the system do the changes
    row = [dt , ts.read()]                                    # Save the row of parameter
    data.append(row)                                          # Append the row to the final data
    savetxt('temp.txt',data, fmt='%.4e', delimiter = ", ")    # save temp file (in case it gets stuck)
    print row

## Save output
print "File number (carefull to not overwrite) -> ",
n = int(input())    
savetxt('fulldown-%03d.txt'%n,data, fmt='%.4e', delimiter = ", ")

## Free resurces
gpib.write("LAMP 1,%.2f"%0)
vs.SetLocalControl()
del vs
del ts
del gpib
