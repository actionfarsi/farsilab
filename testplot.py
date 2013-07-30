from matplotlib.pylab import *

x = linspace(0,10,100)

plot(x,x**0.7)
plot(x,sin(x),'.')
plot(x,cos(x),'-')

print "tada"

show()