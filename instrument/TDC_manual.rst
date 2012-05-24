===========================
 Coincindence Board Manual
===========================
:Author: Alessandro Farsi af342@cornell.edu
:last-edited: 22 May 2012
:revision: 1

How to use it (quick)
=====================
 
1. Connect all the cables
2. Open ``TDC_reader.py`` and go on the last line code.
   Call the function ``monitorTDC()``
3. Execute the file.
   It will run 2 windows, **1** the prompt, **2** a GUI
   showing, hopefully, a realtime histogram.
   If **2** appears empty, but **1** reads meaningful output,
   you must change the histogram range adding the parameter ``rng``
   parameter (i.e. ``monitorTDC(rng = (0,100) )``

4. Once done, close **2** window
5. On **1** it will be asked a name to save the data.

Intro
=====

We use Acam GP2 chip. The chip is installed on a demonstration board
that contains all the connection needed to use the chip. Unfortunately
the software that comes with it (and the controller PicoProg2) are limited
for the use.

We developed our custom controller on a Arduino-like board.
The communication scheme is the following::

    Gp2 <-- SPI --> Max32 <-- Serial-on-usb --> PC

The necessary code:

* ``GP2Max32.pde`` is firmware code to be uploaded to the microcontroller.
    It's written in a c-like language, and it can be compiled
    and uploaded using MPIDE (http://www.acam-usa.com/GP2.html)

* ``TDC_reader.py`` is the client, it contains both the routines for
    comunicationg with the micro-controller and to visualize data.

Software needed
----------------
 
* python 2.7 (http://www.python.org/)
    not p3-compatible
    
* FTD2XX.DLL (http://www.ftdichip.com/Drivers/D2XX.htm)
    to communicate serial at low lowel with more control than pyvisa
    it's included in the drivers for the Max32
    
* numpy (http://numpy.scipy.org/)
* matplotlib 1.1.0 or greater (http://matplotlib.sourceforge.net/)
  to analyze and plot the data.

* MPIDE (https://github.com/chipKIT32/chipKIT32-MAX/downloads)
  firmware compiler and uploader


Wiring the board
================

 ======== ======== ========= =========
  GP2      Serial   Color      Pin
 ======== ======== ========= =========
  SELECT            Brown     53
  RESET             Brown     51
  MISO              Red       50
  MOSI              White     48
  CLK               Black     52
  GROUND            Black     Ground
  INT               Green     3
  Vcc               Red       Vcc
 ======== ======== ========= =========
 
MISO,MOSI,CLOCK and SELECT are output for the SPI communication
INT is the interrupt, from the GP2
RESET to reset the GP2
Vcc and GROUND are for power supply

Firmware
=========

The firmware controls the GP2, translates commands from 
the pc to SPI, read GP2 output, buffers the results and
sends it back to the computer.

For sake of simplicity and speed, there is very little
error control. In case of failure, often one has to re-upload the
firmware.

Commands are sent as single char with additional integer (*not char*)
options.

``a``
    test the board 
    return a test string "T2D Board + ch2"

``t``
    return the status byte
    
``r``
    read buffer.
    It returns N, D1, D2, D3, ..., DN.
    N is the number of datas. data are given in ''int'' (4 bytes)
    If the TDC is set to read 2 channels, it returns N, D1, D2, D3, ..., DN, DD1, DD2, DD3, ..., DDN.

``w + REG_ADDRESS + 4BYTES``
    write the 4 bytes in the given address, for setting up the GP2

``s + REG_ADDRESS``
    read from the given address,
    reads 0 - status
    1 - first write register
    2,3,4,5 - measured values
    
``p``
    reset

    

Client
=======

The client file contains everything needed to use the board.

- serial comunication initialization
- commands/helper for the TDC
- test routines
- acquisition routines
- monitor for the acquisition

it can be used both as standalone and as module.
Refer to the documentation on the file itself.

The monitor functionality ("TDCmonitor()") is based on animation 
capability of *matplotlib*. A thread is started and it pulls continuosly the serial for new data,
storing them in an array and building a histogram. Another thread is created by *matplotlib* as gui, where the histogram
is updated and drawn. When this happen, the main loop is halted.
This is the reason why you need to close the GUI first in order to save the data.

API
========
.. automodule:: TDC_reader
   :members:   