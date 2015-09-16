# -*- coding: utf-8 -*- 

import threading, time, sys, cPickle, os
from time import sleep

## Set the path to the farsilab directory (if not installed) #######
sys.path.append(r'C:\\dropbox\\Gaeta-lab\\farsilab\\')
sys.path.append(r'E:\\ActionDropbox\\Dropbox\\Gaeta-lab\\farsilab\\')
sys.path.append(r'E:\\farsilab\\')

import matplotlib
from numpy import *

import wx
matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as Toolbar
from matplotlib.figure import Figure

from control.instruments.laserScanPanelForm import scanMonitor

from fitting import Parameter, fit

## Globals #########
res_list = [] # List of acquired resonances
c0=299792458. # Light speed

    
a = Parameter(-0.5 ,'a')
b = Parameter(0.1 ,'b')
l0 = Parameter(1550, 'lo')
gamma = Parameter(0.001,'gamma')
y0 = Parameter(0.7, 'y0')
split=Parameter(0.001, 'split')    
        
fit_functions = {   'lorentz': [[a,l0,gamma, y0,b], 
                              lambda x: a() /(1 + ((x-l0())/gamma())**2) + y0() +b()*x],
                    'split': [[a,l0,gamma, y0, b,split],
                              lambda x: a() /(1 + ((x-l0()-split())/gamma())**2)+a()/(1 + ((x-l0()+split())/gamma())**2) +y0()+b()*x],
                    'dumb': [[a],
                            lambda x: a()*x]}
                            
# Instrument handlers
error_log = ""
error_visa = False
gpib_wm = None


def agilent_wl(i, wl):
    i.write("wav %fnm"%wl)

def osics_wl(i, wl, ch=1):
    print "Asking ", "ch%d:l?"%ch,
    cw = i.ask_for_values("ch%d:l?"%ch)
    print cw
    i.write("ch%d:l=%f"%(ch,wl))
    ## If laser scans backward, waits 10 seconds
    if cw[1] > wl:
        print "Moving wavelenght slowly back"
        sleep(10)
    else:
        print "Set wl"
        sleep(1)
        
def script_scan(options, abort, plot_hook):
    auto_range = options['auto_range']
    res_next = auto_range[0]
    fsr0 = options['fsr0']
    
    while (res_next < auto_range[1]):
        print res_next
        
        r = scan_and_fit(res_next, options['step_size'], 
                                   options['rnge'],
                                   function_name = options['fit_function'],
                                   laser_name = options['laser_name'],
                                   )
        
        
        ## Update FSR
        if len(res_list) > 0: 
            fsr0 = c0/res_list[-1]['precise_l0'] - c0/r['precise_l0']
        print fsr0
        r['fsr0'] = fsr0
        
        
        res_next = c0/(c0/r['l0'] - fsr0)
        print res_next
        
        res_list.append(r)
        
        plot_hook(len(res_list)-1)
        if abort: break
        
def script_2wls(options, plot_hook):
    print "Scan Type 2: Jump between wl-start and wl-stop"
    w1, w2 = options['auto_range']
    
    while True:
        print w1
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
        
        print w2
        r = scan_and_fit(w2, options['step_size'], 
                             options['rnge'],
                                   function_name = options['fit_function'],
                                   laser_name = options['laser_name'],
                                   )
        
        fsr0 = c0/w2 - c0/r['precise_l0']
        r['fsr0'] = fsr0
        res_list.append(r)
        
        plot_hook(len(res_list)-1)
        if abort: break

osics1_wl = lambda i,wl: osics_wl(i,wl,1)
osics2_wl = lambda i,wl: osics_wl(i,wl,2)
        
                          # GPIB, handler, setwl
laser_gpib_list = { 'agilent155': [ 20, [agilent_wl,]],
                    'agilent140': [ 19, [agilent_wl,]],
                    'osics':   [ 11, [osics1_wl, osics2_wl]], }

laser_list = { 'dummy': lambda x: 0 }
               
autoscan_scripts = { 'scan through': script_scan,
                     'scan_2wls': script_2wls,}               
               
try:
    ## Init GPIP
    import visa
    ## Init NIDAQmx
    import control.daq  as daq 
except ImportError:
    error_log = error_log + "Import error: verify libraries\n"
    error_visa = True

for name, (addr,f_wl) in laser_gpib_list.items():
    try:    
        i = visa.instrument("GPIB::%d"%(addr)) # Set Laser Address
        i.timeout = 2
        print i
        print i.ask("*idn?")
        for j, f in enumerate(f_wl):
            laser_list[name+"%d"%j] = (i, f)
        
            
    except:
        
        error_log = error_log + "Laser %s on GPIB::%d not connected\n"%(name, addr)

try:        
    gpib_wm = visa.Instrument("GPIB::9")
except:
    error_log = error_log + "Wavemeter not connected\n"


## Instrument ################################################
def scan_and_read(wl, setLaserWl, step_time = 0.8):
    physical_channel = "dev2/ai0"      # Physical Channel: AI0 on Dev1

    voltage_task = daq.InputTask('Dev2')
    voltage_task.add_analog_voltage_channel(physical_channel, terminal_config = "rse")
    
    data = zeros(len(wl))
    samples_read = 0
    
    for i,l in enumerate(wl):
        print l, 
        setLaserWl(l)
        print 1. * samples_read/len(wl) #ratio of scan progress
        sleep(step_time)
        data[i] = voltage_task.read()
        samples_read=samples_read+1
        
    ## Save data
    voltage_task.clear()
    return data
    

def scan_and_read_dummy(wl):
    sleep(1)
    return random.random(len(wl))

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
    setLaserWl = lambda wl : laser_list[laser_name][1](inst,wl)
    print laser_name
    
    # we scan half
    
    y1 = scan_and_read(wl[:len(wl)/2], setLaserWl)
    p_l0 = measure_l(wl[len(wl)/2-1],  setLaserWl) ## Wavemeter measurement of the minima
    y2 = scan_and_read(wl[len(wl)/2:], setLaserWl)
    
    y = r_[y1,y2]
    
    ## Wavemeter wavelength delta
    delta_l0 = p_l0 - wl[len(wl)/2-1]
    
    ## Expected values for parameters
    l0.set(wl[argmin(y)])
    y0.set(amax(y))
    a.set((amin(y)-amax(y)))
    gamma.set(0.002)

    parameters, f = fit_functions[function_name]
    fit(f,parameters, wl, y, 1,)
    
    xt = linspace(wl[0],wl[-1], len(y)*10)
    
    
    print "Precision wl = ", l0() + delta_l0        
    
    r = {'l0': l0(), 'gamma':gamma(), 'precise_l0': l0() + delta_l0,
          'y0': y0(), 'a': a(),
         'data':c_[wl, y].T, 'fit': c_[xt, f(xt)].T}
    
    return r
	
class AutoScan(threading.Thread):
    def __init__(self, options, plotRes, parent):
        threading.Thread.__init__(self)
        
        ## Set panel
        self.plotRes = plotRes
        self.options = options
        
        self.panel = parent
        ## Set acquisition
        
    def run(self):
        ## Lock button
        self.abort = False
        autoscan_script[self.options['auto_script']](self.options, self.abort, self.plotRes())
            
        print "Done"
        wx.PostEvent(self.panel, ResultEvent(0))
            #np.savetxt(filename, c_[resonances, gammas, laser_res, FSRs],
            #                            fmt="%.5f")
        
    def stop(self):
        self.abort = True


## GUI #################################################################        
EVT_RESULT_ID = wx.NewId()
	
class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        


class PlotPanel(wx.Panel):
    """ Inspired by example "embedding_in_wx3.py"
    
    Bare matplotlib panel"""
    def __init__(self, *arg):
        wx.Panel.__init__(self, *arg)

        self.fig = Figure((3,2))
        self.canvas = FigureCanvasWxAgg(self, -1, self.fig)
        self.toolbar = Toolbar(self.canvas) #matplotlib toolbar
        self.toolbar.Realize()
        #self.toolbar.set_active([0,1])
        
        ## Now put all into a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        ## This way of adding to sizer allows resizing
        sizer.Add(self.canvas, 1,wx.ALL | wx.EXPAND)
        ## Best to allow the toolbar to resize!
        sizer.Add(self.toolbar, 0, wx.ALL)
        self.sizer = sizer
        self.SetSizer(sizer)
        self.Fit()

    def GetToolBar(self):
        # You will need to override GetToolBar if you are using an
        # unmanaged toolbar in your frame
        return self.toolbar

    def onEraseBackground(self, evt):
        # this is supposed to prevent redraw flicker on some X servers...
        pass    

        
class Monitor(scanMonitor):
    def __init__( self, parent ):
        scanMonitor.__init__(self, parent)
        
        ## Add plotpanels
        bSizerPlots = self.GetSizer().GetChildren()[0].GetSizer()
        self.m_panel1 = PlotPanel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizerPlots.Add( self.m_panel1, 1, wx.EXPAND |wx.ALL, 5 )
        self.m_panel2 = PlotPanel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizerPlots.Add( self.m_panel2, 1, wx.EXPAND |wx.ALL, 5 )
        
        self.axis = [self.m_panel1.fig.add_subplot(111),
                     self.m_panel2.fig.add_subplot(111)]
        
        self.canvases = [ self.m_panel1.canvas,  self.m_panel2 .canvas]
        
        for f in fit_functions.iterkeys():
            self.m_chc_fit.Append(f)
        for f in laser_list.iterkeys():
            self.m_chc_laser.Append(f)
        for f in autoscan_scripts.iterkeys():
            self.m_chc_autoscr.Append(f)
            
        self.m_chc_fit.SetSelection(0)
        
        self.m_txt_fit.SetValue(error_log)
        
        self.Layout()
        self.Centre( wx.BOTH )

        ## Private vars
        self.a = None
        self.p = None
        self.worker = None

        self.Connect(-1, -1, EVT_RESULT_ID, self.scanDone)
        
    def selectResonance( self, event ):
        # select the resonance
        self.plotRes(event.GetSelection())
        
    def plotRes(self,i): 
        self.m_lst_resonances.Clear()
        for k,r in enumerate(res_list):
            self.m_lst_resonances.Append('%3d x0 = %10.4f'%(k+1,r['l0']))
        
        self.m_lst_resonances.SetSelection(i)
        
        r = res_list[i]
        
        self.m_txt_l0.SetValue("%.4f"%r['l0'])
        self.m_txt_g.SetValue("%.2f"%(1000*r['gamma']))
        self.m_txt_y0.SetValue("%.2f"%r['y0'])
        self.m_txt_area.SetValue("%.2f"%r['a'])
        
        if 'fsr0' in r:
            self.m_txt_fsr0.SetValue("%.2f"%r['fsr0'])
        
        # Write the 
        x,y = r['data']
        xf,yf = r['fit']
        
        self.axis[0].hold(False)
        self.axis[0].plot(x,y,'o')
        self.axis[0].hold(True)
        self.axis[0].plot(xf,yf,'-')
    
        self.axis[0].set_ylim(amin(y)*0.8,amax(y)*1.2)
    
    
        # Highlight point on the bottom
        self.axis[1].hold(False)
        ress = array([r['l0'] for r in res_list if 'fsr0' in r])
        fsr0 = [r['fsr0'] for r in res_list if 'fsr0' in r]
        
        if len(fsr0) > 2:
            fsr0_laser = -c0*diff(1/ress)
            fsr0_laser = r_[fsr0_laser[0], fsr0_laser]
        
            self.axis[1].plot(fsr0_laser,'.', label = "Laser")
            
        self.axis[1].hold(True)
        self.axis[1].plot(fsr0, label = "Wavemeter" )
        
        if 'fsr0' in res_list[i]:
            self.axis[1].plot(i,res_list[i]['fsr0'],'ro')
        self.axis[1].set_xlim(-1,len(res_list))
        
        self.axis[1].legend()
        
        self.canvases[0].draw()
        self.canvases[1].draw()
    
    def scanOnce( self, event ):
        options = self.readLabels()
        r = scan_and_fit(wl0 = options['l0'],
                         step_size = options['step_size'],
                         range = options['rnge'],
                         function_name = options['fit_function'],
                         laser_name = options['laser_name'],
                         )
    
        res_list.append(r)
        
        
        self.plotRes(len(res_list)-1)
    
    def scanAuto( self, event ):
        if not self.worker:
            self.m_btn_start.Disable()
            self.m_btn_auto.SetLabel('Stop')
            self.worker = AutoScan(self.readLabels(),self.plotRes, self)
            self.worker.start()
        else:
            self.worker.stop()
            
            
    
    def scanDone(self, event):
        self.m_btn_start.Enable()
        self.m_btn_auto.SetLabel('Auto Scan')
        self.worker = None
    
    def updateValues( self, event ):
        ## Validate..
        
        ## 
		self.readLabels()
        
    def readLabels(self):
        range = float(self.m_txt_range.GetValue())/1000.
        l0 = float(self.m_txt_l0.GetValue())
        step_size = float(self.m_txt_res.GetValue())/1000.
        auto_start = float(self.m_txt_startl.GetValue())
        auto_stop = float(self.m_txt_stopl.GetValue())
        fsr0 = float(self.m_txt_fsr0.GetValue())
        ## update the npoint label
        self.m_txt_npoints.SetLabel("%d"%(range/step_size))
        options = {'l0': l0,
                   'gamma': float(self.m_txt_g.GetValue())/1000, 
                   'rnge': range,
                   'step_size': step_size,
                   'auto_range': [auto_start, auto_stop],
                   'fsr0': fsr0,
                   'fit_function': self.m_chc_fit.GetStringSelection(),
                   'laser_name': self.m_chc_laser.GetStringSelection(),
                   'auto_script': self.m_ch_autoscr.GetStringSelection(),
                   'y0':float(self.m_txt_y0.GetValue()),
                   'a': float(self.m_txt_area.GetValue())
                   
                   }
        fit_params = []
        return options
        
    def fitAgain( self, event ):
        i = self.m_lst_resonances.GetSelection()
        r = res_list[i]
        options = self.readLabels()
        ## Values from GUI
        l0.set(options['l0'])
        y0.set(options['y0'])
        a.set(options['a'])
        gamma.set(options['gamma'])
        
        print fit_functions[options['fit_function']]
        parameters, f = fit_functions[options['fit_function']]
        wl, y = r['data']
        fit(f,parameters, wl, y, 1,)
    
        xt = linspace(wl[0], wl[-1], len(y)*10)
    
        p_l0 = measure_l(l0()) ## Wavemeter measurement of the minima
            
        r['l0'] = l0()
        r['gamma'] = gamma()
        r['precise_l0']=p_l0
        r['fit'] = c_[xt, f(xt)].T
    
        self.m_txt_fit.SetValue("\n".join([repr(p) for p in parameters]))
    
        res_list[i] = r
    
        self.plotRes(i)

    def saveRes( self, event ):
        ress = [ (a['l0'], a['gamma'], a['precise_l0'], a['fsr0']) for a in res_list]
        ## TODO Order the resonances
        ress = array(ress)
        
        filename = "resonances_%s.txt"%time.strftime("%H%M")
        dlg = wx.FileDialog(
            self, message="Save file",
            defaultDir=os.getcwd(), 
            defaultFile= filename,
            wildcard="Simple data (*.txt)|*.txt",
            style=wx.SAVE
            )

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            filename = dlg.GetPath()
            try:
                savetxt(filename, ress,
                                        fmt="%.5f")
                self.plotRes(0)
            except Exception as e:
                print e," raised"
                
        # Destroy the dialog. Don't do this until you are done with it!
        # BAD things can happen otherwise!
        dlg.Destroy()
        
        
	

    def saveAll( self, event ):
        filename = "resonances_%s.pik"%time.strftime("%H%M")
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(), 
            defaultFile=filename,
            wildcard="Python pickled (*.pik)|*.pik",
            style=wx.SAVE
            )

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            filename = dlg.GetPath()
            try:
                cPickle.dump(res_list, open(filename,'w'))
                self.plotRes(0)
            except Exception as e:
                print e," raised"
                
        # Destroy the dialog. Don't do this until you are done with it!
        # BAD things can happen otherwise!
        dlg.Destroy()
        
        
    def loadAll( self, event ):
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(), 
            defaultFile="",
            wildcard="Python pickled (*.pik)|*.pik",
            style=wx.OPEN
            )

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            filename = dlg.GetPath()
            try:
                lst = cPickle.load(open(filename,'r') )
                global res_list
                res_list = lst
                self.plotRes(0)
            except Exception as e:
                print e," raised"
                
        # Destroy the dialog. Don't do this until you are done with it!
        # BAD things can happen otherwise!
        dlg.Destroy()
        
        
    def selectDel(self, event):
        if event.GetKeyCode() is wx.WXK_DELETE:
            i = self.m_lst_resonances.GetSelection()
            del res_list[i]
            if i>=len(res_list):
                i = len(res_list)
            self.plotRes(i)
        
        
class MonitorApp(wx.App): 
    """Monitor App
    
    when ready app.MainLoop()"""
    def __init__(self, title = "TDC Monitor",):
        wx.App.__init__(self, False)
        self.f = Monitor(None)
        self.f.Show(True)
        
        
if __name__ == "__main__":
    app = MonitorApp()
    app.MainLoop()