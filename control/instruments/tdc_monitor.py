# -*- coding: utf-8 -*-
"""
:author: Action Farsi
:date: 13 July 2012


"""
import threading, time, sys
from time import sleep

## Set the path to the farsilab directory (if not installed) #######
sys.path.append(r'C:\\dropbox\\Gaeta-lab\\farsilab\\')
sys.path.append(r'E:\\ActionDropbox\\Dropbox\\Gaeta-lab\\farsilab\\')

import matplotlib
import matplotlib.animation as animation
from numpy import *

matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as Toolbar
from matplotlib.figure import Figure

import wx
import wx.xrc as xrc

from monitorframe import MonitorFrame 

# Acquisition routines
class AcquisitionWorker(threading.Thread):
    def __init__(self, dual_channel = False):
        """ Thread constructor
        
        :arg temp_file: Name of the temporary file
        :arg do_histogram:
        :arg bins:
        :arg rnge:
        :arg do_coincidences: Generate an additional 
                              histogram with the coincidences t2-t1
        """
        threading.Thread.__init__(self)
        
        self.dual_channel = dual_channel
        self.data = [     array([]),     array([]),     array([]) ]
        self.n_starts = 0
        
        self.lock = threading.Lock()
        #setHistogramParams( bins, rnge, do_histograms, do_coincidences, time_average)
        
    def run(self):
        self.kill = False
        max_size = 1e9
        #self.demon = True
        #self.demon = True
        i = 0
        # Timetag (loose), ch1, ch2
        new_data = [     array([]),     array([]),     array([]) ]
    
        while not self.kill:
            i += 1
            time.sleep(0.1)
            tic = time.time()
            
            ## Acquire
            # d = readBuffer(True)
            d = random.rand(2,10)*100
            
            
            new_data[0] =     concatenate((new_data[0][:], ones(len(d[0]))*tic ))  # Time tag
            new_data[1] =     concatenate((new_data[1][:], d[0]))
            if self.dual_channel:
                new_data[2] =     concatenate((new_data[2][:], d[1][:]))
    
            ## Process the raw_data
            if i %5 == 0:
                toc = time.time()-tic
                self.n_starts += len(new_data[0])
                #print "\nStarts / sec = %6.1f   "%(1.*len(new_data[0])/toc),
                new_data =     array(new_data)
                # Remove timeouts
                t1 =     nonzero(new_data[1][:] < 3000)[0]
                t2 =     nonzero(new_data[2][:] < 3000)[0]
                
                #try:
                #    new_data = new_data[:,     union1d(t1,t2)]
                #except IndexError:
                #    pass
                
                self.lock.acquire()
                self.data[0]=     concatenate((self.data[0],new_data[0][:]))
                self.data[1]=     concatenate((self.data[1],new_data[1][:]))
                self.data[2]=     concatenate((self.data[2],new_data[2][:]))
                
                if len(self.data[0]) > max_size: ## Free memory CAUTION save histogram!!!!!
                    self.data[0] = self.data[0,max_size/3:]
                    self.data[1] = self.data[1,max_size/3:]
                    self.data[2] = self.data[2,max_size/3:]
                new_data = [     array([]),     array([]),     array([]) ]
                
                self.lock.release()
                tic = time.time()
    
class ProcessingWorker(threading.Thread):
    def __init__(self, acquisition_w, panels, dual_channel = False,
                 bins = 10, rnge = (0,100), temp_file = 'temp.txt',
                 do_histograms = True, do_coincidences = False, time_average = 0):

                 
        threading.Thread.__init__(self)
        self.acquisition_w = acquisition_w
        self.dual_channel = dual_channel
        
        self.bins = bins
        self.rnge = rnge
        self.time_average = time_average
        
        self.data = [[],[],[]]
        self.hist = [histogram([], self.bins,  self.rnge),
                     histogram([], self.bins, self.rnge)]
        self.n_starts = 0
        if temp_file != None:
            self.temp_file = open(temp_file,'w')
        else: 
            self.temp_file = None
            
        self.do_coincidences = do_coincidences
        self.do_histograms = do_histograms
        if do_coincidences:
            self.rnge_c = (self.rnge[0] - self.rnge[1], self.rnge[1] - self.rnge[0])
            self.hist_c = histogram([], 2*self.bins, self.rnge_c)
    
        ## Init the panels
        self.axis = [panels[0].fig.add_subplot(111),
                     panels[1].fig.add_subplot(111)]
        
        self.canvases = [ panels[0].canvas,  panels[1].canvas]
        
        self.axis[0].hold(False)
        self.axis[1].hold(False)
    
    
    
    def getData(self):
        self.acquisition_w.lock.acquire()
        self.data[0] = self.acquisition_w.data[0][:]
        self.data[1] = self.acquisition_w.data[1][:]
        if self.dual_channel:
            self.data[2] = self.acquisition_w.data[2][:]
        self.acquisition_w.lock.release()
    
    
    
    def run(self):
        self.kill = False
        #self.demon = True
        def midpoint(x):
            return (x[1:]+x[:-1])/2.
            
        ## get new data from the acquisition thread
        while not self.kill:
            self.getData()
            if self.time_average > 0 and len(self.data[0]) > 0:
                now = self.data[0][-1]  # Take the last measurement as now
                selection = (now-self.data[0]) < self.time_average
                self.data[0] = self.data[0][selection]
                self.data[1] = self.data[1][selection]
                if self.dual_channel:
                    self.data[2] = self.data[2][selection]
            
            ## Generate histogram
            h1 = histogram(self.data[1], self.bins, self.rnge)
            if self.dual_channel:
                h2 = histogram(self.data[2], self.bins, self.rnge)
            if self.dual_channel and self.do_coincidences:
                hc = histogram(self.data[2] - self.data[1], self.bins, 
                              (self.rnge[0]-self.rnge[1],self.rnge[1]-self.rnge[0]))
            ## Update plots
            
            self.axis[0].plot(midpoint(h1[1]),h1[0], label="Ch1")
            if self.dual_channel and not self.do_coincidences:
                self.axis[1].plot(midpoint(h2[1]),h2[0], label="Ch2")
            if self.dual_channel and self.do_coincidences:
                self.axis[0].hold()
                self.axis[0].plot(midpoint(h2[1]),h2[0], label="Ch2")
                self.axis[0].hold()
                self.axis[1].plot(midpoint(hc[1]),hc[0], label="Coinc")
            
            self.axis[0].set_ylim(ymin = 0)
            self.axis[1].set_ylim(ymin = 0)
            
            self.axis[0].legend()
            self.axis[0].grid()
            self.axis[1].legend()
            self.axis[1].grid()
            
            self.canvases[0].draw()
            self.canvases[1].draw()
            ## Save data


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
    
class Monitor(MonitorFrame):  # Adding some functionality to the bare bone form
    def __init__( self, parent ):
        MonitorFrame.__init__(self, parent)
        
        ## Add plotpanels
        bSizerPlots = self.GetSizer().GetChildren()[0].GetSizer()
        self.m_panel1 = PlotPanel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizerPlots.Add( self.m_panel1, 1, wx.EXPAND |wx.ALL, 5 )
        self.m_panel2 = PlotPanel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizerPlots.Add( self.m_panel2, 1, wx.EXPAND |wx.ALL, 5 )
        
        self.Layout()
        self.Centre( wx.BOTH )
        
        ## Private vars
        self.a = None
        self.p = None
    
    
    def startstop( self, event ):
        dual_channel = self.m_rdb_nchannels.GetSelection() == 1
        if not self.a:
            self.a = AcquisitionWorker(dual_channel = dual_channel)
            self.a.start()
            self.startWorker()
        else:
            self.p.kill = True
            self.a.kill = True
            del self.p
            del self.a
            self.a = None
    
    def startWorker(self):     
        options = {'dual_channel': self.m_rdb_nchannels.GetSelection() == 1,
                 'bins': int(self.m_txt_bins.GetValue()),
                 'rnge': (float(self.m_txt_start_t.GetValue()), float(self.m_txt_stop_t.GetValue())),
                 'do_histograms': False,
                 'temp_file': 'temp.txt',
                 'do_coincidences': self.m_chk_hist.GetValue(),
                 'time_average': float(self.m_txt_avg_t.GetValue())}
        print options
        self.p = ProcessingWorker(self.a, (self.m_panel1, self.m_panel2), **options)
        self.p.start()
    
    def changeOptions( self, event ):
        ## TODO Validate every value
        if self.p:
            self.p.kill = True
            self.startWorker()
    
    def changeChannel( self, event ):    
        if self.a:
            self.p.kill = True
            self.a.kill = True
            del self.a
            self.a = None
            self.startstop(None)
  
    def __del__(self):
        if self.a:
            self.p.kill = True
            self.a.kill = True
    
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
    #test()
    #simpleThreadedAcquisition()
    #monitorTDC(bins = 500, rnge = (0,200), average_rate = 1 )
    #monitorTDC2(bins = 200, rnge = (100,200) )
