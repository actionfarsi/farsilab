import visa
from numpy import *
from matplotlib.pylab import *

ins = visa.Instrument('com5')
ins.write('++addr 15')

data = []

ins.write('form4')
try:
    ins.write('outpform')
    while True:
        data.append( ins.read_values())
except:
    pass


plot(array(data))
show()
print 'name file: ',
name = raw_input()
savetxt(name + '.txt', array(data))