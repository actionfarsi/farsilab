"""
Counts edges for a given time

"""

from freqtask import FreqTask
from time import clock,sleep
from matplotlib.pylab import *
from matplotlib import animation

## Parameters
sampling_time = 0.001
time_scale = 4 ## Seconds

t = arange(time_scale/sampling_time)
counts = zeros(t.size)  ## Where the data goes

## Init measurement and plot
task = FreqTask(channel = 2, #channel
                 sampling_time = sampling_time) # (inverse of sampling rate))

## Create figure
fig = figure()
ax = gca()
line, = plot(counts, 'r-')
xlabel('Time')
title('Count rate')
ylim(0,300000)

## Function in the loop
def update_counts(n):
    ## Measurement
    counts_r = task.read(300)
    counts[:] = r_[counts[len(counts_r):], counts_r]
    
    ## Update plot
    line.set_data(t,counts)
    fig.canvas.draw()
    
## Start the animation, that is a loop with callback 
line_ani = animation.FuncAnimation(fig, update_counts, repeat = True,
                                        blit=False)    
    

show()
