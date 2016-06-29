# -*- coding: utf-8 -*- 
""" Laser Scan Panel

Scan at different wavelength
"""

import threading, time, sys, pickle, os
from time import sleep

# import matplotlib
from numpy import *
from scipy.io import savemat
import lmfit

# Helper funtions
from resonance_finder import find_resonances
#from fitting import Parameter, fit

# GUI import
from PyQt4 import QtGui, QtCore  
import pyqtgraph as pg

## Globals #########
res_list = [] # List of acquired resonances
quick_list = [] # List generated from fast scan
temp_res = []

try:
    quick_list = loadtxt('res_temp.txt')
    print('Loaded temp list')
except:
    pass

c0=299792458. # Light speed

# fit_functions = {   'lorentz': [[a,l0,gamma, y0,b], 
#                               lambda x: a() /(1 + ((x-l0())/gamma())**2) + y0() +b()*x],
#                     'split': [[a,l0,gamma, y0, b,split],
#                               lambda x: a() /(1 + ((x-l0()-split())/gamma())**2)+a()/(1 + ((x-l0()+split())/gamma())**2) +y0()+b()*x],
#                     'dumb': [[a],
#                             lambda x: a()*x]}

fit_functions = { 'lorentz': lmfit.models.LorentzianModel() + lmfit.models.ConstantModel() }
                            
# Instrument handlers
error_log = ""
error_visa = False
gpib_wm = None


def agilent_wl(i, wl):
    i.write("wav %fnm"%wl)

def osics_wl(i, wl, ch=1):
    print("Asking ", "ch%d:l?"%ch, end=' ')
    cw = i.ask_for_values("ch%d:l?"%ch)
    print(cw)
    i.write("ch%d:l=%f"%(ch,wl))
    ## If laser scans backward, waits 10 seconds
    if cw[1] > wl:
        print("Moving wavelenght slowly back")
        sleep(10)
    else:
        print("Set wl")
        sleep(1)
        
def script_scan(options, abort):
    auto_range = options['auto_range']
    res_next = auto_range[0]
    fsr0 = options['fsr0']
    
    while (res_next >= auto_range[0]) and (res_next < auto_range[1]):
        print("Res", res_next)
        r = scan_and_fit(res_next, options['step_size'], 
                                   options['rnge'],
                                   function_name = options['fit_function'],
                                   laser_name = options['laser_name'],
                                   )

        ## Update FSR
        if len(res_list) > 0: 
            fsr0 = c0/res_list[-1]['precise_l0'] - c0/r['precise_l0']
        print(fsr0)
        r['fsr0'] = fsr0
        
        res_next = c0/(c0/r['l0'] - fsr0)
        print(res_next)
        
        res_list.append(r)
        
        yield
        
def script_2wls(options, plot_hook):
    print("Scan Type 2: Jump between wl-start and wl-stop")
    w1, w2 = options['auto_range']
    
    while True:
        print(w1)
        r = scan_and_fit(w1, options['step_size'], 
                             options['rnge'],
                                   function_name = options['fit_function'],
                                   laser_name = options['laser_name'],
                                   )
        
        ## MEasure variation from given wl
        fsr0 = c0/w1 - c0/r['precise_l0']
        r['fsr0'] = fsr0
        res_list.append(r)
        plot_hook(len(res_list)-1)
        
        print(w2)
        r = scan_and_fit(w2, options['step_size'], 
                             options['rnge'],
                                   function_name = options['fit_function'],
                                   laser_name = options['laser_name'],
                                   )
        
        fsr0 = c0/w2 - c0/r['precise_l0']
        r['fsr0'] = fsr0
        res_list.append(r)
        
        plot_hook()
        if abort: break

def script_list(options, abort):
    global error_log
    correction = 0-0.012
    resonance_list = quick_list
    start_res = 0# options['last_res'] - 1
    if (start_res < 0) or (start_res > len(resonance_list)) or len(resonance_list)==0:
        error_log = error_log + "Resonance scan # error\n"
        return
    i = 0
    while i < len(resonance_list):
        res_next = resonance_list[i]
        print(res_next)
        
        r = scan_and_fit(res_next-correction, options['step_size'], 
                                   options['rnge'],
                                   function_name = options['fit_function'],
                                   laser_name = options['laser_name'], )
        
        fsr0 = 0
        
        ## Update FSR
        if len(res_list) > 0: 
            fsr0 = c0/res_list[-1]['precise_l0'] - c0/r['precise_l0']
        r['fsr0'] = fsr0

        i += 1
        
        res_list.append(r)
        #plot_hook(len(res_list)-1)
        yield r['precise_l0']
        
        
        
osics1_wl = lambda i,wl: osics_wl(i,wl,1)
osics2_wl = lambda i,wl: osics_wl(i,wl,2)
        
                          # GPIB, handler, setwl
laser_gpib_list = { 'agilent1550': [ 4, [agilent_wl,]],
                    'agilent1400': [ 19, [agilent_wl,]],}
                    #'osics':   [ 11, [osics1_wl, osics2_wl]], }

laser_list = { 'dummy': [0, lambda i,wl: 0] }
               
autoscan_scripts = { 'fsr': script_scan,
                     #'scan_2wls': script_2wls,
                     'list': script_list}               
               
try:
    ## Init GPIP
    import visa
    rm = visa.ResourceManager()
    ## Init NIDAQmx
    import daq  as daq 
except ImportError:
    error_log = error_log + "Import error: verify libraries\n"
    error_visa = True

for name, (addr,f_wl) in list(laser_gpib_list.items()):
    try:    
        i = rm.open_resource("GPIB::%d"%(addr)) # Set Laser Address
        i.timeout = 2
        print(i)
        print(i.query("*idn?"))
    except:        
        error_log = error_log + "Laser %s on GPIB::%d not connected\n"%(name, addr)
    for j, f in enumerate(f_wl):
        laser_list[name+"%d"%j] = (i, f)
    

try:        
    gpib_wm = visa.Instrument("GPIB::9")
except:
    error_log = error_log + "Wavemeter not connected\n"


## Instrument ################################################
def scan_and_read(wl, setLaserWl, step_time = 0.9):
    physical_channel = "dev1/ai0"      # Physical Channel: AI0 on Dev1

    voltage_task = daq.InputTask('Dev1')
    voltage_task.add_analog_voltage_channel(physical_channel, terminal_config = "rse")
    voltage_task.configure_sample_clock_timing(sample_rate = 20e3, samples_per_channel = 20000)
    voltage_task.read_all_samp(False)

    monitor_task = daq.InputTask('Dev1')
    monitor_task.add_analog_voltage_channel("dev1/ai1", terminal_config = "rse")
    monitor_task.configure_sample_clock_timing(sample_rate = 20e3, samples_per_channel = 5000)
    monitor_task.read_all_samp(False)

    data = zeros(len(wl))
    monitor_data = zeros(len(wl))
    samples_read = 0
    
    for i,l in enumerate(wl):
        print("%.3f nm"%l, end=' ') 
        setLaserWl(l)
        
        sleep(step_time)
        data[i] = average(voltage_task.read())
        monitor_data[i] = average(monitor_task.read())
        samples_read=samples_read+1
        print("%.2f %%"%(100. * samples_read/len(wl)), data[i]) #ratio of scan progress
    ## Save data
    voltage_task.clear()
    monitor_task.clear()
    return data, monitor_data
    
def sweep_and_read(laser):
    ## Parameters
    wrange = (1510,1640)
    offsetWL = 0.00
    sample_rate = 4e4
    speed = 5 # nm/s (only options are .5 5 40)
    total_samples = ((wrange[1] - wrange[0]) /speed * sample_rate )


    physical_channel = "dev1/ai0"      # Physical Channel: AI0 on Dev1

    voltage_task = daq.InputTask('Dev1')
    voltage_task.add_analog_voltage_channel(physical_channel, terminal_config = "rse")
    
    voltage_task.configure_sample_clock_timing( sample_rate,
                                            source="".encode('UTF-8'),
                                            sample_mode=daq.DAQmx_Val_FiniteSamps,
                                            samples_per_channel = int(total_samples))

    voltage_task.set_digital_trigger("/Dev2/PFI0")

    
    # Prepare Laser
    ## Setup laser
    pre = "wav:sweep:"
    laser.write(pre + "MODE CONT")
    laser.write(pre + "START %f nm"%wrange[0])
    laser.write(pre + "STOP %f nm"%wrange[1])
    laser.write(pre + "SPEED %fnm/s"%speed)
    laser.write("TRIGGER:OUTPUT SWSTarted:")
    ## Set the laser at 0
    laser.write("wav %f nm"%wrange[0])

    sleep(10)                                        
        
    buffer = []
    samples_read = 0
    
    with voltage_task:
        ## Start acquisition
        voltage_task.start()
        laser.write("WAV:SWEEP:STATE 1")
        # To avoid warnings when the we rea
        #warnings.filterwarnings('ignore', 'Read')
        
        byte_read = 0
        
        while byte_read < total_samples:
            b = voltage_task.read()
            #
            byte_read += len(b)    
            if len(b) != 0:
                print((len(b), "%.2f"%(byte_read/total_samples)))
                buffer.extend(b)
            sleep(.5)
    
    wl = linspace(wrange[0],wrange[1], total_samples)
    return wl, array(buffer)
    
    
def scan_and_read_dummy(wl, setLaserWl):
    sleep(1)
    return (1-exp(-((wl-average(wl))/.005)**2))

if error_visa:
    scan_and_read = scan_and_read_dummy
    
def measure_l(wl, setLaserWl):
    ## Skip of there is not wavemeter
    if not gpib_wm:
        return wl
        
    "Using wavemeter q8326"
    # Set laser to wavelenght
    #sleep(0.5)
    #setLaserWl(wl)
    sleep(5)
    
    #sleep(6)
    return gpib_wm.ask_for_values("E")[0]/1e-9  #in nm

## Analysis ##############################################################                             
def scan_and_fit(wl0, step_size, range, laser_name, function_name = 'lorentz'):
    wl = arange(wl0 - range/2, wl0 + range/2, step_size)
    
    
    inst = laser_list[laser_name][0]
    setLaserWl = lambda wl : laser_list[laser_name][1](inst, wl)
    print(laser_name, wl)
    
    # we scan half
    
    y1, m1 = scan_and_read(wl[:len(wl)/2], setLaserWl)
    p_l0 = measure_l(wl[len(wl)/2-1],  setLaserWl) ## Wavemeter measurement of the minima
    y2, m2 = scan_and_read(wl[len(wl)/2:], setLaserWl)
    
    y = r_[y1,y2]
    y_m = r_[m1, m2]

    ## Wavemeter wavelength delta
    delta_l0 = p_l0 - wl[len(wl)/2-1]
    
    ## Expected values for parameters
    model = fit_functions[function_name]
    params = model.make_params()

    params['center'].value = wl[argmin(y)]
    params['c'].value = amax(y)
    params['amplitude'].value = amin(y)-amax(y)
    params['sigma'].value = 0.002


    fit_res = model.fit(y_m, x = wl, params = params)
    print(fit_res.fit_report())
    params = fit_res.params


    xt = linspace(wl[0],wl[-1], len(y)*10)
      
    
    r = {'l0': params['center'].value, 'gamma': params['sigma'].value, 'precise_l0': params['center'].value + delta_l0,
          'y0': params['c'].value, 'a': params['amplitude'].value,
         'data':c_[wl, y, y_m].T, 'fit': c_[xt, fit_res.eval(x = xt)].T,
         'monitor': y_m}
    
    return r

def prepareSaveFile(filename):
    ress = [ (a['l0'], a['gamma'], a['precise_l0'], a['fsr0']) for a in res_list]
    res_data = dstack([  a['data'] for a in res_list ])
    
    ## TODO Order the resonances
    ress = array(ress)
    savetxt(filename + '.txt', ress, fmt="%.5f")
    savemat(filename, {'data': res_data})
	
class AutoScan(QtCore.QThread):
    redraw = QtCore.pyqtSignal()

    def __init__(self, options, plotRes, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.exiting = False
        
        ## Set panel
        self.plotRes = plotRes
        self.options = options
        
        
        
        ## Set acquisition
        self.script = autoscan_scripts[ self.options['auto_script']]
        
        print(self.options['auto_script'])
        
        
    def run(self):
        ## Lock button
        print('hi')
        for r in self.script(self.options, self.exiting):
            self.redraw.emit() #plot
            #plotLast()
            
            prepareSaveFile('temp_autoscan')
            if self.exiting: break
        print("Done")
        
    def stop(self):
        self.abort = True


## GUI #################################################################        
        
# class Monitor(scanMonitor):
#     def __init__( self, parent ):
#         scanMonitor.__init__(self, parent)
        
#         ## Add plot_widgets
#         bSizerPlots = self.GetSizer().GetChildren()[0].GetSizer()
#         self.m_panel1 = pyqtgraph.PlotWidget( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
#         bSizerPlots.Add( self.m_panel1, 1, wx.EXPAND |wx.ALL, 5 )
#         self.m_panel2 = pyqtgraph.PlotWidget( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
#         bSizerPlots.Add( self.m_panel2, 1, wx.EXPAND |wx.ALL, 5 )
        
#         self.axis = [self.m_panel1.addItem(),
#                      self.m_panel2.addItem()]
        
#         self.canvases = [ self.m_panel1.getPlotItem(),  self.m_panel1.getPlotItem()]
        
#         for f in fit_functions.keys():
#             self.m_chc_fit.Append(f)
#         for f in laser_list.keys():
#             self.m_chc_laser.Append(f)
#         for f in autoscan_scripts.keys():
#             self.m_chc_autoscr.Append(f)
        

#         ## Default values ###    
#         self.m_chc_fit.SetSelection(0)
#         self.m_chc_laser.SetSelection(len(laser_list))
#         self.m_chc_autoscr.SetSelection(0)
        
        
#         self.m_txt_fit.SetValue(error_log)
        
#         self.Layout()
#         self.Centre( wx.BOTH )

#         ## Private vars
#         self.a = None
#         self.p = None
#         self.worker = None

#         ## Event!!!!!
#         self.Connect(-1, -1, EVT_RESULT_ID, self.scanDone)
        
#     def selectResonance( self, event ):
#         # select the resonance
#         self.plotRes(event.GetSelection())
def plotLast():
    print('Plotting')
    ## Plot last resonance
    r = res_list[-1]
    x,y,ym = r['data']
    xf,yf = r['fit']
    
    #plot.clear()
    plot.plot(x,y)
    plot.plot(xf,yf/ amax(ym)*amax(y), pen = {'color':'r'})

    plot.plot(x,ym/ amax(ym)*amax(y), pen = {'color':'b'})
    ## plot the FSRs

    x = [r['l0'] for r in res_list]
    y = [r['fsr0'] for r in res_list]
    plotFSR.clear()
    plotFSR.plot(x,y, symbolBrush=(255,0,0), symbolPen='w')

#     def plotRes(self,i): 
#         self.m_lst_resonances.Clear()
#         for k,r in enumerate(res_list):
#             self.m_lst_resonances.Append('%3d x0 = %10.4f'%(k+1,r['l0']))
        
#         self.m_lst_resonances.SetSelection(i)
        
#         r = res_list[i]
        
#         self.m_txt_l0.SetValue("%.4f"%r['l0'])
#         self.m_txt_g.SetValue("%.2f"%(1000*r['gamma']))
#         self.m_txt_y0.SetValue("%.2f"%r['y0'])
#         self.m_txt_area.SetValue("%.2f"%r['a'])
        
#         if 'fsr0' in r:
#             self.m_txt_fsr0.SetValue("%.2f"%r['fsr0'])
        
#         # Write the 
#         x,y = r['data']
#         xf,yf = r['fit']
        
#         self.axis[0].hold(False)
#         self.axis[0].plot(x,y,'o')
#         self.axis[0].hold(True)
#         self.axis[0].plot(xf,yf,'-')
    
#         self.axis[0].set_ylim(amin(y)*0.8,amax(y)*1.2)
    
    
#         # Highlight point on the bottom
#         self.axis[1].hold(False)
#         ress = array([r['l0'] for r in res_list if 'fsr0' in r])
#         fsr0 = [r['fsr0'] for r in res_list if 'fsr0' in r]
        
#         if len(fsr0) > 2:
#             fsr0_laser = -c0*diff(1/ress)
#             fsr0_laser = r_[fsr0_laser[0], fsr0_laser]
        
#             self.axis[1].plot(fsr0_laser,'.', label = "Laser")
            
#         self.axis[1].hold(True)
#         self.axis[1].plot(fsr0, label = "Wavemeter" )
        
#         if 'fsr0' in res_list[i]:
#             self.axis[1].plot(i,res_list[i]['fsr0'],'ro')
#         self.axis[1].set_xlim(-1,len(res_list))
        
#         self.axis[1].legend()
        
#         self.canvases[0].draw()
#         self.canvases[1].draw()
    
#     def fastScan(self, event):
#         options = self.readLabels()
#         wl, data = sweep_and_read(laser = laser_list[options['laser_name']][0])
#                                       #               options['last_res'])
                                      
#         res = find_resonances(wl,data, threshold = 5)
#         savetxt('res_temp.txt',res)
#         savemat('scant_temp', {'wl':wl, 'data':data})
#         self.axis[0].hold(False)
#         self.axis[0].plot(wl,data)
#         self.axis[0].hold(True)
#         self.axis[0].plot(res,0.5*ones_like(res),'o')
#         self.canvases[0].draw()
        
#         quick_list = res
        
        
            
#     def scanOnce( self, event ):
#         options = self.readLabels()
#         r = scan_and_fit(wl0 = options['l0'],
#                          step_size = options['step_size'],
#                          range = options['rnge'],
#                          function_name = options['fit_function'],
#                          laser_name = options['laser_name'],
#                          )
    
#         res_list.append(r)
        
        
#         self.plotRes(len(res_list)-1)
    
def scanAuto(options):
    #if not self.worker:
        #self.m_btn_start.Disable()
        #self.m_btn_auto.SetLabel('Stop')
        worker = AutoScan(options, plotLast)
        worker.start()
        #else:
        #    self.worker.stop()
        #script = autoscan_scripts[ options['auto_script']]
        #for r in script(options, None, plotLast):
        #    prepareSaveFile('temp_autoscan.txt')
            
            
            
    
#     def scanDone(self, event):
#         self.m_btn_start.Enable()
#         self.m_btn_auto.SetLabel('Auto Scan')
#         self.worker = None
    
#     def updateValues( self, event ):
#         ## Validate..
        
#         ## 
#         self.readLabels()
        
#     def readLabels(self):
#         range = float(self.m_txt_range.GetValue())/1000.
#         l0 = float(self.m_txt_l0.GetValue())
#         step_size = float(self.m_txt_res.GetValue())/1000.
#         auto_start = float(self.m_txt_startl.GetValue())
#         auto_stop = float(self.m_txt_stopl.GetValue())
#         fsr0 = float(self.m_txt_fsr0.GetValue())
#         ## update the npoint label
#         self.m_txt_npoints.SetLabel("%d"%(range/step_size))
#         options = {'l0': l0,
#                    'gamma': float(self.m_txt_g.GetValue())/1000, 
#                    'rnge': range,
#                    'step_size': step_size,
#                    'auto_range': [auto_start, auto_stop],
#                    'fsr0': fsr0,
#                    'fit_function': self.m_chc_fit.GetStringSelection(),
#                    'laser_name': self.m_chc_laser.GetStringSelection(),
#                    'auto_script': self.m_chc_autoscr.GetStringSelection(),
#                    'y0':float(self.m_txt_y0.GetValue()),
#                    'a': float(self.m_txt_area.GetValue()),
#                    'last_res': int(self.m_txt_lastRes.GetValue()),
#                    }
#         fit_params = []
#         return options
        
#     def fitAgain( self, event ):
#         i = self.m_lst_resonances.GetSelection()
#         r = res_list[i]
#         options = self.readLabels()
#         ## Values from GUI
#         l0.set(options['l0'])
#         y0.set(options['y0'])
#         a.set(options['a'])
#         gamma.set(options['gamma'])
        
#         print(fit_functions[options['fit_function']])
#         parameters, f = fit_functions[options['fit_function']]
#         wl, y = r['data']
#         fit(f,parameters, wl, y, 1,)
    
#         xt = linspace(wl[0], wl[-1], len(y)*10)
    
#         p_l0 = measure_l(l0()) ## Wavemeter measurement of the minima
            
#         r['l0'] = l0()
#         r['gamma'] = gamma()
#         r['precise_l0']=p_l0
#         r['fit'] = c_[xt, f(xt)].T
    
#         self.m_txt_fit.SetValue("\n".join([repr(p) for p in parameters]))
    
#         res_list[i] = r
    
#         self.plotRes(i)
        
    
    
    
#     def saveRes( self, event ):
        
        
#         filename = "resonances_%s.txt"%time.strftime("%H%M")
#         dlg = wx.FileDialog(
#             self, message="Save file",
#             defaultDir=os.getcwd(), 
#             defaultFile= filename,
#             wildcard="Simple data (*.txt)|*.txt",
#             style=wx.SAVE
#             )

#         # Show the dialog and retrieve the user response. If it is the OK response, 
#         # process the data.
#         if dlg.ShowModal() == wx.ID_OK:
#             # This returns a Python list of files that were selected.
#             filename = dlg.GetPath()
#             try:
#                 prepareSaveFile(filename)
#                 self.plotRes(0)
#             except Exception as e:
#                 print(e," raised")
                
#         # Destroy the dialog. Don't do this until you are done with it!
#         # BAD things can happen otherwise!
#         dlg.Destroy()
        
        
	

#     def saveAll( self, event ):
#         filename = "resonances_%s.pik"%time.strftime("%H%M")
#         dlg = wx.FileDialog(
#             self, message="Choose a file",
#             defaultDir=os.getcwd(), 
#             defaultFile=filename,
#             wildcard="Python pickled (*.pik)|*.pik",
#             style=wx.SAVE
#             )

#         # Show the dialog and retrieve the user response. If it is the OK response, 
#         # process the data.
#         if dlg.ShowModal() == wx.ID_OK:
#             # This returns a Python list of files that were selected.
#             filename = dlg.GetPath()
#             try:
#                 pickle.dump(res_list, open(filename,'w'))
#                 self.plotRes(0)
#             except Exception as e:
#                 print(e," raised")
                
#         # Destroy the dialog. Don't do this until you are done with it!
#         # BAD things can happen otherwise!
#         dlg.Destroy()
        
        
#     def loadAll( self, event ):
#         dlg = wx.FileDialog(
#             self, message="Choose a file",
#             defaultDir=os.getcwd(), 
#             defaultFile="",
#             wildcard="Python pickled (*.pik)|*.pik",
#             style=wx.OPEN
#             )

#         # Show the dialog and retrieve the user response. If it is the OK response, 
#         # process the data.
#         if dlg.ShowModal() == wx.ID_OK:
#             # This returns a Python list of files that were selected.
#             filename = dlg.GetPath()
#             try:
#                 lst = pickle.load(open(filename,'r') )
#                 global res_list
#                 res_list = lst
#                 self.plotRes(0)
#             except Exception as e:
#                 print(e," raised")
                
#         # Destroy the dialog. Don't do this until you are done with it!
#         # BAD things can happen otherwise!
#         dlg.Destroy()
        
        
#     def selectDel(self, event):
#         if event.GetKeyCode() is wx.WXK_DELETE:
#             i = self.m_lst_resonances.GetSelection()
#             del res_list[i]
#             if i>=len(res_list):
#                 i = len(res_list)
#             self.plotRes(i)

        
if __name__ == "__main__":
    print(error_log)
    print(laser_list)
    ## Always start by initializing Qt (only once per application)
    app = QtGui.QApplication([])

    ## Define a top-level widget to hold everything
    w = QtGui.QWidget()

    ## Create the GUI
    plot = pg.PlotWidget()
    plot.enableAutoRange()
    plotFSR = pg.PlotWidget()
    plotFSR.enableAutoRange()
    btn = QtGui.QPushButton('Start scan')



    layout = QtGui.QGridLayout()
    w.setLayout(layout)
    layout.addWidget(btn, 0, 0)   # button goes in upper-left
    layout.addWidget(plot, 1, 0,)  # plot goes on right side, spanning 3 rows

    layout.addWidget(plotFSR, 2, 0)
    

    #plot.plot([1,3,5,64,2,21,43,23,67,3,44,])

    options = { 'rnge': .013,  # nm
                'fit_function': 'lorentz',
                'laser_name': 'agilent14000',
                'auto_script': 'fsr',  #fsr, list
                'step_size': .0001, # nm
                'auto_range': [1395.670, 1435], # nm
                'last_res': 1429.449,
                'fsr0': 489.480,
                'l0': 1430,
                'gamma': 2/1000, 
                'y0':3,
                'a': 1,
            }
    ## Use pyqtgraph option
    # options_params = [
    #     {'name': 'rnge', 'value': 0.013,         'type': 'float','suffix': 'nm'},

    #     {'name': 'fit_function',  'value': 'lorentz',        'type': 'list', 'values': fit_functions.keys(),},

    #     {'name': 'step_size', 'type': 'float', 'value': .0001, 'suffix': 'nm'},
    #     {'name': 'laser_name', 'type': 'list', 'values': laser_list.keys()}, 'value': 'agilent14000' },
    #     {'name': 'auto_script', 'type': 'list', 'values': autoscan_scripts.keys()}, 'value': 'fsr' },
    #     {'name': 'fsr0', 'type': 'float', 'value': 489.480, 'suffix': 'GHz'},
    # ]

    # from pyqtgraph.parametertree import Parameter, ParameterTree
    # p = Parameter.create(name='params', type='group', children=options_params)

    quick_list = loadtxt("730x1050-TE-ring17.txt").T[0]
    worker = AutoScan(options, plotLast)
    worker.redraw.connect(plotLast)
    
    btn.clicked.connect(worker.start)
    
    ## Display the widget as a new window
    w.show()

    ## Start the Qt event loop
    app.exec_()