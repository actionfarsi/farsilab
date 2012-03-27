# laser

# gpip

# WA1568.2
# LO
# PO011.0

## Threading test
import visa
import threading
import wx

gpib = visa.instrument("GPIB::30")
        
def OnLaserOn(evt):
    gpib.write("LO")
    gpib.write("OP010.00")

def OnLaserOff(evt):
    gpib.write("LF")
	
def OnSetPower(evt):
    gpib.write("WA"+evt.GetEventObject().GetValue())
    
    
app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
frame = wx.Frame(None, wx.ID_ANY, "Santec Laser Controller") # A Frame is a top-level window.
frame.Show(True)     # Show the frame.

box = wx.BoxSizer(wx.HORIZONTAL)
ctrLaserOn = wx.Button(frame, label="On")
ctrLaserOff = wx.Button(frame, label = "Off")
ctrSetPower = wx.TextCtrl(frame, value="1569.115", style=wx.TE_PROCESS_ENTER)
ctrSetPower.SetEditable(True)
frame.Bind(wx.EVT_BUTTON, OnLaserOn, ctrLaserOn)
frame.Bind(wx.EVT_BUTTON, OnLaserOff, ctrLaserOff)
frame.Bind(wx.EVT_TEXT_ENTER, OnSetPower, ctrSetPower)
#frame.Bind(wx.EVT_TEXT, OnChangePower, ctrSetPower) 

box.Add(ctrLaserOn,  1, wx.EXPAND)
box.Add(ctrLaserOff,  1, wx.EXPAND)
box.Add(ctrSetPower,  1, wx.EXPAND)

frame.SetSizer(box)
frame.SetAutoLayout(1)
box.Fit(frame)

app.MainLoop()