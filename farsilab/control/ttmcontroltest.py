# -*- coding: utf-8 -*-
"""
TTM Package Viewer
"""

import socket
import struct
from bitarray import bitarray
from numpy import *
import queue, threading

import ctypes

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

#connect to the socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('127.0.0.1',10503))

dec = struct.Struct('<Q')
header_s = struct.Struct('>8s H H BB 8H')

bitmask_1 = bitarray(64,'little')
bitmask_1[:60] = 1
bitmask_1[60:64] = 0

bitmask_2 = bitarray(64,'little')
bitmask_2[:61] = 0
bitmask_2[61:64] = 1

bitmask = [178 * bitmask_1,
           178 * bitmask_2,
           array(178 * (7 * bitarray('0') + 1 * bitarray('1'))),]

data_buffer_size = 100000
data_buffer = [zeros(data_buffer_size, dtype=longlong),
               zeros(data_buffer_size, dtype='h')]

packet_queue = queue.Queue()


def decodePacket(data_size, data, packet_mode = 'i64u'):
    # Works only for i64bit unpacked mode
    assert (packet_mode == 'i64u')

    global bitmask # Store it for faster access
    
    # Rewrite mask if needed (use dictionary if to boost)
    if  len(data) != len(bitmask[0]):
        print('rewriting bitmask', data_size, len(data)/64)
        bitmask = [data_size *bitmask_1,
                   data_size *bitmask_2,
                   array(data_size * (7 * bitarray('0') + 1 * bitarray('1'))),]

    ## Extract time stamp and channel
    time_stamp = fromstring((data & (bitmask[0])).tobytes(), dtype = '<Q')
    ch =         fromstring((data & (bitmask[1])).tobytes(), dtype = '<b' )
    print(ch)
    return (time_stamp, ch[bitmask[2]]/2/8)

def decodeNetPacket(m):
    ## Packet is header (decoded by 'header' struct)
    ## + data. We analyze header and save on the data
    ## in queue to be processed separately
    h = header_s.unpack(m[:header_s.size])
    
    ## First 4+4 bits are the cookies and the packet version
    assert(h[0] == b'TTM8Data')  
    #assert(h[1] == 0x0401)

    data_size = h[-1] // 8  #bits
    packet_n = h[2]
    data_format = h[3]
    digitalIOstate = h[6]

    data=bitarray(0,'little')
    data.frombytes(m[header_s.size:])

    header = {'data_size': data_size,
              'mode': 'i64u', ### TODO
              'packet_n': packet_n,
              'bytes': m[:header_s.size]}

    return header, data
        

def processPackage():
    global data_buffer
    while True:
        data_size, data, mode = packet_queue.get()
        ttm, ch = decodePacket(data_size, data, mode)
        #print (len(ch))
        step = len(ttm)
        data_buffer[0][:len(ttm)] = ttm
        data_buffer[1][:len(ttm)] = ch
        data_buffer[0] = roll(data_buffer[0],step)
        data_buffer[1] = roll(data_buffer[1],step)
        packet_queue.task_done()


def processNetpacket():
    last_packet = -1
    while True:
        m, add = s.recvfrom(2048)
        header, data = decodeNetPacket(m)
        ## Verify we are not losing net-packages
        if last_packet == -1:
            last_packet = header['packet_n'] - 1
        if header['packet_n'] != (last_packet+1)%2**16:
            print(header['packet_n']-last_packet, " packet miss")
        last_packet = header['packet_n']
        ## put encoded data in the queue
        packet_queue.put( (header['data_size'], data, header['mode']))


m, add = s.recvfrom(2048)
header, data = decodeNetPacket(m)
ttm, ch = decodePacket(header['data_size'], data, header['mode'])
print(diff(ttm)*82.3)
print(ch)
    #print (i, packet_queue.qsize())


## Process the pack of package and save each TTM into the buffer
#t = threading.Thread(target=processPackage)
#t.daemon = True
#t.start()

## Take packet and save in the packet queue
#t2 = threading.Thread(target=processNetpacket)
#t2.daemon = True
#t2.start()

######## GUI ######
# Window + chart

class MyApp(pg.GraphicsWindow):
    def closeEvent(self, event):
        global t2
        del t2
        print('pippo')

if __name__ == '__main__':
    import sys


    win = MyApp()
    win.setWindowTitle('TTM Monitor')
    p1 = win.addPlot()
    d_average = zeros(10)
    curve1 = p1.plot(data_buffer[0])

    def update():
        global d_average
        d_average[0] = len(d_average)/(data_buffer[0][-1]-data_buffer[0][0])
        d_average = roll(d_average,1)
        curve1.setData(d_average)

    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(150)

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
    print('End')

  
#packet_queue.join()

    