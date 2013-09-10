""" Simple Serial Logger """

import time
import visa

s = visa.Instrument("COM12")
f = open(time.strftime("%b-%d-%Y %H:%M", time.localtime())+".log", 'w')

whilte True:
    f.write(int(s.read()))
    f.flush()
    sleep(5)
    