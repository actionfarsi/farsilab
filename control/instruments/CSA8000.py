import visa
from matplotlib.pylab import *
from scipy.io import savemat
import os, re

if __name__ == "__main__":
    ins = visa.Instrument("GPIB::1")

    ## Init and verify device
    ins.write('SELECTED DEVICE CLEAR')
    print ins.ask('*idn?')
    
    ## Set Encoding do ascii
    ins.write('data:encdg ascii')
    ## Be Sure transfer all the points
    ins.write('data:stop 4000')
    
    ## ask for data
    a = ins.ask('curve?')
    data = [int(i) for i in a.split()[1].split(',')]
    
    ## ask for 
    a = ins.ask('horizontal:main:scale?')
    scale = float(a.split()[-1])
    t = linspace(0,10,len(data))*scale
    
    #plot(t, data)
    #show()
    
    ## Helper for saving files
    file_list = [ f for f in os.listdir('.') if f[-3:] == 'mat'] # get file list
    file_list.sort(key = os.path.getctime) # order by time
    
    file_name = "scan"
    if len(file_list)!= 0:
        m = re.match('(\D*)(\d*).mat', file_list[-1])
        if m:
            try:
                file_name = m.group(1) + "%d"%(int(m.group(2))+1)
            except:
                file_name = m.group(1) + str(1)
    
    print "Insert filename (if nothing %s.mat) --> "%file_name,
    input_name = raw_input()
    
    ## Overwriting control
    while True:
        if input_name != "":
            file_name = input_name
        
        if file_name+".mat" in file_list:
            print "\nWARNING! File will be overwritten.\nPress Enter to confirm. Otherwise type a new name --> ",
            input_name = raw_input()
            if input_name == "":
                break
            continue
        
        break    
        
        
    savemat(file_name + '.mat', {'scale':scale,'data':data, 'time':t  },  oned_as='row')