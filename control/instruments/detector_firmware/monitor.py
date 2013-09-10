# Tec Station

import visa
from matplotlib import pylab as pl
import matplotlib.animation as animation


apd = 0

def init():
    apd = visa.Instrument("COM13")

    # start
    apd.write('A')

hist_size = 10

tec1_hist = [ [0]*hist_size, [0]*hist_size, [0]*hist_size ]
tec2_hist = [ [0]*hist_size, [0]*hist_size, [0]*hist_size ]


tec1_lines = 0
tec1_lines = 0
    

def animate(i):
    # Read
    #tec1 = apd.read().split()
    #tec2 = apd.read().split()
    tec1 = ["T", "1", "TT", "2", "re","3"]
    tec2 = ["T", "1", "TT", "2", "re","3"]
    
    
    tec1_hist[0].append(float(tec1[1]))
    tec1_hist[0] = tec1_hist[0][1:]
    tec1_hist[1].append(float(tec1[3]))
    tec1_hist[1] = tec1_hist[1][1:]
    tec1_hist[2].append(float(tec1[5]))
    tec1_hist[2] = tec1_hist[2][1:]
    
    
    for i in [0,1]:
        tec1_lines[i][0].set_ydata(tec1_hist[i])
        #tec2_lines[i].set_ydata(tec2_hist[i])
        
    return tec1_lines[0]

fig = pl.figure()

tec1_lines = [pl.plot(tec1_hist[0]), pl.plot(tec1_hist[1])]
tec2_lines = [pl.plot(tec2_hist[0]), pl.plot(tec2_hist[1])]

ani = animation.FuncAnimation(fig, animate, interval = 500, blit=True)
pl.show()

raw_input()