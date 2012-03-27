## Breakdown 

# Voltage Supply
from ps178x import PS178x
# Frequency counter
from freqcounter import FreqTask
from numpy import *
import sys, os, time
from matplotlib import pylab as pl

# init voltage supply
vs = PS178x()

vs.Initialize(3, 9800) # Open a serial connection

vs.SetRemoteControl()
vs.SetMaxVoltage(72)
vs.SetOutVoltage(40)
vs.TurnPSOn()

# init frequency reader
ts = FreqTask(2,1)

data = []

for voltage in linspace(61.,62.5,100):
    vs.SetOutVoltage(voltage)
    time.sleep(0.1)
    row = [voltage, ts.read()]
    data.append(row)
    print row
vs.SetOutVoltage(40)

print data

#files = os.listdir(path)
print "File number (0 for new one) -> "
n = int(input())
if n == 0:
    while 'breakdown-%03d.txt'%n in listdir(path):
        n = n+1
    
savetxt('breakdown-%03d.txt'%n,data, fmt='%.4e', delimiter = ", ")

# Free resurces
vs.SetLocalControl()
del ts
del vs



pl.plot(data[1],data[0])
pl.semilogy()
pl.show()