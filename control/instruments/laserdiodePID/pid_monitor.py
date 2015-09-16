import visa
from matplotlib.pylab import *
import matplotlib.animation as animation


ins = visa.Instrument("COM3", baud_rate=9800)

t = array([ (0.,0.,0.) ]*50)


fig, ax = subplots()
line = ax.plot(t)
axhline(50, color= 'k')
ylim(40,80)
print line

def animate(i):
    e1,e2,out = ins.read_values()
    t[:-1] = t[1:]
    t[-1] = (e1,e2,out+45)

    line[0].set_ydata(t.T[0])  # update the data
    line[1].set_ydata(t.T[1])  # update the data
    line[2].set_ydata(t.T[2])  # update the data
    
    return line,


while True:
    
    ani = animation.FuncAnimation(fig,func = animate, interval=25)

    show()
    