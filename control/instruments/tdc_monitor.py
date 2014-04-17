# -*- coding: utf-8 -*-
"""
:author: Action Farsi
:date: 13 July 2012


"""

from matplotlib import pylab as pl
import matplotlib.animation as animation
from numpy import savetxt, random,histogram
#s = serial.Serial("com4", timeout = 0)

from ctypes import *

import time

# Acquisition routines
import threading, time, sys
# sys.path.append('E:\Utilities')
# import instserver
# try:
#     server = instserver.server()
# except:
# server = None
    
# def generateHist(data, bins = 20, rnge = None,
                       # histogram = None):
    # """ Generate an histogram of data
    
    # :arg data: Array-like
    # :arg bins: Number of bins
    # :arg rnge: 2-tuple with min and max values,
               # if None it is calculated from the data
    # :arg histogram: Array-like updated histogram rather then create new one
                    # If histogram is not None, also a range must be given
    # """
    
    # if histogram == None:
        # histogram = [0]*bins
    # else:
        # if rnge == None:
            # raise Exception("Histogram given but not range")
        # bins = len(histogram)
    # if rnge == None:
        # rnge = [min(data),max(data)]
    # delta_bin = 1.*(rnge[1] - rnge[0])/bins
    
    # for d in data:
        # if (d>=rnge[0]) and (d<rnge[1]):
            # histogram[ int((d-rnge[0])/delta_bin) ] += 1
    # return ( (pl.arange(bins)+ 0.5)*delta_bin + rnge[0]), histogram
    

 # Acquisition routines
# ==========================

# import threading, time, sys

# # sys.path.append('E:\Utilities')
# # import instserver
# # try:
    # # server = instserver.server()
# # except:
# server = None
    
# Threads for the acquisition and elaboration. 
# class AcquisitionWorker(threading.Thread):
    # """ Thread for acquire data from 1 channel
    
    # To use it
    
    # 1. Initialize the TDC
    # 2. Create the thread
    # 3. Start the thread
    # 4. The thread will store the acquisition in the variable self.data
    # 5. Once acquisition is done, stop the threads, and save the data on file.
    
    # It can also save a temporary file on disk (in case of accident).
    # Optionally it updates an histogram for real-time visualization.
    
    # It **does not** initialize, only read the buffer.
    # """
    
    # def __init__(self, bins = 10, rnge = (0,100), temp_file = 'temp.txt',
                       # do_histograms = True):
        # """ Thread constructor
        
        # :arg temp_file: Name of the temporary file
        # :arg do_histogram:
        # :arg bins:
        # :arg rnge:
        
        # """
        # threading.Thread.__init__(self)
        # self.bins = bins
        # self.rnge = rnge
        # self.data = []
        # self.hist = generateHist([], self.bins, rnge= self.rnge)
        # if temp_file != None:
            # self.temp_file = open(temp_file,'w')
        # else:
            # self.temp_file = None
        # self.do_histograms = do_histograms
        
            
        
    # def run(self):
        # """ Thread loop
        
        # In an infinite loop, it reads the TDC buffer,
        # converts it in time, and optionally create the histogram
        
        # To stop the loop, set self.kill = True
        # """
        
        # self.kill = False
        # self.demon = True
        
        # tic = time.time()
        
        # new_data = []
        # i = 0
        
        # while not self.kill:
            # i += 1
            # time.sleep(0.04)
            # d = readBuffer()
            # print "%6d"%len(d),
            # # d = random.rand(10)*100
            # new_data.extend(d)
            
            # if i %5 == 0:
                # print ""
                
                # new_data = pl.array(new_data)
                # Remove timeouts
                # # t = pl.nonzero(new_data < 3000)
                
                # try:                   
                    # new_data = new_data[new_data < 3000]
                # except IndexError:
                    # pass
                # self.data.extend(new_data)
                # toc = time.time()-tic
                
                # print "Counts / sec = %8.2f"%(1.*len(new_data)/toc)
                # print '                                 Starts ',
                # Generate channels histogram
                # if self.do_histograms:
                    # self.hist = generateHist(new_data, self.bins, rnge= self.rnge,histogram = self.hist[1])                  
                    # # print "Ch1 ",self.hist[1]
                    
                # Save a tempfile and flush (just to be sure)
                # if self.temp_file != None:
                    # for d in new_data:
                        # self.temp_file.write( "%12.3f \n"%(d) ) 
                # tic = time.time()
                # new_data = []
                
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
        self.data = [pl.array([]), pl.array([])]
        self.n_starts = 0
        
        self.lock = threading.Lock()
        #setHistogramParams( bins, rnge, do_histograms, do_coincidences, time_average)
        
    def run(self):
        self.kill = False
        #self.demon = True
        #self.demon = True
        i = 0
        new_data = [ pl.array([]), pl.array([]) ]
    
        while not self.kill:
            i += 1
            time.sleep(0.1)
            tic = time.time()
            # d = readBuffer(True)
            
            ## Acquire
            d = random.rand(2,10)*100
            new_data[0] = pl.concatenate((new_data[0][:], d[0]))
            print new_data
            if self.dual_channel:
                new_data[0].extend(d[0])
                new_data[1].extend(d[1])
    
            ## Process the raw_data
            if i %5 == 0:
                toc = time.time()-tic
                self.n_starts += len(new_data[0])
                #print "\nStarts / sec = %6.1f   "%(1.*len(new_data[0])/toc),
                new_data = pl.array(new_data)
                # Remove timeouts
                t1 = pl.nonzero(new_data[0][:] < 3000)[0]
                t2 = pl.nonzero(new_data[1][:] < 3000)[0]
                
                #try:
                #    new_data = new_data[:, pl.union1d(t1,t2)]
                #except IndexError:
                #    pass
                
                self.lock.acquire()
                self.data[0]= pl.concatenate((self.data[0],new_data[0][:]))
                self.data[1]= pl.concatenate((self.data[1],new_data[1][:]))
                new_data = [ pl.array([]), pl.array([]) ]
                
                self.lock.release()
                tic = time.time()
    
class ProcessingWorker(threading.Thread):
    def __init__(self, acquisition_w, panels, dual_channel = False,
                 bins = 10, rnge = (0,100), temp_file = 'temp.txt',
                 do_histograms = True, do_coincidences = False, time_average = 0):

                 
        threading.Thread.__init__(self)
        self.acquisition_w = acquisition_w
        self.dual_channel = False
        
        self.bins = bins
        self.rnge = rnge
        self.time_average = time_average
        
        self.data = [pl.array([]), pl.array([])]
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
        if self.dual_channel:
            self.data[1] = self.acquisition_w.data[1][:]
        self.acquisition_w.lock.release()
    
    def run(self):
        self.kill = False
        #self.demon = True
        
        ## get new data from the acquisition thread
        while not self.kill:
            self.getData()
            ## Generate histogram
            f = histogram(self.data[0], self.bins, self.rnge)[0]
            ## Update plots
            self.axis[0].plot(f)
            self.canvases[0].draw()
            ## Save data
    
# class AcquisitionWorker(threading.Thread):
    # """ Thread for acquire data from 2 channels
    
    # To use it
    
    # 1. Initialize the TDC
    # 2. Create the thread
    # 3. Start the thread
    # 4. The thread will store the acquisition in the variable self.data
    # 5. Once acquisition is done, stop the threads, and save the data on file.
    
    # It can also save a temporary file on disk (in case of accident).
    # Optionally it updates an histogram for real-time visualization.
    
    # It **does not** initialize, only read the buffer.
    # """
    
    # def __init__(self, bins = 10, rnge = (0,100), temp_file = 'temp.txt',
                       # do_histograms = True, do_coincidences = False, time_average = 0):
        # """ Thread constructor
        
        # :arg temp_file: Name of the temporary file
        # :arg do_histogram:
        # :arg bins:
        # :arg rnge:
        # :arg do_coincidences: Generate an additional 
                              # histogram with the coincidences t2-t1
        # """
        # threading.Thread.__init__(self)
        # setHistogramParams( bins, rnge, do_histograms, do_coincidences, time_average)
            
    # def setHistogramParams( bins = 10, rnge = (0,100), do_histograms = True, do_coincidences = False)
        # self.bins = bins
        # self.rnge = rnge
        # self.data = [pl.array([]),pl.array([])]
        # self.hist = [generateHist([], self.bins, rnge= self.rnge),
                     # generateHist([], self.bins, rnge= self.rnge)]
        # self.n_starts = 0
        # if temp_file != None:
            # self.temp_file = open(temp_file,'w')
        # else: 
            # self.temp_file = None
        # self.do_coincidences = do_coincidences
        # self.do_histograms = do_histograms
        # if do_coincidences:
            # self.rnge_c = (self.rnge[0] - self.rnge[1], self.rnge[1] - self.rnge[0])
            # self.hist_c = generateHist([], 2*self.bins, rnge= self.rnge_c)
    
    # def run(self):
        # """ Thread loop
        
        # In an infinite loop, it reads the TDC buffer,
        # converts it in time, and optionally create the histogram
        
        # To stop the loop, set self.kill = True
        # """
        # self.kill = False
        # self.demon = True
        
        # tic = time.time()
        
        # new_data = [ [],[] ]
        # i = 0
        
        # while not self.kill:
            # i += 1
            # time.sleep(0.1)
            # d = readBuffer(True)
            # # d = random.rand(2,10)*100
            # new_data[0].extend(d[0])
            # new_data[1].extend(d[1])
            
            # if i %5 == 0:
                # toc = time.time()-tic
                # self.n_starts += len(new_data[0])
                # print "\nStarts / sec = %6.1f   "%(1.*len(new_data[0])/toc),
                # new_data = pl.array(new_data)
                # Remove timeouts
                # t1 = pl.nonzero(new_data[0,:] < 3000)[0]
                # t2 = pl.nonzero(new_data[1,:] < 3000)[0]
                
                
                # try:
                    # new_data = new_data[:, pl.union1d(t1,t2)]
                # except IndexError:
                    # pass
                    
                # self.data[0]= pl.concatenate((self.data[0],new_data[0,:]))
                # self.data[1]= pl.concatenate((self.data[1],new_data[1,:]))
                
                
                # Generate channels histogram
                # if self.do_histograms:
                    # self.hist[0] = generateHist(new_data[0], self.bins, rnge= self.rnge,histogram = self.hist[0][1])
                    # self.hist[1] = generateHist(new_data[1], self.bins, rnge= self.rnge,histogram = self.hist[1][1])
                    # # print "Ch1 ",self.hist[0][1]
                    # # print "Ch2 ",self.hist[1][1]
                    
                # Generate coincidences histogram
                # if self.do_coincidences:
                    # try:
                        # coinc = new_data#[:,pl.intersect1d(t1,t2)]
                        # coinc = coinc[1]-coinc[0]
                        # self.hist_c = generateHist(coinc, 2*self.bins, rnge = self.rnge_c, histogram = self.hist_c[1])
                        # # print "Coincidences ", self.hist_c[1]
                        # print "Coinc %5.1f (%d)"%(1.*len(coinc)/toc, sum(self.hist_c[1])),
                    # except IndexError:
                        # print "Coinc %5.1f"%(0),
                        
                        
                    
                # Save a tempfile and flush (just to be sure)
                # if self.temp_file != None:
                    # for i in xrange(len(new_data[0])):
                        # self.temp_file.write( "%12.3f %12.3f\n"%(new_data[0][i],new_data[1][i]) ) 
                # tic = time.time()
                # new_data = [[], []]
                

 # Monitor
# ====================
# Uses matplotlib v1.1

# from matplotlib.widgets import Button

# def monitorTDC(bins = 100, rnge = (0,100) ):
    # """ Realtime acquisition and monitor
    
    # :arg bins:
    # :arg rnge:
    
    # When done, close first the Gui.
    # Then the prompt will ask how to save the data.
    
    # It creates an AcquisitionWorker thread, and an animated
    # matplotlib window that updates with data coming from the
    # acquisiton
    # """
    # TODO check version of Matplotlib
    
    # Initialize the measurement
    # initTdc()
    
    # Start thread for 1 channel acquisition
    # aWorker = AcquisitionWorker(bins = bins, rnge = rnge)
    # aWorker.start()

    # Init the figure for displaying the histogram
    
    # def update_line(num, line):
        # line.set_data(aWorker.hist)
        # if max(aWorker.hist[1]) > update_line.scale *0.85:
            # update_line.scale *= 2
            # pl.ylim(0, update_line.scale)
            # fig.canvas.draw()
        
        # return line,
        
    # fig = pl.figure()
    # ax = pl.gca()
    # l, = pl.plot(aWorker.hist[0], aWorker.hist[1], 'r-')
    # pl.xlabel('Time (ns)')
    # pl.title('TDC Channel 1')
    # update_line.scale = 25
    # pl.ylim(0, update_line.scale)
    
    # Start the animation, that is a loop were 
    # line_ani = animation.FuncAnimation(fig, update_line, 1,repeat = True,
                                        # fargs=(l,),
                                        # interval=500, blit=False)    
    
    # pl.show()
    
    # When the window is closed, stop acquisition and save data
    # aWorker.kill = True
    # time.sleep(0.5)
    # n = raw_input('Save data in file name -> ')
    # savetxt(n + '.txt', aWorker.data)

# def monitorTDC2(bins = 100, rnge = (0,100), average_rate ):    
    # """ Realtime acquisition and monitor
    
    # :arg bins:
    # :arg rnge:
    
    # When done, close first the Gui.
    # Then the prompt will ask how to save the data.
    
    # It creates an AcquisitionWorker thread, and an animated
    # matplotlib window that updates with data coming from the
    # acquisiton
    # """
    
    # TODO check version of Matplotlib
    
    # Initialize the measurement
    # initTdc(2)
    # time_start = time.time()
    # Start thread for 1 channel acquisition
    # aWorker = AcquisitionWorker2ch(bins = bins, rnge = rnge,
                                    # do_coincidences = True)
    # aWorker.start()

    # Init the figure for displaying the histogram
    
    # def update_line(num):
        # l1.set_data(aWorker.hist[0])
        # l2.set_data(aWorker.hist[1])
        # if max(aWorker.hist[0][1]) > update_line.scale1 *0.85 or \
           # max(aWorker.hist[0][1]) > update_line.scale1 *0.85:
            # update_line.scale1 *= 3
            # ax1.set_ylim(0, update_line.scale1)
            # fig.canvas.draw()
        # l3.set_data(aWorker.hist_c)
        # if max(aWorker.hist_c[1]) > update_line.scale2 *0.85:
            # update_line.scale2 *= 3
            # ax2.set_ylim(0, update_line.scale2)
            # fig.canvas.draw()
        # if server != None:
            # server.values = [aWorker.hist_c[1]]
        # return l1,l2,l3
    
    # fig = pl.figure()
    # ax1 = pl.subplot(121)
    # l1, = pl.plot(aWorker.hist[0][0], aWorker.hist[0][1], 'r-')
    # l2, = pl.plot(aWorker.hist[1][0], aWorker.hist[1][1], 'b-')
    # pl.xlabel('Time (ns)')
    # pl.title('TDC Channel 1,2')
    # update_line.scale1 = 25
    # ax1.set_ylim(0, update_line.scale1)
    # ax2 = pl.subplot(122)
    # l3, = pl.plot(aWorker.hist_c[0], aWorker.hist_c[1], 'g-')
    # pl.xlabel('Time (ns)')
    # pl.title('TDC Coincidences')
    # update_line.scale2 = 25
    # ax2.set_ylim(0, update_line.scale2)
    
    
    # Start the animation, that is a loop were 
    # line_ani = animation.FuncAnimation(fig, update_line, 1,repeat = True,
                                        # interval=500, blit=False)    
    
    # pl.show()
    
    # When the window is closed, stop acquisition and save data
    # aWorker.kill = True
    # time_stop = time.time()
    # time.sleep(0.5)
    # # print aWorker.hist_c[1]
    # print "Time acquisition = %.2f\nN Starts = %d"%(time_stop-time_start,aWorker.n_starts) 
    # n = raw_input('Save data in file name -> ')
    # savetxt(n + '.txt', aWorker.data)  # header = "Time acquisition = %.2f\nN Starts = %d"%(time_stop-time_start,aworker.n_starts) 



import matplotlib

matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as Toolbar
from matplotlib.figure import Figure

import wx
import wx.xrc as xrc

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

        
###########################################################################
## Class MonitorFrame
###########################################################################

class MonitorFrame ( wx.Frame ):
    
    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition,
                            size = wx.Size( 658,546 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        
        bSizerPlots = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_panel1 = PlotPanel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizerPlots.Add( self.m_panel1, 1, wx.EXPAND |wx.ALL, 5 )
        
        self.m_panel2 = PlotPanel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizerPlots.Add( self.m_panel2, 1, wx.EXPAND |wx.ALL, 5 )
        
        
        bSizer1.Add( bSizerPlots, 1, wx.EXPAND, 5 )
        
        bSizerOptions = wx.BoxSizer( wx.VERTICAL )
        
        sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"label" ), wx.HORIZONTAL )
        
        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"StartT (ns)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        sbSizer1.Add( self.m_staticText1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.m_txt_start_t = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        sbSizer1.Add( self.m_txt_start_t, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"StopT (ns)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        sbSizer1.Add( self.m_staticText2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.m_txt_stop_t = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        sbSizer1.Add( self.m_txt_stop_t, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"N Bins", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        sbSizer1.Add( self.m_staticText3, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.m_txt_bins = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        sbSizer1.Add( self.m_txt_bins, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        
        bSizerOptions.Add( sbSizer1, 1, wx.SHAPED, 5 )
        
        bSizer4 = wx.BoxSizer( wx.HORIZONTAL )
        
        bSizer5 = wx.BoxSizer( wx.VERTICAL )
        
        self.m_btn_startstop = wx.Button( self, wx.ID_ANY, u"Start/Stop", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_btn_startstop.SetFont( wx.Font( 20, 74, 90, 92, False, "Arial Black" ) )
        
        bSizer5.Add( self.m_btn_startstop, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
        
        bSizer6 = wx.BoxSizer( wx.VERTICAL )
        
        self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Time Average", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )
        bSizer6.Add( self.m_staticText4, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
        
        self.m_txt_avg_t = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer6.Add( self.m_txt_avg_t, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
        
        
        bSizer5.Add( bSizer6, 1, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 5 )
        
        
        bSizer4.Add( bSizer5, 1, wx.EXPAND, 5 )
        
        m_rdb_nchannelsChoices = [ u"Single Channel", u"Dual Channel" ]
        self.m_rdb_nchannels = wx.RadioBox( self, wx.ID_ANY, u"wxRadioBox", wx.DefaultPosition, wx.DefaultSize, m_rdb_nchannelsChoices, 1, wx.RA_SPECIFY_COLS )
        self.m_rdb_nchannels.SetSelection( 1 )
        bSizer4.Add( self.m_rdb_nchannels, 0, wx.ALL, 5 )
        
        
        bSizerOptions.Add( bSizer4, 1, wx.SHAPED, 5 )
        
        
        bSizer1.Add( bSizerOptions, 1, wx.EXPAND, 5 )
        
        
        self.SetSizer( bSizer1 )
        self.Layout()
        
        self.Centre( wx.BOTH )
        
        # Connect Events
        self.m_txt_start_t.Bind( wx.EVT_TEXT_ENTER, self.changeStopT )
        self.m_txt_stop_t.Bind( wx.EVT_TEXT_ENTER, self.ChangeStopT )
        self.m_txt_bins.Bind( wx.EVT_TEXT_ENTER, self.changeBinN )
        self.m_btn_startstop.Bind( wx.EVT_BUTTON, self.startstop )
        self.a = None
    
    def __del__( self ):
        pass
    
    
    # Virtual event handlers, overide them in your derived class
    def changeStopT( self, event ):
        event.Skip()
    
    def ChangeStopT( self, event ):
        event.Skip()
    
    def changeBinN( self, event ):
        event.Skip()
    
    def startstop( self, event ):
        if not self.a:
            self.a = AcquisitionWorker()
            self.a.start()
            self.p = ProcessingWorker(self.a, (self.m_panel1, self.m_panel2) )
            self.p.start()
        else:
            self.p.kill = True
            self.a.kill = True
            del self.p
            del self.a
            self.a = None
        
        
class MonitorApp(wx.App):
    """Monitor App
    
    when ready app.MainLoop()"""

    def __init__(self, title = "TDC Monitor",):
        wx.App.__init__(self, False)
        self.f = MonitorFrame(None)
        
       
        
        self.f.Show(True)
        
        
if __name__ == "__main__":
    app = MonitorApp()
    app.MainLoop()
    #test()
    #simpleThreadedAcquisition()
    #monitorTDC(bins = 500, rnge = (0,200), average_rate = 1 )
    #monitorTDC2(bins = 200, rnge = (100,200) )
