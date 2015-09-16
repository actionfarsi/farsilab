""" Laser Scan """

from time import sleep, strftime
import threading

## Parameters
c0=299792458.
res0 = 1559.3502 #guess of first Resonance
FSR0 = 226.9 # guess of FSR in GHz

range_width = 0.020 # width of individual scan
step_size = 0.0001 # step size nm : use at least 0.0003 for best accuracy
range = (res0-range_width/2, res0+range_width/2)

step_time = 0.7 #dwell time of the laser
sample_rate = 100e3
speed = 0.5 # scan speed of the laser nm/s


## Init GPIP
import visa
gpib = visa.instrument("GPIB::20") # Set Laser Address

## Init NIDAQmx
import daq

## Thread decorator (from http://stackoverflow.com/questions/884410/how-to-return-a-function-value-with-decorator-and-thread)
# Callable that stores the result of calling the given callable f.
class ResultCatcher:
    def __init__(self, f):
        self.f = f
        self.val = None

    def __call__(self, *args, **kwargs):
        self.val = self.f(*args, **kwargs)

def threaded(f):
    def decorator(*args,**kargs):
        # Encapsulate f so that the return value can be extracted.
        retVal = ResultCatcher(f)

        th = threading.Thread(target=retVal, args=args)
        th.start()
        th.join()

        # Extract and return the result of executing f.
        return retVal.val

    decorator.__name__ = f.__name__
    return decorator
#### ============================


@threaded
def scan_and_read( l,
                  step_time, step_size,):
       
    total_samples = ((range[1] - range[0]) /step_size )

    physical_channel = "dev2/ai0"      # Physical Channel: AI0 on Dev1

    voltage_task = daq.InputTask('Dev2')
    voltage_task.add_analog_voltage_channel(physical_channel, terminal_config = "rse")
    
    data = []
    samples_read = 0
    la=l-range_width/2
    
    while samples_read < total_samples:
        gpib.write("wav %fnm"%la)
        #print la # current wavelength
        print samples_read/total_samples #ratio of scan progress
        sleep(step_time)
        data.extend(voltage_task.read())
        la=la+step_size
        samples_read=samples_read+1
        
       
        
    ## Save data
    print len(data)
    voltage_task.clear()
    return data

import matplotlib

from matplotlib.pylab import *
from scipy.io import savemat 
from fitting import Parameter, fit



a = Parameter(-0.5 ,'a')
b = Parameter(0.1 ,'b')
l0 = Parameter(1550, 'lo')
gamma = Parameter(0.001,'gamma')
y0 = Parameter(0.7, 'y0')
#split=Parameter(0.5, 'split')

parameters = [a,l0,gamma,y0,b]
f = lambda x: a() /(1 + ((x-l0())/gamma())**2)+a()/(1 + ((x-l0())/gamma())**2) +y0()+b()*x

def scan_and_fit(l, step_size = step_size):
    range = r_[l-range_width/2, l+range_width/2]
    y = scan_and_read(l,
                      step_time, step_size)
                        
    x = linspace(range[0],range[1],len(y))
    ## Expected values for parameters
    l0.set(x[argmin(y)])
    y0.set(amax(y))
    a.set((amin(y)-amax(y)))
    gamma.set(0.002)
    #split.set(0.5)

    
    fit(f,parameters, x, y, 1)
    figure(1)
    hold(False)
    title("$\lambda_0 = %.4f$"%l0())
    xt = linspace(range[0],range[1],100) 
    plot(x,y,'o')
    hold(True)
    plot(xt, f(xt),'-')
    
    
    return l0(), gamma()

@threaded    
def measure_l(l):
    "Using wavemeter q8326"
    # Set laser to wavelenght
    sleep(0.5)
    gpib.write("wav %fnm"%l)
    sleep(2)
    # Measure the actual wavelength
    gpib_wm = visa.Instrument("GPIB::9")
    sleep(6)
    return gpib_wm.ask_for_values("E")[0]/1e-9  #in nm
    
#scan_and_fit(res0)

#res0=c0/(c0/res0 - FSR0)
#scan_and_fit(res0)

def scan_routine(auto = False):
    def plot_resonances():
        figure(0)
        hold(False)
        subplot(211)
        plot(resonances,'.')
        xlim(-1,len(resonances)+1)
        ylabel('RES')
        subplot(212)
        plot(-diff(c0/array(resonances)),'.')
        xlim(-1,len(resonances)+1)
        ylabel('FRS')
        hold(True)
        
    ion()
    
    laser_res = []
    resonances = []
    gammas = []
    FSRs=[]
    res_next = res0
    fsr0 = FSR0
    filename = "resonances_%s.txt"%strftime("%H%M")
    while res_next < 1640 and res_next > 1505:
        try:
            print "Scan for resonance [%.4f nm] --> "%res_next,
            if auto:
                res_0 = ''
            else:
                res_0 = raw_input()
            ## Parse input
            if res_0 == '0':
                break
            if res_0 == '':
                res_0 = res_next
            else:
                res_0 = float(res_0)
                
            print res_next    
            res,gamma = scan_and_fit(res_next, step_size)
            draw()
            res_0 = measure_l(res) ## Wavemeter measurement of the minima
            
            print "Is it okay (Y)? --> ",
            if not auto:
                if raw_input() != '':
                    print "Discarded!"
                    continue
            
            print "Added"
            resonances.append(res_0)
            gammas.append(gamma)
            laser_res.append(res)
          
            plot_resonances()
            draw()
            ## Update FSR
            if len(resonances) > 1: 
                fsr0 = c0/resonances[-2] - c0/resonances[-1]
            print fsr0
            FSRs.append(fsr0)
            res_next = c0/(c0/res - fsr0)
            print res_next
            np.savetxt(filename, c_[resonances, gammas, laser_res,FSRs],
                                        fmt="%.5f")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print e," raised"

          
#data = scan_and_read(range, step_time, step_size, samples_per_step = 10)
#data3 = scan_and_read(range, step_time, step_size, samples_per_step = 10)

#print "File name (matlab file) -> ",
#n = raw_input() 

#savemat(n + ".mat",{'data': data, 'range': range, 'speed': speed})
#np.savetxt("test.txt",data)
#plot(linspace(range[0],range[1],len(data)), data)

#plot(FSRs)

    
scan_routine(auto = False)

