#from ps178x import PS178x
# Frequency counter
from freqcounter import FreqTask
from numpy import *
import time
import visa

#Pulse generator
gpib = visa.instrument("GPIB::15")


# init frequency reader
ts = FreqTask(2,1)

data = []


## ac/dc
for dt in linspace(0, 1000,160):
    gpib.write("DLAY 2,0,%.2e"%(dt*1e-9))
    time.sleep(0.1)
    a = 0
    for i in xrange(1):
        a = a + ts.read()
    row = [dt , a/1.]
    data.append(row)
    savetxt('temp.txt',data, fmt='%.4e', delimiter = ", ")
    print row

print "File number (0 for new one) -> ",
n = int(input())    
savetxt('timescan-%03d.txt'%n,data, fmt='%.4e', delimiter = ", ")

del ts