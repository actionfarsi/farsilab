<?php

/*
* PHP code generated with wxFormBuilder (version Feb 26 2014)
* http://www.wxformbuilder.org/
*
* PLEASE DO "NOT" EDIT THIS FILE!
*/

/*
 * Class scanMonitor
 */

class scanMonitor extends wxFrame {
	
	function __construct( $parent=null ){
		parent::__construct ( $parent, wxID_ANY, wxEmptyString, wxDefaultPosition, new wxSize( 580,544 ), wxDEFAULT_FRAME_STYLE|wxTAB_TRAVERSAL );
		
		$this->SetSizeHints( wxDefaultSize, wxDefaultSize );
		
		$bSizer1 = new wxBoxSizer( wxHORIZONTAL );
		
		$bSizer2 = new wxBoxSizer( wxVERTICAL );
		
		
		$bSizer1->Add( $bSizer2, 1, wxEXPAND, 5 );
		
		$bSizer3 = new wxBoxSizer( wxVERTICAL );
		
		$gSizer1 = new wxGridSizer( 0, 2, 0, 0 );
		
		$this->m_staticText4 = new wxStaticText( $this, wxID_ANY, "Wavelength (nm)", wxDefaultPosition, wxDefaultSize, 0 );
		$this->m_staticText4->Wrap( -1 );
		$gSizer1->Add( $this->m_staticText4, 0, wxALL, 5 );
		
		$this->m_txt_l0 = new wxTextCtrl( $this, wxID_ANY, "1510", wxDefaultPosition, wxDefaultSize, 0 );
		$gSizer1->Add( $this->m_txt_l0, 0, wxALL, 5 );
		
		$this->m_staticText5 = new wxStaticText( $this, wxID_ANY, "Width (pm)", wxDefaultPosition, wxDefaultSize, 0 );
		$this->m_staticText5->Wrap( -1 );
		$gSizer1->Add( $this->m_staticText5, 0, wxALL, 5 );
		
		$this->m_txt_g = new wxTextCtrl( $this, wxID_ANY, "4", wxDefaultPosition, wxDefaultSize, 0 );
		$gSizer1->Add( $this->m_txt_g, 0, wxALL, 5 );
		
		$this->m_staticText6 = new wxStaticText( $this, wxID_ANY, "MyLabel", wxDefaultPosition, wxDefaultSize, 0 );
		$this->m_staticText6->Wrap( -1 );
		$gSizer1->Add( $this->m_staticText6, 0, wxALL, 5 );
		
		$this->m_textCtrl6 = new wxTextCtrl( $this, wxID_ANY, wxEmptyString, wxDefaultPosition, wxDefaultSize, 0 );
		$gSizer1->Add( $this->m_textCtrl6, 0, wxALL, 5 );
		
		$this->m_staticText7 = new wxStaticText( $this, wxID_ANY, "MyLabel", wxDefaultPosition, wxDefaultSize, 0 );
		$this->m_staticText7->Wrap( -1 );
		$gSizer1->Add( $this->m_staticText7, 0, wxALL, 5 );
		
		$this->m_textCtrl7 = new wxTextCtrl( $this, wxID_ANY, wxEmptyString, wxDefaultPosition, wxDefaultSize, 0 );
		$gSizer1->Add( $this->m_textCtrl7, 0, wxALL, 5 );
		
		
		$bSizer3->Add( $gSizer1, 1, wxEXPAND, 5 );
		
		$this->m_txt_fit = new wxTextCtrl( $this, wxID_ANY, wxEmptyString, wxDefaultPosition, new wxSize( -1,60 ), wxTE_READONLY );
		$bSizer3->Add( $this->m_txt_fit, 0, wxALL|wxEXPAND, 5 );
		
		$m_lst_resonancesChoices = array();
		$this->m_lst_resonances = new wxListBox( $this, wxID_ANY, wxDefaultPosition, wxDefaultSize, $m_lst_resonancesChoices, 0 );
		$bSizer3->Add( $this->m_lst_resonances, 0, wxALL|wxEXPAND, 5 );
		
		$bSizer5 = new wxBoxSizer( wxHORIZONTAL );
		
		$gSizer3 = new wxGridSizer( 0, 2, 0, 0 );
		
		$this->m_button1 = new wxButton( $this, wxID_ANY, "Scan Single", wxDefaultPosition, wxDefaultSize, 0 );
		$gSizer3->Add( $this->m_button1, 0, wxALL|wxALIGN_CENTER_HORIZONTAL, 5 );
		
		$this->m_button2 = new wxButton( $this, wxID_ANY, "Auto Scan", wxDefaultPosition, wxDefaultSize, 0 );
		$gSizer3->Add( $this->m_button2, 0, wxALL|wxALIGN_CENTER_VERTICAL|wxALIGN_CENTER_HORIZONTAL, 5 );
		
		$this->m_staticText81 = new wxStaticText( $this, wxID_ANY, "Range (pm)", wxDefaultPosition, wxDefaultSize, 0 );
		$this->m_staticText81->Wrap( -1 );
		$gSizer3->Add( $this->m_staticText81, 0, wxALL|wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL, 5 );
		
		$this->m_txt_range = new wxTextCtrl( $this, wxID_ANY, "10", wxDefaultPosition, new wxSize( 40,-1 ), 0 );
		$gSizer3->Add( $this->m_txt_range, 0, wxALL|wxALIGN_CENTER_VERTICAL|wxALIGN_CENTER_HORIZONTAL, 5 );
		
		$this->m_staticText82 = new wxStaticText( $this, wxID_ANY, "Resolution (pm)", wxDefaultPosition, wxDefaultSize, 0 );
		$this->m_staticText82->Wrap( -1 );
		$gSizer3->Add( $this->m_staticText82, 0, wxALL|wxALIGN_CENTER_VERTICAL|wxALIGN_CENTER_HORIZONTAL, 5 );
		
		$this->m_txt_res = new wxTextCtrl( $this, wxID_ANY, ".5", wxDefaultPosition, new wxSize( 40,-1 ), 0 );
		$gSizer3->Add( $this->m_txt_res, 0, wxALL|wxALIGN_CENTER_VERTICAL|wxALIGN_CENTER_HORIZONTAL, 5 );
		
		$this->m_staticText91 = new wxStaticText( $this, wxID_ANY, "N Points", wxDefaultPosition, wxDefaultSize, 0 );
		$this->m_staticText91->Wrap( -1 );
		$gSizer3->Add( $this->m_staticText91, 0, wxALL|wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL, 5 );
		
		$this->m_txt_npoints = new wxStaticText( $this, wxID_ANY, "...", wxDefaultPosition, wxDefaultSize, 0 );
		$this->m_txt_npoints->Wrap( -1 );
		$gSizer3->Add( $this->m_txt_npoints, 0, wxALL|wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL, 5 );
		
		$this->m_button4 = new wxButton( $this, wxID_ANY, "STOP", wxDefaultPosition, wxDefaultSize, 0 );
		$gSizer3->Add( $this->m_button4, 0, wxALL, 5 );
		
		$this->m_button5 = new wxButton( $this, wxID_ANY, "Save Resonances", wxDefaultPosition, wxDefaultSize, 0 );
		$gSizer3->Add( $this->m_button5, 0, wxALL, 5 );
		
		$this->m_button6 = new wxButton( $this, wxID_ANY, "Save All", wxDefaultPosition, wxDefaultSize, 0 );
		$gSizer3->Add( $this->m_button6, 0, wxALL, 5 );
		
		
		$bSizer5->Add( $gSizer3, 1, 0, 5 );
		
		$gSizer2 = new wxGridSizer( 0, 2, 0, 0 );
		
		$this->m_staticText8 = new wxStaticText( $this, wxID_ANY, "Start (nm)", wxDefaultPosition, wxDefaultSize, 0 );
		$this->m_staticText8->Wrap( -1 );
		$gSizer2->Add( $this->m_staticText8, 0, wxALL|wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL, 5 );
		
		$this->m_txt_startl = new wxTextCtrl( $this, wxID_ANY, "1510", wxDefaultPosition, new wxSize( 40,-1 ), 0 );
		$gSizer2->Add( $this->m_txt_startl, 0, wxALL|wxALIGN_CENTER_VERTICAL, 5 );
		
		$this->m_staticText9 = new wxStaticText( $this, wxID_ANY, "FSR (GHZ)", wxDefaultPosition, wxDefaultSize, 0 );
		$this->m_staticText9->Wrap( -1 );
		$gSizer2->Add( $this->m_staticText9, 0, wxALL|wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL, 5 );
		
		$this->m_txt_frs0 = new wxTextCtrl( $this, wxID_ANY, "300", wxDefaultPosition, new wxSize( 40,-1 ), 0 );
		$gSizer2->Add( $this->m_txt_frs0, 0, wxALL|wxALIGN_CENTER_VERTICAL, 5 );
		
		
		$bSizer5->Add( $gSizer2, 0, 0, 5 );
		
		
		$bSizer3->Add( $bSizer5, 1, wxEXPAND, 5 );
		
		
		$bSizer1->Add( $bSizer3, 0, 0, 5 );
		
		
		$this->SetSizer( $bSizer1 );
		$this->Layout();
		
		$this->Centre( wxBOTH );
		
		// Connect Events
		$this->m_txt_l0->Connect( wxEVT_COMMAND_TEXT_UPDATED, array($this, "updateValues") );
		$this->m_txt_g->Connect( wxEVT_COMMAND_TEXT_UPDATED, array($this, "updateValues") );
		$this->m_textCtrl6->Connect( wxEVT_COMMAND_TEXT_UPDATED, array($this, "updateValues") );
		$this->m_textCtrl7->Connect( wxEVT_COMMAND_TEXT_UPDATED, array($this, "updateValues") );
		$this->m_lst_resonances->Connect( wxEVT_COMMAND_LISTBOX_SELECTED, array($this, "selectResonance") );
		$this->m_button1->Connect( wxEVT_COMMAND_BUTTON_CLICKED, array($this, "scanOnce") );
		$this->m_button2->Connect( wxEVT_COMMAND_BUTTON_CLICKED, array($this, "scanAuto") );
		$this->m_txt_range->Connect( wxEVT_COMMAND_TEXT_UPDATED, array($this, "updateValues") );
		$this->m_txt_res->Connect( wxEVT_COMMAND_TEXT_UPDATED, array($this, "updateValues") );
		$this->m_txt_startl->Connect( wxEVT_COMMAND_TEXT_UPDATED, array($this, "updateValues") );
		$this->m_txt_frs0->Connect( wxEVT_COMMAND_TEXT_UPDATED, array($this, "updateValues") );
	}
	
	
	function __destruct( ){
	}
	
	
	// Virtual event handlers, overide them in your derived class
	function updateValues( $event ){
		$event->Skip();
	}
	
	
	
	
	function selectResonance( $event ){
		$event->Skip();
	}
	
	function scanOnce( $event ){
		$event->Skip();
	}
	
	function scanAuto( $event ){
		$event->Skip();
	}
	
	
	
	
	
}

?>
