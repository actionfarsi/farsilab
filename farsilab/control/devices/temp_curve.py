# coding: utf-8
get_ipython().magic('pylab')
x = linspace(270,400,200)
r = 15 * exp(4100 *(1/x-1/298.15))
plot(r,x)
plot(x,r)
plot(x,r/(r+5))
plot(x,r/(r+15))
plot(x,r/(r+3))
plot(x,3/(r+3))
x = linspace(270,400,30)
r = 15 * exp(4100 *(1/x-1/298.15))
plot(x,3/(r+3))
show()
plot(x,3/(r+3))
plot(x,3/(r+3),'-')
plot(x,3/(r+3),'o-')
x
plot(x,1/(r+1),'o-')
plot(x,1/(r+1)*1064,'o-')
plot(x,1/(r+1)*1064,'o-')
plot(x,10/(r+10)*1064,'o-')
plot(x,6.8/(r+6.8)*1064,'o-')
plot(x,6.8/(r+6.8)*1064,'o-')
r
v = 6.8/(r+6.8)*1064
v
v.astype(int)
x
x.astype(int)
