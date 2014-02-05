""" Instrument Panel 

Simple Simple Simple GUI

It creates a frame/app with buttons associated to callbacks

addButton       - just execute the callback
addButtonValue  - the value returned is printed on the callback
addValueCtr     - the input text is send to the callback function

TODO addPlot
TODO addButtonSave

"""

# Used to guarantee to use at least Wx2.8
#import wxversion
#wxversion.ensureMinimal('2.8')

import matplotlib

matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as Toolbar
from matplotlib.figure import Figure

import wx
import wx.xrc as xrc
import threading, time


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

class Timer(threading.Thread):
        def __init__(self,callback, timed):
            threading.Thread.__init__(self)
            self.running = True
            self.callback = callback
            self.timed = timed

        def run(self):
            " The things I want to do go here. "
            while self.running == True:
                self.callback(None)
                time.sleep(self.timed)

        def stop(self):
            self.running = False
        
        
class InstrumentFrame(wx.Frame):
    def __init__(self, title = "Instrument GUI",
                       description = "Commands\n\n",
                       parent = None,):
                       
        ## A Frame is a top-level window
        wx.Frame.__init__(self, parent, wx.ID_ANY, title)
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
        self.vbox = wx.BoxSizer(wx.HORIZONTAL)
        self.box = wx.BoxSizer(wx.VERTICAL)
        
        self.vbox.Add(self.box, 1, wx.ALL| wx.EXPAND, border = 0)
        
        #self.box.SetMinSize((300,15))
        
        self.description = wx.StaticText(self, label = description)
        #self.description.SetSize((300,-1))
        self.box.Add(self.description, 1, wx.ALL | wx.EXPAND, border = 4)
        
        self.SetSizer(self.vbox)
        #self.SetAutoLayout(1)
        self.Fit()
    
    def addColumn(self):
        self.box = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.box, 1, wx.ALL | wx.EXPAND, border = 4)
        self.Fit()
    
    def addButton(self, name, callback):
        """ Add a button and connect it to a command 
        
        callback is a function with 0 parameters
        """
        self.buttons.append(wx.Button(self, label= name))
        self.Bind(wx.EVT_BUTTON, lambda evt: callback(), self.buttons[-1])
        self.box.Add(self.buttons[-1],  0,wx.ALL|wx.EXPAND , border = 4)
        self.buttons[-1].SetFont( self.buttonF )
        self.buttons[-1].SetSize( (-1, 20) )
        ## Update layout
        self.box.Fit(self)
    
    def addButtonValue(self, name, callback):
        """ Add button + return value and connect it to a command 
        
        """
        
        ## Editable text control
        txt = wx.StaticText(self, label="--",
                          style= wx.ALIGN_CENTRE | wx.ST_NO_AUTORESIZE)
        txt.SetFont( self.buttonF )
        
        ## Associated button
        btn = wx.Button(self, label= name)
        btn.SetFont( self.buttonF )
        
        ## Bind the event
        def callbackWrap(evt):
            v = callback()
            txt.SetLabel(str(v))
            
            
        self.Bind(wx.EVT_BUTTON, callbackWrap, btn) 

        ## Add to a the sizer
        valueCnt = wx.BoxSizer(wx.HORIZONTAL)
        valueCnt.Add(btn, 0,wx.ALL |wx.EXPAND , border = 4)
        valueCnt.Add(txt, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL , border = 4)
        valueCnt.Fit(self)
        
        self.box.Add(valueCnt,  0, wx.ALL , border = 4)
        ## Update layout
        self.box.Fit(self)
    
    def addList(self, options, callback):
        ## Associated button
        btn = wx.Button(self, label= name)
        btn.SetFont( self.buttonF )
        
        ## Bind the event
        self.Bind(wx.EVT_TEXT_ENTER, lambda evt: callback(txt.GetValue()), txt)
        self.Bind(wx.EVT_BUTTON, lambda evt: callback(txt.GetValue()), btn) 

        ## Add to a the sizer
        valueCnt = wx.BoxSizer(wx.HORIZONTAL)
        valueCnt.Add(btn, 0,wx.ALL, border = 4)
        valueCnt.Add(txt, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL , border = 4)
        valueCnt.Fit(self)
        
        self.box.Add(valueCnt,  0, wx.ALL | wx.EXPAND, border = 4)
        ## Update layout
        self.box.Fit(self)
    
    def addValueCtr(self, name, callback, default = "0"):
        """ Add input + button and connect it to a command 
        
        """
        
        ## Editable text control
        txt = wx.TextCtrl(self, value=default,
                          style=wx.TE_PROCESS_ENTER | wx.TE_CENTRE)
        txt.SetEditable(True)
        txt.SetFont( self.buttonF )
        
        ## Associated button
        btn = wx.Button(self, label= name)
        btn.SetFont( self.buttonF )
        
        ## Bind the event
        self.Bind(wx.EVT_TEXT_ENTER, lambda evt: callback(txt.GetValue()), txt)
        self.Bind(wx.EVT_BUTTON, lambda evt: callback(txt.GetValue()), btn) 

        ## Add to a the sizer
        valueCnt = wx.BoxSizer(wx.HORIZONTAL)
        valueCnt.Add(btn, 0,wx.ALL, border = 4)
        valueCnt.Add(txt, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL , border = 4)
        valueCnt.Fit(self)
        
        self.box.Add(valueCnt,  0, wx.ALL | wx.EXPAND, border = 4)
        ## Update layout
        self.box.Fit(self)

    
        
    def addPlotPanel(self, name, callback, timed = 0, multichannel = False):
        " If timer, the button starts and stops acquisition "
        p = PlotPanel(self)
        
        ## Associated button
        btn = wx.Button(p, label= name)
        btn.SetFont( self.buttonF )
        
        def callbackWrap(evt):
            """ Callback and draw """
            results = callback()
            if not multichannel:
                results = [results]
            
            ## Try to update, if not, replot
            try:
                lines = self.ax.get_lines()
                for i,r in enumerate(results):
                    lines[i].set_ydata(r)
                self.ax.relim()
                self.ax.autoscale_view()
            except Exception as inst:
                print inst
                self.ax = p.fig.add_subplot(111)
                self.ax.hold(True)
                for r in results:
                    self.ax.plot(r)
                
            
            ## Update the canvas
            p.canvas.draw()
    
        

        
        def timerStartStop(evt):
            if p.timer == None:
                p.timer = Timer(callbackWrap, timed)
                p.timer.start()
            else:
                p.timer.stop()
                p.timer = None
                
        ## Bind the event
        if timed <= 0:
            self.Bind(wx.EVT_BUTTON, callbackWrap, btn) 
        
        else:
            p.timer = None
            self.Bind(wx.EVT_BUTTON, timerStartStop, btn)
            
            
        
        ## Add the button to the panel
        p.GetSizer().Add(btn, 0,  wx.ALL | wx.EXPAND,border = 1)
        p.Fit()
        
        self.box.Add(p,  1,wx.ALL | wx.EXPAND, border = 4)
        #self.buttons[-1].SetFont( self.buttonF )
        #self.buttons[-1].SetSize( (-1, 20) )
        ## Update layout
        self.box.Fit(self)
        self.Fit()
        
    
class InstrumentApp(wx.App):
    """Instrument App
    
    Incapsulate app, so that you don't need to import wx.
    just
    
    app = InstrumentApp(title, description)
    app.addButton(foo)
    app.addValueCtr(foo)
    
    when ready
    
    app.MainLoop()"""
    
    
    def __init__(self, title = "Instrument GUI",
                       description = "Commands\n-\n-",):
        wx.App.__init__(self,False)
        self.f = InstrumentFrame(title, description)
        
        self.addValueCtr = self.f.addValueCtr
        self.addButton = self.f.addButton
        self.addButtonValue = self.f.addButtonValue
        self.addPlotPanel = self.f.addPlotPanel
        self.addColumn = self.f.addColumn
        
        
import random
        
def test():
    app = InstrumentApp()  # Create a new app, don't redirect stdout/stderr to a window.
    
    def b1():
        print "b1"

    def b2():
        return "22"
        
    def b3(i):
        print i,"pp"
        
    def b4():
        return [[random.random() for i in xrange(5)],
                [random.random() for i in xrange(5)]]
    
    app.addButton("Do b1",b1)
    app.addButtonValue("Value b2",b2)
    app.addColumn()
    app.addValueCtr("Control b3", b3)
    app.addPlotPanel("Plot b4", b4, multichannel = True, timed = 0.2)
    app.addColumn()
    app.addValueCtr("Control b3", b3)
    app.addPlotPanel("Plot b4", b4, multichannel = True, timed = 0.2)
    
    app.MainLoop()

## Run the test if the module is executed
if __name__ == '__main__':
    test()
    

