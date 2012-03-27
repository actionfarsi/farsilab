# Used to guarantee to use at least Wx2.8
import wxversion
wxversion.ensureMinimal('2.8')

import wx
import wx.aui
import matplotlib as mpl
from numpy import *
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as Canvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2Wx as Toolbar

import threading,time
import random

n = 500
data = zeros(n)
t1 = zeros(n)
data2 = zeros(n)
t2 = zeros(n)





def thread_random2():
        def run():
            while True:
                time.sleep(0.1)
                data2[:-1] = data2[1:]
                data2[-1] = random.random()*10
                t2[:-1] = t2[1:]
                t2[-1] = time.clock()
                
        print "Starting Thread"
        job = threading.Thread(target = run)
        job.start()
        return job        
        

def thread_update(fr,canvas):
        def run():
            while True:
                #time.sleep(0.05)
                canvas.gca().clear()
                canvas.gca().plot(t1-t1[-1],data)
                canvas.gca().plot(t2-t2[-1],data2)
                canvas.gca().set_ylim(0,15)
                canvas.gca().set_xlim(-5,1)
                canvas.canvas.draw()  
                fr.Refresh()
                
        print "Starting Thread"
        job = threading.Thread(target = run)
        job.start()
        return job


class Plot(wx.Panel):
    def __init__(self, parent, id = -1, dpi = None, **kwargs):
        wx.Panel.__init__(self, parent, id=id, **kwargs)
        self.figure = mpl.figure.Figure(dpi=dpi, figsize=(2,2))
        self.canvas = Canvas(self, -1, self.figure)
        self.toolbar = Toolbar(self.canvas)
        self.toolbar.Realize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas,1,wx.EXPAND)
        sizer.Add(self.toolbar, 0 , wx.LEFT | wx.EXPAND)
        self.SetSizer(sizer)


def demo():
    app = wx.PySimpleApp()
    frame = wx.Frame(None,-1,'Plotter')
    sizer = wx.BoxSizer()
    frame.SetSizer(sizer)
    plot = Plot(frame)
    sizer.Add(plot, 1, wx.EXPAND)
    
    plot.figure.gca().plot(data)
    
    frame.Show()
    thread_update(frame,plot.figure)
    thread_random()
    
    app.MainLoop()

if __name__ == "__main__": demo()