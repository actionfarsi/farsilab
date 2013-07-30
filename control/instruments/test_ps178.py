'''

'''

import sys, ps178x
try:
    from win32com.client import Dispatch
except:
    pass
err = sys.stderr.write

def TalkToPS(ps, port, baudrate):
    '''load is either a COM object or a PS178x object.  They have the 
    same interface, so this code works with either.
 
    port is the COM port on your PC that is connected to the power supply.
    baudrate is a supported baud rate of the power supply.
    '''
    def test(cmd, results):
        if results:
            print cmd, "failed:"
            print "  ", results
            exit(1)
        else:
            print cmd
    ps.Initialize(port, baudrate) # Open a serial connection
    print "Time from Power Supply =", ps.TimeNow()
    test("Set to remote control", ps.SetRemoteControl())
    test("Set max voltage", ps.SetMaxVoltage(5))
    test("Set output voltage", ps.SetOutVoltage(2.5))
    test("Set output current", ps.SetOutCurrent(1))
    print "  Input values:" 
    values = ps.GetReading()
    for value in values.split("\t"): print "    ", value
    print "  Product info:"
    values = ps.GetProductInformation()
    for value in values.split("\t"): print "    ", value
    test("Set to local control", ps.SetLocalControl())

def Usage():
    name = sys.argv[0]
    msg = '''Usage:  %(name)s {com|obj} port baudrate
Demonstration python script to talk to a B&K Power supply 1785B series either via the COM
(component object model) interface or via a PS178x object (in PS178x.py).
port is the COM port number on your PC that the power supply is connected to.  
baudrate is the baud rate setting of the power supply
''' % locals()
    print msg
    exit(1)

def main():
    if len(sys.argv) != 4: 
        Usage()
    access_type = sys.argv[1]
    port        = int(sys.argv[2])
    baudrate    = int(sys.argv[3])
    if access_type == "com":
        ps = Dispatch('BKServers.PS178x')
    elif access_type == "obj":
        ps = ps178x.PS178x()
    else:
        Usage()
    TalkToPS(ps, port, baudrate)
    return 0

main()
