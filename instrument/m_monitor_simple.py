import wxmpl, wx
import socket, pickle
import numpy
from instserver import connect

host = '192.168.5.24'    # The remote host
#host = 'localhost'
port = 9999              # The same port as used by the server    

class MonitorApp(wx.App):
    def __init__(self):
        wx.App.__init__(self, redirect = False)
        self.p = wx.Frame(None, id = wx.ID_ANY, title = "Monitor",
                          pos = wx.DefaultPosition, size = wx.Size( 600,400 ),
                          style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        
	
        self.p.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.SetTopWindow(self.p)
        
        self.timer = wx.PyTimer(self.onTimer)
        
        self.frame = wxmpl.PlotPanel(self.p, -1)
        self.frame.set_crosshairs(False)
        self.p.Show(True)

        bSizer1 = wx.BoxSizer( wx.HORIZONTAL )
        bSizer2 = wx.BoxSizer( wx.VERTICAL )       
        
        axes = self.frame.get_figure().gca()
        
        # Attach the StripCharter
        self.charter = wxmpl.StripCharter(axes)
        self.ch = []
        self.ctr = []
        # Read the incoming and decide numbers of channels
        data = pickle.loads(connect("monitor", host, port))
        for d in xrange(len(data)):
            self.ch.append(Channel("D%d"%(d+1)))
            self.ch[-1].data = data[d]
            
            t = wx.TextCtrl(self.p, wx.ID_ANY, "%8.2f"%((data[d])[-1]), wx.DefaultPosition,wx.Size(200,40), 0 )
            t.SetFont( wx.Font( 20, 74, 90, 90, False, "Tahoma" ) )
            self.ctr.append(t)
            bSizer2.Add(t, 1, wx.ALL, 5 )
        
        bSizer1.Add( self.frame, 1, wx.ALL|wx.EXPAND, 5 )
        bSizer1.Add( bSizer2, 0, wx.ALL, 5 )
        
        self.p.SetSizer( bSizer1 )
        self.p.Layout()
		
        self.p.Centre( wx.BOTH )
        
        print self.ctr
        
        self.charter.setChannels(self.ch)
        # Prime the pump and start the timer
        self.charter.update()    
        self.timer.Start(100)
        
    def onTimer(self):     
        i = 0
        for d in pickle.loads(connect("monitor", host, port)):
            self.ch[i].data = d
            self.ch[i].setChanged(True)
            self.ctr[i].SetValue("%8.2f"%d[0])
            print d
            i = i+1
        
        self.charter.update()        
        
class Channel(wxmpl.Channel):
    def getY(self):
        return self.data
    def getX(self):
        return numpy.arange(len(self.data),0,-1)
        
app = MonitorApp()
app.MainLoop()
del app
