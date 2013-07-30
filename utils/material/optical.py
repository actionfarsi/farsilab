from numpy import *
from scipy import interpolate

dir = "E:\\Documents\\Cornell\\Gaeta Lab\\workbench\\res\\material\\"

C = 3e8  # Light Speed
l = linspace(0.5, 2.5, 100)*1e6   # Wavelenght

def n_sell(coeffs, l):
    return sqrt(sum(array([ cs[0]*l**2 / (l**2-cs[1]**2) for cs in coeffs]), 0) + 1)
    
def disp_w(n, l):
    beta = (2 * pi / n * C / l)[::-1]
    o = (2 * pi * C / l)[::-1]
    
    beta_i = interpolate.splrep(beta, o, k= 5)
    return (o,interpolate.splev(o,beta_i, der = 2))

def beta2(disp, l):
    return  - disp * l**2/(2 * pi * C)
    
class Bunch():
    pass
    


########      Silicon crystal        #########
si = Bunch()
# Sellmeier - http://refractiveindex.info/?group=CRYSTALS&material=Si  ( Handbook of Optics, 3rd edition, Vol. 4. McGraw-Hill 2009 )
si.sellmeier = [(10.6684293, 0.301516485), (0.003043475,1.13475115), (1.54133408, 1104.0)]
si.ntab = [l, n_sell(si.sellmeier,l)]

########      Amorphous Silicon      #########
a_si = Bunch()
# n from table SOPRA N&K Database
temp = loadtxt(dir + "CRYSTALS_a-Si_sopra_siam1.txt", skiprows = 1, unpack = True)   # l, n, k
a_si.ntab = [temp[0]*1e-6, temp[1]+1j*temp[2] ]

########      Silicon dioxide        #########
si_d = Bunch()
#  Gorachand Ghosh. Dispersion-equation coefficients for the refractive index and birefringence of calcite and quartz crystals, Opt. Commun. 163, 95-102 (1999) doi:10.1016/S0030-4018(99)00091-7
si_d.sellmeier = [(0.28604141, 0), (1.07044083, 1.00585997e-2),(1.10202242, 100)]
si_d.ntab = [l, n_sell(si_d.sellmeier, l)]


from matplotlib.pylab import *

o,b = disp_w(si_d.ntab[1],si_d.ntab[0])
plot(o,b)
show()