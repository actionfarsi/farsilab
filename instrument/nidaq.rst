=========
 NiDaqMx
=========
:Author: Alessandro Farsi af342@cornell.edu
:last-edited: 1 June 2012
:revision: 1

Intro
=====================
 
This scripts where devlopped for using 
NiDaq works defining abstract tasks (read values, write values)
that are then executed by the specific device.

The calls are encapsulated in an instrument class, that contains
the inizialization and a reading method.

FreqTask
=====================
.. automodule:: freqtask
   :members:   
   
Scripts that use ``FreqTask``
===============================

``averaged_freq.py``
--------------------
Continuosly read frequency channels and average.
It also uses instrument_server to broadcast the results for monitor


``counter.py``
--------------------
Read ticks (counts) from the channels for a given time.


``parameter_scan``
--------------------
Loop over different parameters (controlling different instruments)
and record the frequency rate.
