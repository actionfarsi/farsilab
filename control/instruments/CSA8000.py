import visa

if __name__ == "__main__":
    ins = visa.Instrument("GPIB::1")

    ## Init and verify device
    ins.write('SELECTED DEVICE CLEAR')
    ins.ask('*idn?')
    
    ## Set Encoding do ascii
    ins.ask('data:encdg ascii')

    ## ask for data
    a = ins.ask('curve?')
    data = [int(i) for i in a.split()[1].split(',')]
    
    ## ask for 
    a = ins.ask('horizontal:main:scale?')
    scale = float(a.split()[-1])
    plot(arange(len(data))*scale, data)

    filename = raw_input
    savemat(filename + '.mat', {'scale':scale,'data':data },  oned_as='row')