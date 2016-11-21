# -*- coding: utf-8 -*-
"""
TTM Package Viewer and converter
"""

import socket
import struct
from bitarray import bitarray
from numpy import *
import numpy as np
import queue, threading
from time import sleep

import ctypes

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt4.QtCore import QThread
from PyQt4.QtNetwork import QHostAddress, QUdpSocket

import ttm_c


#connect to the socket
address = ('192.168.1.1',10502)
t_bin = 82.3e-12

dec = struct.Struct('<Q')
header_s = struct.Struct('>8s H H BB 8H')

TTFormat = {'1': 'i64u',
            '2': 'i64c'}
#  TTFormat_Unknown          = 0, //!< Data Format Unknown (Should never be used!)
#  TTFormat_IMode_EXT64_FLAT = 1, //!< I-Mode Continuous Flat - 3 Bit Channel - 1 Bit Slope - 60 Bit Timetag
#  TTFormat_IMode_EXT64_PACK = 2, //!< I-Mode Continuous Packed - 1 Bit High(1)/Low(0) - High: 31 Bit Timetag - Low: 3 Bit Channel - 1 Bit Slope - 27 Bit Timetag
# TTFormat_IMode_Cont_RAW29 = 3, //!< I-Mode Continuous - 3 Bit Void - 3 Bit Channel - 8 Bit StartCnt - 1 Bit Slope - 17 Bit Timetag
#  TTFormat_IMode_Cont_RAW32 = 4, //!< I-Mode Continuous - 3 Bit StartOvrCnt - 3 Bit Channel - 8 Bit StartCnt - 1 Bit Slope - 17 Bit Timetag
#  TTFormat_IMode_StartStop_RAW29 = 5, //!< I-Mode Start/Stop - 3 Bit Void - 3 Bit Channel - 8 Bit StartCnt - 1 Bit Slope - 17 Bit Timetag
#  TTFormat_GMode = 6,            //!< G-Mode - 3 Bit Void - 1 Bit Channel - 5 Bit Void - 1 Bit Slope - 22 Bit Timetag
#  TTFormat_RMode = 7,            //!< R-Mode - 3 Bit Void - 1 Bit Channel - 5 Bit Void - 23 Bit Timetag
#  TTFormat_MMode = 8             //!< M-Mode - 3 Bit Void - 1 Bit Channel - 5 Bit StartCnt - 23 Bit Timetag
#} TTMDataFormat_t;


## Defining ctypes structure
class Timetag_header(ctypes.BigEndianStructure):
    _fields_ = [
        ('magicA', ctypes.c_uint16),
        ('magicB', ctypes.c_uint16),
        ('magicC', ctypes.c_uint16),
        ('magicD', ctypes.c_uint16),
        ('packet_version', ctypes.c_uint16),
        ('packet_count', ctypes.c_uint16),
        ('data_format', ctypes.c_uint8),
        ('mmode_div', ctypes.c_uint8),
        ('mmode_timeout', ctypes.c_uint16),
        ('digital_IOstate', ctypes.c_uint16),
        ('run_magic', ctypes.c_uint16),
        ('GPX_clock_conf', ctypes.c_uint16),
        ('reserved_B', ctypes.c_uint16),
        ('reserved_C', ctypes.c_uint16),
        ('user_data', ctypes.c_uint16),
        ('data_size', ctypes.c_uint16),
    ]

class Timetag_I64(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('time', ctypes.c_uint64, 60),
        ('slope', ctypes.c_uint64, 1),
        ('channel', ctypes.c_uint64, 3),
    ]

class Timetag_I64c(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('timehigh', ctypes.c_uint32, 27),
        ('slope', ctypes.c_uint32, 1),
        ('channel', ctypes.c_uint32, 3),
        ('highlow', ctypes.c_uint32,1)
    ]

class Timetag_I64_high(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('timelow', ctypes.c_uint32, 31),
        ('highlow', ctypes.c_uint8,1)
    ]

class Timetag_packet(ctypes.LittleEndianStructure):
    #_pack_ = 1
    _fields_ = [
        #('padding', ctypes.c_uint16),
        ('header', Timetag_header),
        ('data', Timetag_I64*(2*2048)),
    ]

#print(ctypes.sizeof(Timetag_header))
#print(ctypes.sizeof(Timetag_I64))
#print(Timetag_I64.time, Timetag_I64.slope, Timetag_I64.channel)

# Pointers
timetag_header_p = ctypes.POINTER(Timetag_header)
timetag_packet_p = ctypes.POINTER(Timetag_packet)
timetag_I64_p = ctypes.POINTER(Timetag_I64)
timetag_I64c_p = ctypes.POINTER(Timetag_I64c)

print(ctypes.sizeof(Timetag_I64c))

assert ctypes.sizeof(Timetag_header) == 30
assert ctypes.sizeof(Timetag_I64) == 8

packet_queue = queue.PriorityQueue(maxsize = 1000)

compressed_t0 = 0

def decodePacket(bin_data,  data_size = None, packet_mode = 'i64u', track_t0 = False):
    # Works only for i64bit unpacked mode
    print(len(bin_data))
    global compressed_t0
    #assert (packet_mode == 'i64u')
    if packet_mode == 'i64u':
        data_size = len(bin_data)//ctypes.sizeof(Timetag_I64)

        t = ctypes.cast(bin_data, timetag_I64_p)

        time = np.fromiter((i.time for i in t), np.int64, data_size)
        channel = np.fromiter((i.channel for i in t), np.int8, data_size)

    if packet_mode == 'i64c':
        data_size = len(bin_data)//ctypes.sizeof(Timetag_I64c)

        t = ctypes.cast(bin_data, timetag_I64c_p)
        #if t[0].highlow == 0:
        #    ctypes.cast(bin_data, timetag_I64c_p)  
        highlow = np.fromiter((i.highlow for i in t ), np.uint64, data_size)
        time =   np.fromiter((i.timehigh for i in t ), np.uint64, data_size)+(cumsum(highlow))*2**27
        channel = np.fromiter((i.channel for i in t ), np.uint8, data_size)
        time    = time[highlow == 0]
        channel = channel[highlow == 0]

        if track_t0:
            time = time + compressed_t0
            compressed_t0 += sum(highlow)*2**27
        else:
            track_t0 = 0
    return(time, channel)



## Packet analysis (the single packet processing is implemented in c)

class PacketCounter():
    def __init__(self):
        self.event_count = np.zeros((8,1000)) ## For calculating rate, refresh every packet
        self.total_count = np.zeros(8)
        self.last_tt = np.zeros(1000, dtype = np.uint64)

    def processPacket(self, data_size, data_p, packet_mode = 'i64u'):
        event_count, last_tt = ttm_c.eventCounter(data_size, data_p, packet_mode = 'i64u')
        self.event_count[:,:-1] = self.event_count[:,1:]
        self.event_count[:,-1] = event_count
        self.total_count += event_count

        self.last_tt[:-1] = self.last_tt[1:]
        self.last_tt[-1] = last_tt

        #print('total', self.total_count)
        #print((self.index_count[:,0]))

    def get_average(self, n = 100):
        return (np.sum(self.event_count[:,-n:-2],1))/((self.last_tt[-2]-self.last_tt[-n]) * t_bin)

    def reset(self):
        self.index_count = np.zeros((8,1000)) ## For calculating rate, refresh every packet
        self.total_count = np.zeros(8)
        self.last_count = np.zeros((8,1000), dtype = np.uint64)


class Histogrammer():
    def __init__(self, start, stop):
        self.trigger_armed = False
        self.last_tt = np.zeros(8, dtype = np.uint64)
        self.histogram_d = {}
        self.start = start
        self.stop = stop

        self.range = (-1000,1000)

    def processPacket(self, data_size, data_p, packet_mode = 'i64u'):
        coinc_tt, self.last_tt, self.trigger_armed = ttm_c.coincidenceCounter(data_size, data_p,
                                        self.start, self.stop, unordered = True,
                                        last_tt = self.last_tt,
                                        trigger_armed = self.trigger_armed,
                                        packet_mode = 'i64u')

        
        diffs = (array(coinc_tt[:,1] - coinc_tt[:,0], dtype = np.int64))
        h_local = np.unique(diffs, return_counts = True)
        for k,v in zip(*h_local):
            self.histogram_d[k] = self.histogram_d.get(k,0) + v

    def get_histogram(self):
        x = np.sort(np.fromiter(self.histogram_d.keys(), dtype = int64))
        y = np.fromiter((self.histogram_d[xx] for xx in x), dtype= int64, count = len(x))
        return x,y

def TimeRebase():
	""" Convert all the timetags from absolute to relative to a specific channel """
	def init(self, start):
		""" Start channel is the rebase """
		self.start = start
		self.time = 0
		self.t = []
		self.ch = []

	def processPacket(self, data_size, data_packet, packet_mode = 'i64u'):
		t, ch = decodePacket(data_packet, data_size, packet_mode)  # done in python
		new_t = []
		new_ch = []
		for i in range(len(ch)):
			if ch[i] == self.start:
				self.time = t[i]
			else:
				new_t.append(t[i]-self.time)
				new_ch.append(ch[i])
		self.t.append(np.array(new_t, dtype = np.int64))
		self.ch.append(np.array(new_ch, dtype = np.int8))
	



def decodeNetPacket(m):
    ## Packet is header (decoded by 'header' struct)
    ## + data. We analyze header and save on the data
    ## in queue to be processed separately
    packet = ctypes.cast(m, timetag_packet_p).contents
    h = packet.header
    #print(h.magicA.to_bytes(2,'big'), h.magicB.to_bytes(2,'big'))
    #print(h.magicC.to_bytes(2,'big'), h.magicD.to_bytes(2,'big'))
    #print(h.packet_version.to_bytes(2,'big'))
    ## First 4+4 bits are the cookies and the packet version
    #assert(h[0] == b'TTM8Data')  
    #assert(h[1] == 0x0401)

    data_size = h.data_size // 8  #bytes
    packet_n = h.packet_count
    data_format = h.data_format
    digitalIOstate = h.digital_IOstate

    header = {'data_size': data_size,
              'mode': 'i64u', ### TODO
              'packet_n': packet_n,}
    return header
        

def processPackage():
    #global data_buffer
    last_packet = -1
    while True:
        packet_n, (data_size, data, mode) = packet_queue.get()
        packet_queue.task_done()

        ## Verify we are not losing net-packages
        if last_packet == -1:
            last_packet = packet_n - 1
        if packet_n != (last_packet+1)%2**16:
            print(packet_n-last_packet, " packet miss")
        last_packet = packet_n

        #pc.processPacket(data_size,data, mode)
        hh.processPacket(data_size,data, mode)
        #ttm_c.eventCounter(data_size,data, mode)
        #data_buffer[0][:len(ttm)] = ttm
        #data_buffer[1][:len(ttm)] = ch
        #data_buffer[0] = roll(data_buffer[0],step)
        #data_buffer[1] = roll(data_buffer[1],step)
        


def processNetpacket():
    last_packet = -1
    m = ctypes.create_string_buffer(ctypes.sizeof(Timetag_packet))
    while True:
            s.recv_into(m)
            header = decodeNetPacket(m)
            packet_n = header['packet_n']
            
            ## put encoded data in the queue
            packet_queue.put( (header['packet_n'],
                              (header['data_size'], m[30:], header['mode']), ),
                            )

        


#m, add = s.recvfrom(ctypes.sizeof(Timetag_packet))
#header, data = decodeNetPacket(m)
#print(header)

#ttm, ch = decodePacket(header['data_size'], data, header['mode'])
#print(diff(ttm)*82.3)
#print(ch)
    #print (i, packet_queue.qsize())

## Take packet and save in the packet queue
#t2 = threading.Thread(target=processNetpacket)
#t2.daemon = True
#t2.start()


## Process the pack of package and save each TTM into the buffer
#t = threading.Thread(target=processPackage)
#t.daemon = True
#t.start()

    
def processing(s,m):
    s.recv_into(m)
    header = decodeNetPacket(m)
    packet_n = header['packet_n']
    
    ## put encoded data in the queue
    #packet_queue.put( (header['packet_n'],
                      #(header['data_size'], m[30:], header['mode']), ),
                    #)
    #packet_n, (data_size, data, mode) = packet_queue.get()
    #packet_queue.task_done()

    ## Verify we are not losing net-packages
    if last_packet == -1:
        last_packet = packet_n - 1
    if packet_n != (last_packet+1)%2**16:
        print(packet_n-last_packet, " packet miss")
    last_packet = packet_n

    #pc.processPacket(data_size,data, mode)
    hh.processPacket(header['data_size'], m[30:], header['mode'])


pc = PacketCounter()
hh = Histogrammer(7,5)

class QtPacketProcessing(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.socket = QUdpSocket()
        self.socket.bind(QHostAddress(address[0]), address[1])
        self.terminate = False

    def run(self):
        last_packet = -1
        m = ctypes.create_string_buffer(ctypes.sizeof(Timetag_packet)*64)
        while not self.terminate:
            if not self.socket.hasPendingDatagrams():
                continue
            #b_received = s.recv_into(m)
            m, addr, port = self.socket.readDatagram(1024*8)
            #print(m)
            header = decodeNetPacket(m)
            packet_n = header['packet_n']
            #print(packet_n)
            data_size = header['data_size']
            
            #if b_received > (30 + data_size*8):
            #    print('Longer message')
            ## put encoded data in the queue
            #packet_queue.put( (header['packet_n'],
                              #(header['data_size'], m[30:], header['mode']), ),
                            #)
            #packet_n, (data_size, data, mode) = packet_queue.get()
            #packet_queue.task_done()

            ## Verify we are not losing net-packages
            if last_packet == -1:
                last_packet = packet_n - 1
            if packet_n != (last_packet+1)%2**16:
                print(packet_n-last_packet, " packet miss")
            last_packet = packet_n

            #ttm_c.printPacket(data_size, m[30:(data_size+4)*8],  header['mode'])
            pc.processPacket(data_size,  m[30:(data_size+4)*8], header['mode'])
            #hh.processPacket(data_size,  m[30:(data_size+4)*8], header['mode'])

 
######## GUI ######
# Window + chart

class MyApp(pg.GraphicsWindow):
    def closeEvent(self, event):
        global t
        del t
        print('Bye Bye')

pen_color = [(0,255,0),(255,0,0),(0,0,255),(125,125,125),
             (180,180,0),(180,0,180),(0,180,180),(255,0,255)]

if __name__ == '__main__':
    import sys


    win = MyApp()
    win.setWindowTitle('TTM Monitor')
    p1 = win.addPlot()
    
    curve1 = p1.plot(zeros(100))
    p2 = win.addPlot()
    d_average = zeros((100,8))
    c_a = [p2.plot(d_average[i], pen=pen_color[i] ) for i in range(8)]

    def update():
        d_average[:-1,:] = d_average[1:,:]
        d_average[-1,:] = pc.get_average(n=100)
        for i,c in enumerate(c_a):
            c.setData(d_average[:,i])
        hist_data = hh.get_histogram()
        curve1.setData(x = hist_data[0], y = hist_data[1])
        #print(pc.last_tt)
        #print(packet_queue.qsize())
        #print('total {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f}'.format(*pc.total_count))
        #print('rate  {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f}'.format(*pc.get_average()))

        print(pc.get_average())

    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(250)
    t = QtPacketProcessing()
    t.start()
    

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

    print('End')

  
#packet_queue.join()

    