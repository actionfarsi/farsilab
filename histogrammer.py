
from numpy import *
from matplotlib import pylab as pl
import fitting
import sys

""" Stand Alone app to analize histogram

data are a dictionary with

:sol: solution

"""
    
# Used to guarantee to use at least Wx2.8
import wxversion
wxversion.ensureMinimal('2.8')

import matplotlib
matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as Toolbar
from matplotlib.figure import Figure

import wx
import wx.xrc as xrc

class PlotPanel(wx.Panel):
    """ Inspired by example "embedding_in_wx3.py"
    
    Bare matplotlib panel
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        self.fig = Figure((3,2))
        self.canvas = FigureCanvasWxAgg(self, -1, self.fig)
        self.toolbar = Toolbar(self.canvas) #matplotlib toolbar
        self.toolbar.Realize()
        #self.toolbar.set_active([0,1])
        
        ## Now put all into a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        ## This way of adding to sizer allows resizing
        sizer.Add(self.canvas, 1, wx.ALL | wx.EXPAND)
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

class InstrumentFrame(wx.Frame):
    def __init__(self, title = "Visualizer GUI",
                       parent = None,):
        
        self.fitted = None
        self.infoFit = ""
        ## A Frame is a top-level window
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, size = (700,600))
        self.Show(True)     # Show the frame.
        
        self.stdF = wx.Font(14, wx.FONTFAMILY_DEFAULT,
                                  wx.FONTSTYLE_NORMAL,
                                  wx.FONTWEIGHT_NORMAL)
                                  
        self.buttonF = wx.Font(16, wx.FONTFAMILY_DEFAULT,
                                    wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_BOLD)
                                  
        self.SetFont( self.stdF )
        
        self.buttons = []
        
        ## Set Sizer and Automatic Layout
        ##- 4 boxes 1) 3d/contour
        ##          2) slice/animation
        ##          3) Open/save
        ##          4) parameters..
        
        self.box = wx.FlexGridSizer(2,2)
        self.box.SetFlexibleDirection(wx.BOTH)
        
        ### Button Box ######
        ### ========== ######
        buttonbox = wx.BoxSizer(wx.VERTICAL)
        ## Load
        btn = wx.Button(self, label= "Load")
        btn.SetFont( self.buttonF )
    
        ## Bind the event
        def callbackWrap(evt):
            dlg = wx.FileDialog(None, style = wx.OPEN, wildcard = "*.mat")
            if dlg.ShowModal() == wx.ID_OK:
                # User has selected something, get the path, set the window's title to the path
                filename = dlg.GetPath()
                try:
                    try:
                        d1,d2 = loadtxt(filename)
                        data = d2-d1
                    except:
                        data = loadtxt(filename)
                    self.setData(data)
                except:
                    print filename,"  - File error"

            ##v = callback()
            ##txt.SetLabel(str(v))
        
        ## Bind the event
        self.Bind(wx.EVT_BUTTON, callbackWrap, btn) 
        buttonbox.Add(btn,  0, wx.ALL | wx.EXPAND, border = 4)
        
        ## Save
        # # btn = wx.Button(self, label= "Save")
        # # btn.SetFont( self.buttonF )
    
        # # def callbackWrap(evt):
            # # dlg = wx.FileDialog(None, style = wx.SAVE, wildcard = ".mat")
            # # if dlg.ShowModal() == wx.ID_OK:
                # # # User has selected something, get the path, set the window's title to the path
                # # filename = dlg.GetPath()
                # # try:
                    # # savemat(filename, self.data, appendmat = False)
                # # except:
                    # # print filename,"  - File error"
        
        # # ## Bind the event
        # # self.Bind(wx.EVT_BUTTON, callbackWrap, btn) 
        # # buttonbox.Add(btn, 0, wx.ALL | wx.EXPAND, border = 4)
        
        ## Fit
        listFunc = wx.ComboBox(self, style = wx.CB_READONLY)
        listFunc.Append("Exponential")
        listFunc.Append("Lorentzian")
        listFunc.Append("Gaussian")
        listFunc.SetSelection(0)
        
        buttonbox.Add(listFunc, 0, wx.ALL | wx.EXPAND, border = 4)
        
        btn = wx.Button(self, label= "Fit")
        btn.SetFont( self.buttonF )
    
        def callbackWrap(evt):
            self.fitData(listFunc.GetValue())
            self.setData(self.data)
        
        ## Bind the event
        self.Bind(wx.EVT_BUTTON, callbackWrap, btn) 
        buttonbox.Add(btn, 0, wx.ALL | wx.EXPAND, border = 4)
        
        ## Range
        self.txtRange0 = wx.TextCtrl(self)
        self.txtRange1 = wx.TextCtrl(self)
        btn = wx.Button(self, label= "Set Range")
        
        def callbackWrap(evt):
            self.range[0] = float(self.txtRange0.GetValue())
            self.range[1] = float(self.txtRange1.GetValue())
            self.setData(self.data)
            
        self.Bind(wx.EVT_BUTTON, callbackWrap, btn)
        
        rangebox = wx.BoxSizer(wx.HORIZONTAL)
        rangebox.Add(wx.StaticText(self, label = "Min (ns) "))
        rangebox.Add(self.txtRange0)
        buttonbox.Add(rangebox)
        rangebox = wx.BoxSizer(wx.HORIZONTAL)
        rangebox.Add(wx.StaticText(self, label = "Max (ns)"))
        rangebox.Add(self.txtRange1)
        buttonbox.Add(rangebox)
        buttonbox.Add(btn)
        
        self.box.Add(buttonbox)
        
        ### Bins       ######
        ### ========== ######
        self.plot = PlotPanel(self)
        bSizer = wx.BoxSizer( wx.VERTICAL )
        
        ## Slider to select the frame
        self.m_slider = wx.Slider( self, wx.ID_ANY, 20,
                                    10, 35,   # Size
                                    wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
        
        
        
        def onslidertext(evt):
            self.bins = int(10**(self.m_slider.GetValue()/10.))
            self.info.SetLabel("bin size = %.2f ns\n"%((0.+self.range[1]-self.range[0])/self.bins) +  self.infoFit)
        
        def onslider(evt):
            #self.line.set_ydata( abs(self.data['sol'][self.m_slider.GetValue()])**2 )
            #self.vline.set_xdata( [self.z[self.m_slider.GetValue()], self.z[self.m_slider.GetValue()]])
            #self.plot.canvas.draw()
            onslidertext(evt)
            self.setData(self.data)
            #self.slice_plot.canvas.draw()
        
        self.Bind(wx.EVT_SCROLL_CHANGED, onslider, self.m_slider)
        self.Bind(wx.EVT_SCROLL_THUMBTRACK, onslidertext, self.m_slider)
        
        
        bSizer.Add(self.plot,  1,wx.ALL | wx.EXPAND, border = 2)
        bSizer.Add( self.m_slider, 0, wx.ALL|wx.EXPAND, border= 2 )
        
        self.box.Add(bSizer,  1,wx.ALL | wx.EXPAND, border = 2)
        
        
        ### Slice      ######
        ### ========== ######
        self.slice_plot = PlotPanel(self)
        self.box.Add( self.slice_plot, 1, wx.EXPAND |wx.ALL, 2 )
        
        ### Info ######
        ### ==== ######
        self.info = wx.StaticText(self, label = "blah blah")
        #self.description.SetSize((300,-1))
        self.box.Add(self.info, 0, wx.ALL , border = 4)   
        
        
        
        ## Flexible Grid ####
        ## ------------- ####
        self.box.AddGrowableRow(0,4)
        self.box.AddGrowableRow(1,1)
        self.box.AddGrowableCol(0,1)
        self.box.AddGrowableCol(1,3)
        self.SetSizer(self.box)
        self.Layout()
    
    def setData(self, data):
        """ Update with new data """
        self.data = data
        
        ## Data ###
        self.txtRange0.SetValue("%.2f"%self.range[0])
        self.txtRange1.SetValue("%.2f"%self.range[1])
        #solutions = data["sol"]
        
        #self.z = data.get("z", linspace(0,1, len(solutions)) ).flatten()
        #t = data.get("t", linspace(0,1, len(solutions[0]))).flatten()
        #w = data.get("w", linspace(-1,1, len(solutions[0]))).flatten()
        #pot = data.get("pump", None)
        
        
        #title = data.get("title", ["Beam propagation"])[0]
        #notes = data.get("notes", [""])[0]
        #date = data.get("date",[""])[0]
        
        #info = "%s\n%s\n%s"%(title,date, notes)
        
        
        
        ## Plot ###
        axis = self.plot.fig.add_subplot(111)            
        axis.hold(False)
        # Histogram
        
        hist, bin_edges = histogram(data, self.bins, self.range,density = True)
        
        x = (bin_edges[1:]+bin_edges[:-1])/2
        axis.plot(x, hist, 'k')
        axis.hold(True)
        #hist, bin_edges = histogram(data, self.bins*10, range)
        #axis.plot(bin_edges[:-1], hist*10, 'g')
        
        if self.fitted is not None:        
            axis.plot(self.fitted[0],self.fitted[1], 'r')
        
        self.hist = hist
        self.bin_edges = bin_edges
        
        #self.vline = axis.axvline(self.z[-1], linewidth=3, color='k')
        
        ## Slider ###
        #self.m_slider.SetRange(0,len(solutions)-1)
        #self.m_slider.SetValue(len(solutions)-1)
        
        ## Notes ##
        self.info.SetLabel("bin size = %.2f ns\n"%(bin_edges[1]-bin_edges[0]) +  self.infoFit)
        
        self.plot.canvas.draw()            
        #self.slice_plot.canvas.draw()
        
    def fitData(self, type = "Gaussian"):
        delta = fitting.Parameter(1.,'d')
        x0 = fitting.Parameter(0.,'x0')
        a = fitting.Parameter(amax(self.hist),'a')
        
        fitfunc = {"Lorentzian": lambda x: 4*a()/delta() / ( (delta()/2)**2 + (x-x0())**2),
                    "Exponential": lambda x: a() * exp( -abs(x-x0()) * 2 * log(2) / delta() ),
                    "Gaussian": lambda x: a() * exp( - (x-x0())**2 * 2 * log(2) / delta()**2 )}
        print type
        x = (self.bin_edges[1:]+self.bin_edges[:-1])/2.
        fitting.fit(fitfunc[type], [delta,x0,a], x, self.hist,1)

        self.infoFit = "%s fit:\nFWHM = %.2f ns; x0 = %.2f ns; Amax = %.2f"%(type, delta(),x0(),a()) 
        
        self.fitted = linspace(x[0],x[-1],500), fitfunc[type](linspace(x[0],x[-1],500))
        
        
if __name__ == "__main__":
    
    # filename = sys.argv[1]
    # try:
        # d1,d2 = loadtxt(filename)
        # data = d2-d1
    # except:
        # data = loadtxt(filename)
        
    range = [-80,80]
    bins = 100
    
    
    data = random.random(300) * 59
    app = wx.App(False)
    f = InstrumentFrame()
    f.bins = bins
    f.range = range
    f.setData(data)
    
    app.MainLoop()
