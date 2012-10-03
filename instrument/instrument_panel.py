""" Instrument Panel 

Simple Simple Simple GUI



"""

import wx

gpib = None#visa.instrument("GPIB::30")
    
class InstrumentFrame(wx.Frame):
    def __init__(self, title = "Instrument GUI",
                       description = "Commands\n\n",
                       parent = None,):
                       
        ## A Frame is a top-level window
        wx.Frame.__init__(self, parent, wx.ID_ANY, title)
        self.Show(True)     # Show the frame.
        
        self.stdF = wx.Font(16, wx.FONTFAMILY_DEFAULT,
                                  wx.FONTSTYLE_NORMAL,
                                  wx.FONTWEIGHT_NORMAL)
                                  
        self.buttonF = wx.Font(20, wx.FONTFAMILY_DEFAULT,
                                    wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_BOLD)
                                  
        self.SetFont( self.stdF )
        
        self.buttons = []
        
        ## Set Sizer and Automatic Layout
        self.box = wx.BoxSizer(wx.VERTICAL)
        
        self.box.SetMinSize((300,15))
        
        self.description = wx.StaticText(self, label = description)
        self.box.Add(self.description, 1, wx.ALL | wx.EXPAND, border = 4)   
        
        self.SetSizer(self.box)
        self.SetAutoLayout(1)
        self.box.Fit(self)
        
    def addButton(self, name, callback):
        """ Add a button and connect it to a command 
        
        callback is a function with 0 parameters
        """
        self.buttons.append(wx.Button(self, label= name))
        self.Bind(wx.EVT_BUTTON, lambda evt: callback(), self.buttons[-1])
        self.box.Add(self.buttons[-1],  1,wx.ALL | wx.EXPAND, border = 4)
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
        valueCnt.Add(btn, 1,wx.ALL | wx.EXPAND, border = 4)
        valueCnt.Add(txt, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL , border = 4)
        valueCnt.Fit(self)
        
        self.box.Add(valueCnt,  1, wx.ALL | wx.EXPAND, border = 4)
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
        valueCnt.Add(btn, 1,wx.ALL | wx.EXPAND, border = 4)
        valueCnt.Add(txt, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL , border = 4)
        valueCnt.Fit(self)
        
        self.box.Add(valueCnt,  1, wx.ALL | wx.EXPAND, border = 4)
        ## Update layout
        self.box.Fit(self)

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
                       description = "Commands\n\n",):
        wx.App.__init__(self,False)
        self.f = InstrumentFrame()
        
        self.addValueCtr = self.f.addValueCtr
        self.addButton = self.f.addButton
        self.addButtonValue = self.f.addButtonValue
        
def test():
    app = InstrumentApp()  # Create a new app, don't redirect stdout/stderr to a window.
    
    def b1():
        print "b1"

    def b2():
        return "22"
        
    def b3(i):
        print i,"pp"
    
    app.addButton("B1",b1)
    app.addButtonValue("b2",b2)
    app.addValueCtr("b3", b3)
    
    
    app.MainLoop()

#test()
    

