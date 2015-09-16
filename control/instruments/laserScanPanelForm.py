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
## Class scanMonitor
###########################################################################

class scanMonitor ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 580,544 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer1 = wx.BoxSizer( wx.HORIZONTAL )
		
		bSizer2 = wx.BoxSizer( wx.VERTICAL )
		
		bSizer2.SetMinSize( wx.Size( 400,-1 ) ) 
		
		bSizer1.Add( bSizer2, 1, wx.EXPAND, 5 )
		
		bSizer3 = wx.BoxSizer( wx.VERTICAL )
		
		bSizer7 = wx.BoxSizer( wx.HORIZONTAL )
		
		gSizer1 = wx.GridSizer( 0, 2, 0, 0 )
		
		self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Wavelength (nm)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )
		gSizer1.Add( self.m_staticText4, 0, wx.ALL, 5 )
		
		self.m_txt_l0 = wx.TextCtrl( self, wx.ID_ANY, u"1510", wx.DefaultPosition, wx.Size( 80,-1 ), 0 )
		gSizer1.Add( self.m_txt_l0, 0, wx.ALL, 5 )
		
		self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, u"Width (pm)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText5.Wrap( -1 )
		gSizer1.Add( self.m_staticText5, 0, wx.ALL, 5 )
		
		self.m_txt_g = wx.TextCtrl( self, wx.ID_ANY, u"4", wx.DefaultPosition, wx.Size( 80,-1 ), 0 )
		gSizer1.Add( self.m_txt_g, 0, wx.ALL, 5 )
		
		self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, u"area", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText6.Wrap( -1 )
		gSizer1.Add( self.m_staticText6, 0, wx.ALL, 5 )
		
		self.m_txt_area = wx.TextCtrl( self, wx.ID_ANY, u"1", wx.DefaultPosition, wx.Size( 80,-1 ), 0 )
		gSizer1.Add( self.m_txt_area, 0, wx.ALL, 5 )
		
		self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, u"y0", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText7.Wrap( -1 )
		gSizer1.Add( self.m_staticText7, 0, wx.ALL, 5 )
		
		self.m_txt_y0 = wx.TextCtrl( self, wx.ID_ANY, u"1", wx.DefaultPosition, wx.Size( 80,-1 ), 0 )
		gSizer1.Add( self.m_txt_y0, 0, wx.ALL, 5 )
		
		
		bSizer7.Add( gSizer1, 1, 0, 5 )
		
		gSizer2 = wx.GridSizer( 0, 2, 0, 0 )
		
		self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, u"AutoScan", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText11.Wrap( -1 )
		self.m_staticText11.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		
		gSizer2.Add( self.m_staticText11, 0, wx.ALL, 5 )
		
		self.m_staticText12 = wx.StaticText( self, wx.ID_ANY, u"...", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText12.Wrap( -1 )
		gSizer2.Add( self.m_staticText12, 0, wx.ALL, 5 )
		
		self.m_staticText8 = wx.StaticText( self, wx.ID_ANY, u"Start (nm)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText8.Wrap( -1 )
		gSizer2.Add( self.m_staticText8, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_txt_startl = wx.TextCtrl( self, wx.ID_ANY, u"1510", wx.DefaultPosition, wx.Size( 80,-1 ), 0 )
		gSizer2.Add( self.m_txt_startl, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText13 = wx.StaticText( self, wx.ID_ANY, u"Stop (nm)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText13.Wrap( -1 )
		gSizer2.Add( self.m_staticText13, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_txt_stopl = wx.TextCtrl( self, wx.ID_ANY, u"1630", wx.DefaultPosition, wx.Size( 80,-1 ), 0 )
		gSizer2.Add( self.m_txt_stopl, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"FSR (GHZ)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText9.Wrap( -1 )
		gSizer2.Add( self.m_staticText9, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_txt_fsr0 = wx.TextCtrl( self, wx.ID_ANY, u"300", wx.DefaultPosition, wx.Size( 80,-1 ), 0 )
		gSizer2.Add( self.m_txt_fsr0, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		bSizer7.Add( gSizer2, 1, 0, 5 )
		
		
		bSizer3.Add( bSizer7, 0, wx.EXPAND, 5 )
		
		self.m_txt_fit = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,60 ), wx.TE_MULTILINE|wx.TE_READONLY )
		bSizer3.Add( self.m_txt_fit, 0, wx.ALL|wx.EXPAND, 5 )
		
		bSizer6 = wx.BoxSizer( wx.HORIZONTAL )
		
		m_chc_laserChoices = []
		self.m_chc_laser = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_chc_laserChoices, 0 )
		self.m_chc_laser.SetSelection( 1 )
		bSizer6.Add( self.m_chc_laser, 0, wx.ALL, 5 )
		
		self.m_staticText14 = wx.StaticText( self, wx.ID_ANY, u"Autoscan script", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText14.Wrap( -1 )
		bSizer6.Add( self.m_staticText14, 0, wx.ALL, 5 )
		
		m_chc_autoscrChoices = []
		self.m_chc_autoscr = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_chc_autoscrChoices, 0 )
		self.m_chc_autoscr.SetSelection( 0 )
		bSizer6.Add( self.m_chc_autoscr, 0, wx.ALL, 5 )
		
		
		bSizer3.Add( bSizer6, 0, 0, 5 )
		
		bSizer5 = wx.BoxSizer( wx.HORIZONTAL )
		
		m_lst_resonancesChoices = []
		self.m_lst_resonances = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_lst_resonancesChoices, 0 )
		bSizer5.Add( self.m_lst_resonances, 0, wx.ALL|wx.EXPAND, 5 )
		
		gSizer3 = wx.GridSizer( 0, 2, 0, 0 )
		
		self.m_btn_start = wx.Button( self, wx.ID_ANY, u"Scan Single", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer3.Add( self.m_btn_start, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_btn_auto = wx.Button( self, wx.ID_ANY, u"Auto Scan", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer3.Add( self.m_btn_auto, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_staticText81 = wx.StaticText( self, wx.ID_ANY, u"Range (pm)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText81.Wrap( -1 )
		gSizer3.Add( self.m_staticText81, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_txt_range = wx.TextCtrl( self, wx.ID_ANY, u"10", wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
		gSizer3.Add( self.m_txt_range, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_staticText82 = wx.StaticText( self, wx.ID_ANY, u"Resolution (pm)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText82.Wrap( -1 )
		gSizer3.Add( self.m_staticText82, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_txt_res = wx.TextCtrl( self, wx.ID_ANY, u".5", wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
		gSizer3.Add( self.m_txt_res, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_staticText91 = wx.StaticText( self, wx.ID_ANY, u"N Points", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText91.Wrap( -1 )
		gSizer3.Add( self.m_staticText91, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_txt_npoints = wx.StaticText( self, wx.ID_ANY, u"...", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txt_npoints.Wrap( -1 )
		gSizer3.Add( self.m_txt_npoints, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_btn_fit = wx.Button( self, wx.ID_ANY, u"Fit Again", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer3.Add( self.m_btn_fit, 0, wx.ALL|wx.EXPAND, 5 )
		
		m_chc_fitChoices = []
		self.m_chc_fit = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_chc_fitChoices, 0 )
		self.m_chc_fit.SetSelection( 1 )
		gSizer3.Add( self.m_chc_fit, 1, wx.ALL, 5 )
		
		self.m_btn_saveres = wx.Button( self, wx.ID_ANY, u"Save Resonances", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer3.Add( self.m_btn_saveres, 0, wx.ALL, 5 )
		
		self.m_staticline2 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		gSizer3.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.m_btn_saveall = wx.Button( self, wx.ID_ANY, u"Save All", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer3.Add( self.m_btn_saveall, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_btn_loadall = wx.Button( self, wx.ID_ANY, u"Load All", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer3.Add( self.m_btn_loadall, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )
		
		
		bSizer5.Add( gSizer3, 0, wx.EXPAND, 5 )
		
		
		bSizer3.Add( bSizer5, 1, wx.EXPAND, 5 )
		
		self.m_dirPicker1 = wx.DirPickerCtrl( self, wx.ID_ANY, wx.EmptyString, u"Select a folder", wx.DefaultPosition, wx.DefaultSize, wx.DIRP_DEFAULT_STYLE )
		self.m_dirPicker1.Enable( False )
		
		bSizer3.Add( self.m_dirPicker1, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer1.Add( bSizer3, 0, 0, 5 )
		
		
		self.SetSizer( bSizer1 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_txt_l0.Bind( wx.EVT_TEXT, self.updateValues )
		self.m_txt_g.Bind( wx.EVT_TEXT, self.updateValues )
		self.m_txt_area.Bind( wx.EVT_TEXT, self.updateValues )
		self.m_txt_y0.Bind( wx.EVT_TEXT, self.updateValues )
		self.m_txt_startl.Bind( wx.EVT_TEXT, self.updateValues )
		self.m_txt_fsr0.Bind( wx.EVT_TEXT, self.updateValues )
		self.m_lst_resonances.Bind( wx.EVT_KEY_UP, self.selectDel )
		self.m_lst_resonances.Bind( wx.EVT_LISTBOX, self.selectResonance )
		self.m_btn_start.Bind( wx.EVT_BUTTON, self.scanOnce )
		self.m_btn_auto.Bind( wx.EVT_BUTTON, self.scanAuto )
		self.m_txt_range.Bind( wx.EVT_TEXT, self.updateValues )
		self.m_txt_res.Bind( wx.EVT_TEXT, self.updateValues )
		self.m_btn_fit.Bind( wx.EVT_BUTTON, self.fitAgain )
		self.m_btn_saveres.Bind( wx.EVT_BUTTON, self.saveRes )
		self.m_btn_saveall.Bind( wx.EVT_BUTTON, self.saveAll )
		self.m_btn_loadall.Bind( wx.EVT_BUTTON, self.loadAll )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def updateValues( self, event ):
		event.Skip()
	
	
	
	
	
	
	def selectDel( self, event ):
		event.Skip()
	
	def selectResonance( self, event ):
		event.Skip()
	
	def scanOnce( self, event ):
		event.Skip()
	
	def scanAuto( self, event ):
		event.Skip()
	
	
	
	def fitAgain( self, event ):
		event.Skip()
	
	def saveRes( self, event ):
		event.Skip()
	
	def saveAll( self, event ):
		event.Skip()
	
	def loadAll( self, event ):
		event.Skip()
	

