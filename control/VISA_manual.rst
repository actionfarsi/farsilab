===========================
 VISA instrument Manual
===========================
:Author: Alessandro Farsi af342@cornell.edu
:last-edited: 29 January 2013
:revision: 1

Requirements
------------
* PyVisa
* Visa (use NiVisa from National Instrument website. It's a big download for Win)
* Any communication interface (GPIB, Serial, UsbtoSerial...)


Using PyVisa to control instrumentation
=======================================

:: 
 
 import visa
 instrument = visa.Instrument('GPIB::4')
 
 print instrument.ask('*IDN?')

 
List of available instruments
=============================

The code for each instrument is different depending on
the needs of the particular experiment we were running.
**Use them as a reference**

* ''pm100'' Thorlabs powermeter. Results are sent through the network via ''instrumentserver''
* ''santec'' Santec tunable laser. This present a simple GUI
* ''osas'' Selection of communication from differnt scopes and spectrum analyzers
* ''awg'' Arbitray Wavefunction Generator (Tektronik) 

API
========
.. automodule:: TDC_reader
   :members:   