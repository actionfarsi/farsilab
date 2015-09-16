# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Feb 26 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MonitorFrame
###########################################################################

class MonitorFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 658,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer1 = wx.BoxSizer( wx.HORIZONTAL )
		
		bSizerPlots = wx.BoxSizer( wx.VERTICAL )
		
		
		bSizer1.Add( bSizerPlots, 1, wx.ALL|wx.EXPAND, 5 )
		
		bSizerOptions = wx.BoxSizer( wx.VERTICAL )
		
		sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Histogram Options" ), wx.VERTICAL )
		
		self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"StartT (ns)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )
		sbSizer1.Add( self.m_staticText1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_txt_start_t = wx.TextCtrl( self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer1.Add( self.m_txt_start_t, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"StopT (ns)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2.Wrap( -1 )
		sbSizer1.Add( self.m_staticText2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_txt_stop_t = wx.TextCtrl( self, wx.ID_ANY, u"100", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer1.Add( self.m_txt_stop_t, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"N Bins", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )
		sbSizer1.Add( self.m_staticText3, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_txt_bins = wx.TextCtrl( self, wx.ID_ANY, u"10", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer1.Add( self.m_txt_bins, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		bSizerOptions.Add( sbSizer1, 1, wx.SHAPED|wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )
		
		bSizer4 = wx.BoxSizer( wx.VERTICAL )
		
		bSizer5 = wx.BoxSizer( wx.VERTICAL )
		
		bSizer6 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Time Average", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )
		bSizer6.Add( self.m_staticText4, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_txt_avg_t = wx.TextCtrl( self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6.Add( self.m_txt_avg_t, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		
		bSizer5.Add( bSizer6, 1, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		m_rdb_nchannelsChoices = [ u"Single Channel", u"Dual Channel" ]
		self.m_rdb_nchannels = wx.RadioBox( self, wx.ID_ANY, u"Channels", wx.DefaultPosition, wx.DefaultSize, m_rdb_nchannelsChoices, 1, wx.RA_SPECIFY_COLS )
		self.m_rdb_nchannels.SetSelection( 1 )
		bSizer5.Add( self.m_rdb_nchannels, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_chk_hist = wx.CheckBox( self, wx.ID_ANY, u"Coincidences", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_chk_hist.SetValue(True) 
		bSizer5.Add( self.m_chk_hist, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_text_log = wx.TextCtrl( self, wx.ID_ANY, u"Log\nTDC Off", wx.DefaultPosition, wx.Size( -1,100 ), wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2 )
		bSizer5.Add( self.m_text_log, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_btn_startstop = wx.Button( self, wx.ID_ANY, u"Start/Stop", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btn_startstop.SetFont( wx.Font( 20, 74, 90, 92, False, "Arial Black" ) )
		
		bSizer5.Add( self.m_btn_startstop, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		
		bSizer4.Add( bSizer5, 1, 0, 5 )
		
		
		bSizerOptions.Add( bSizer4, 0, wx.SHAPED, 5 )
		
		
		bSizer1.Add( bSizerOptions, 0, 0, 5 )
		
		
		self.SetSizer( bSizer1 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_txt_start_t.Bind( wx.EVT_TEXT, self.changeOptions )
		self.m_txt_stop_t.Bind( wx.EVT_TEXT, self.changeOptions )
		self.m_txt_bins.Bind( wx.EVT_TEXT, self.changeOptions )
		self.m_txt_avg_t.Bind( wx.EVT_TEXT, self.changeOptions )
		self.m_rdb_nchannels.Bind( wx.EVT_RADIOBOX, self.changeChannel )
		self.m_chk_hist.Bind( wx.EVT_CHECKBOX, self.changeOptions )
		self.m_btn_startstop.Bind( wx.EVT_BUTTON, self.startstop )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def changeOptions( self, event ):
		event.Skip()
	
	
	
	
	def changeChannel( self, event ):
		event.Skip()
	
	
	def startstop( self, event ):
		event.Skip()
	

