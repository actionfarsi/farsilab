""" Data Block Converter
To be used with AWG """
 
import struct, numpy
    
def decodeWaveform(raw_data):
    ## Skip Header
    cursor = raw_data.find('\r\n') + 3
    
    ## extractDataBlocks
    n_digits = int(raw_data[cursor])
    buffer_size = int(raw_data[cursor+1:cursor+1+n_digits])/5
    
    cursor = cursor + 1 + n_digits 
    data = [ struct.unpack('<fb', raw_data[cursor + i*5:cursor + i*5 + 5])[0] for i in xrange(buffer_size) ]
    # TODO return also the marker bit
    return numpy.array(data)
    
    
def encodeWaveform(data):
    header = 'MAGIC 1000\r\n'
    buffer_size_s = str(len(data)*5)
    buffer_header = '#' + str(len(buffer_size_s)) + buffer_size_s
    body = [  struct.pack('<fb', d, 0) for d in data ]
    body = ''.join(body)
    return header + buffer_header + body
    
def test():
    import visa
    import matplotlib.pylab as pl
    inst = visa.Instrument('GPIB::14')
    r = inst.ask('MMEM:DATA? "10ns.wfm"')
    
    d = decodeWaveform(r)
    r = encodeWaveform(numpy.sin(numpy.linspace(0,6,100)))
    
    buffer_size_s = str(len(r))
    buffer_header = '#' + str(len(buffer_size_s)) + buffer_size_s
    print buffer_header
    
    inst.write('MMEM:DATA "10Sinsc.wfm",' + buffer_header + r)
    #pl.plot(d)
    #pl.show()
    
    
test()
#raw_input()