'''

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

This python module provides a functional interface to a B&K Power supply (178x series)
through the ps178x object.  This object can also be used as a COM
server by running this module as a script to register it.  All the
power supply object methods return strings.  All units into and out of the
power supply object's methods are in SI units.
 
See the documentation file that came with this script.

$RCSfile: ps178x.py $ 
$Revision: 1.0 $
$Date: 2008/12/19  $
$Author: Jeremy Lo, Don Peterson $
'''
 
from __future__ import division
import sys, time, serial
from string import join
try:
    from   win32com.server.exception import COMException
except:
    pass

# Debugging information is set to stdout by default.  You can change
# the out variable to another method to e.g. write to a different
# stream.
out = sys.stdout.write
nl = "\n"
 
class InstrumentException(Exception): pass

class InstrumentInterface:
    '''Provides the interface to a 26 byte instrument along with utility
    functions.
    '''
    debug = 0  # Set to 1 to see dumps of commands and responses
    length_packet = 26  # Number of bytes in a packet
    convert_current = 1e3  # Convert current in A to 1 mA
    convert_voltage = 1e3  # Convert voltage in V to mV
    convert_power   = 1e3  # Convert power in W to mW
    # Number of settings storage registers
    lowest_register  = 1
    highest_register = 25
    def Initialize(self, com_port, baudrate, address=0):
        self.sp = serial.Serial(com_port-1, baudrate)
        self.address = address
    def DumpCommand(self, bytes):
        '''Print out the contents of a 26 byte command.  Example:
            aa .. 20 01 ..   .. .. .. .. ..
            .. .. .. .. ..   .. .. .. .. ..
            .. .. .. .. ..   cb
        '''
        assert(len(bytes) == self.length_packet)
        header = " "*3
        out(header)
        for i in xrange(self.length_packet):
            if i % 10 == 0 and i != 0:
                out(nl + header)
            if i % 5 == 0:
                out(" ")
            s = "%02x" % ord(bytes[i])
            if s == "00":
                # Use the decimal point character if you see an
                # unattractive printout on your machine.
                #s = "."*2
                # The following alternate character looks nicer
                # in a console window on Windows.
                s = chr(250)*2
            out(s)
        out(nl)
    def CommandProperlyFormed(self, cmd):
        '''Return 1 if a command is properly formed; otherwise, return 0.
        '''
        commands = (
            0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29,
            0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F, 0x31, 0x32, 0x37, 0x12
        )
        # Must be proper length
        if len(cmd) != self.length_packet:
            out("Command length = " + str(len(cmd)) + "-- should be " + \
                str(self.length_packet) + nl)
            return 0
        # First character must be 0xaa
        if ord(cmd[0]) != 0xaa:
            out("First byte should be 0xaa" + nl)
            return 0
        # Second character (address) must not be 0xff
        if ord(cmd[1]) == 0xff:
            out("Second byte cannot be 0xff" + nl)
            return 0
        # Third character must be valid command
        byte3 = "%02X" % ord(cmd[2])
        if ord(cmd[2]) not in commands:
            out("Third byte not a valid command:  %s\n" % byte3)
            return 0
        # Calculate checksum and validate it
        checksum = self.CalculateChecksum(cmd)
        if checksum != ord(cmd[-1]):
            out("Incorrect checksum" + nl)
            return 0
        return 1
    def CalculateChecksum(self, cmd):
        '''Return the sum of the bytes in cmd modulo 256.
        '''
        assert((len(cmd) == self.length_packet - 1) or (len(cmd) == self.length_packet))
        checksum = 0
        for i in xrange(self.length_packet - 1):
            checksum += ord(cmd[i])
        checksum %= 256
        return checksum
    def StartCommand(self, byte):
        return chr(0xaa) + chr(self.address) + chr(byte)
    def SendCommand(self, command):
        '''Sends the command to the serial stream and returns the 26 byte
        response.
        '''
        assert(len(command) == self.length_packet)
        self.sp.write(command)
        response = self.sp.read(self.length_packet)
        assert(len(response) == self.length_packet)
        return response
    def ResponseStatus(self, response):
        '''Return a message string about what the response meant.  The
        empty string means the response was OK.
        '''
        responses = {
            0x90 : "Wrong checksum",
            0xA0 : "Incorrect parameter value",
            0xB0 : "Command cannot be carried out",
            0xC0 : "Invalid command",
            0x80 : "",
        }
        assert(len(response) == self.length_packet)
        assert(ord(response[2]) == 0x12)
        return responses[ord(response[3])]
    def CodeInteger(self, value, num_bytes=4):
        '''Construct a little endian string for the indicated value.  Two
        and 4 byte integers are the only ones allowed.
        '''
        assert(num_bytes == 1 or num_bytes == 2 or num_bytes == 4)
        value = int(value)  # Make sure it's an integer
        s  = chr(value & 0xff)
        if num_bytes >= 2:
            s += chr((value & (0xff << 8)) >> 8)
            if num_bytes == 4:
                s += chr((value & (0xff << 16)) >> 16)
                s += chr((value & (0xff << 24)) >> 24)
                assert(len(s) == 4)
        return s
    def DecodeInteger(self, str):
        '''Construct an integer from the little endian string. 1, 2, and 4 byte 
        strings are the only ones allowed.
        '''
        assert(len(str) == 1 or len(str) == 2 or len(str) == 4)
        n  = ord(str[0])
        if len(str) >= 2:
            n += (ord(str[1]) << 8)
            if len(str) == 4:
                n += (ord(str[2]) << 16)
                n += (ord(str[3]) << 24)
        return n
    def GetReserved(self, num_used):
        '''Construct a string of nul characters of such length to pad a
        command to one less than the packet size (leaves room for the 
        checksum byte.
        '''
        num = self.length_packet - num_used - 1
        assert(num > 0)
        return chr(0)*num
    def PrintCommandAndResponse(self, cmd, response, cmd_name):
        '''Print the command and its response if debugging is on.
        '''
        assert(cmd_name)
        if self.debug:
            out(cmd_name + " command:" + nl)
            self.DumpCommand(cmd)
            out(cmd_name + " response:" + nl)
            self.DumpCommand(response)
    def GetCommand(self, command, value, num_bytes=4):
        '''Construct the command with an integer value of 0, 1, 2, or 
        4 bytes.
        '''
        cmd = self.StartCommand(command)
        if num_bytes > 0:
            r = num_bytes + 3
            cmd += self.CodeInteger(value)[:num_bytes] + self.Reserved(r)
        else:
            cmd += self.Reserved(0)
        cmd += chr(self.CalculateChecksum(cmd))
        assert(self.CommandProperlyFormed(cmd))
        return cmd
    def GetData(self, data, num_bytes=4):
        '''Extract the little endian integer from the data and return it.
        '''
        assert(len(data) == self.length_packet)
        if num_bytes == 1:
            return ord(data[3])
        elif num_bytes == 2:
            return self.DecodeInteger(data[3:5])
        elif num_bytes == 4:
            return self.DecodeInteger(data[3:7])
        else:
            raise Exception("Bad number of bytes:  %d" % num_bytes)
    def Reserved(self, num_used):
        assert(num_used >= 3 and num_used < self.length_packet - 1)
        return chr(0)*(self.length_packet - num_used - 1)
    def SendIntegerToPS(self, byte, value, msg, num_bytes=4):
        '''Send the indicated command along with value encoded as an integer
        of the specified size.  Return the instrument's response status.
        '''
        cmd = self.GetCommand(byte, value, num_bytes)
        response = self.SendCommand(cmd)
        self.PrintCommandAndResponse(cmd, response, msg)
        return self.ResponseStatus(response)
    def GetIntegerFromPS(self, cmd_byte, msg, num_bytes=4):
        '''Construct a command from the byte in cmd_byte, send it, get
        the response, then decode the response into an integer with the
        number of bytes in num_bytes.  msg is the debugging string for
        the printout.  Return the integer.
        '''
        assert(num_bytes == 1 or num_bytes == 2 or num_bytes == 4)
        cmd = self.StartCommand(cmd_byte)
        cmd += self.Reserved(3)
        cmd += chr(self.CalculateChecksum(cmd))
        assert(self.CommandProperlyFormed(cmd))
        response = self.SendCommand(cmd)
        self.PrintCommandAndResponse(cmd, response, msg)
        return self.DecodeInteger(response[3:3 + num_bytes])
    def Dec2Bin(self, number):
        '''convert dec integer to binary string bStr'''
        bStr = ''
        if number < 0:  raise ValueError, "must be a positive integer"
        if number == 0: return '0'
        while number > 0:
            bStr = str(number % 2) + bStr
            number = number >> 1
        return bStr
    def StateBinStr(self, binStr):
        if binStr[0] == "0":
            op_mode = "Front Panel"
        else:
            op_mode = "Remote Control"
            
        if binStr[1:4] == "000":
            fan = "off"
        elif binStr[1:4] == "001":
            fan = "1"
        elif binStr[1:4] == "010":
            fan = "2"
        elif binStr[1:4] == "011":
            fan = "3"
        elif binStr[1:4] == "100":
            fan = "4"
        elif binStr[1:4] == "101":
            fan = "5"

        if binStr[4:6] == "00":
            outp_mode = "Off"
        elif binStr[4:6] == "01":
            outp_mode = "CV"
        elif binStr[4:6] == "10":
            outp_mode = "CC"
        elif binStr[4:6] == "11":
            outp_mode = "Unreg"    

        if binStr[6] == "0":
            heat_pro = "Normal"
        else:
            heat_pro = "Abnormal"

        if binStr[7] == "0":
            out_state = "OFF"
        else:
            out_state = "ON"
        stateStr = ["   Operation Mode: " + str(op_mode), "   Fan Speed: " + str(fan),
                    "   Output Mode: " + str(outp_mode), "   Over heat protection: " + str(heat_pro),
                    "   Output State: " + str(out_state)]
        return join(stateStr, "\t")
    
class PS178x(InstrumentInterface):
    _reg_clsid_      = "{C93DDA51-9B32-4EE4-AD47-FA67E244726D}"
    _reg_desc_       = "B&K PS 178x COM Server"
    _reg_progid_     = "BKServers.PS178x"  # External name
    _public_attrs_   = ["debug"]
    _public_methods_ = [
          "Initialize",
          "TimeNow",
          "TurnPSOn",
          "TurnPSOff",
          "SetRemoteControl",
          "SetLocalControl",
          "SetMaxVoltage",
          "SetOutVoltage",
          "SetOutCurrent",
          "SetCommunicationAddress",
          "GetReading",
          "GetProductInformation",
          "EnableLocalControl",
          "DisableLocalControl",  
    ]
    def Initialize(self, com_port, baudrate, address=0):
        "Initialize the base class"
        InstrumentInterface.Initialize(self, com_port, baudrate, address)
    def TimeNow(self):
        "Returns a string containing the current time"
        return time.asctime()
    def TurnPSOn(self):
        "Turns the power supply output on"
        msg = "Turn power supply output on"
        on = 1
        return self.SendIntegerToPS(0x21, on, msg, num_bytes=1)
    def TurnPSOff(self):
        "Turns the power supply output off"
        msg = "Turn power supply output off"
        off = 0
        return self.SendIntegerToPS(0x21, off, msg, num_bytes=1)
    def SetRemoteControl(self):
        "Sets the power supply to remote control"
        msg = "Set remote control"
        remote = 1
        return self.SendIntegerToPS(0x20, remote, msg, num_bytes=1)
    def SetLocalControl(self):
        "Sets the power supply to local control"
        msg = "Set local control"
        local = 0
        return self.SendIntegerToPS(0x20, local, msg, num_bytes=1)
    def SetMaxVoltage(self, voltage):
        "Sets the maximum output voltage limit"
        msg = "Set max output voltage limit"
        return self.SendIntegerToPS(0x22, voltage*self.convert_voltage, msg, num_bytes=4)
    def SetOutVoltage(self, voltage):
        "Sets the output voltage"
        msg = "Set output voltage"
        return self.SendIntegerToPS(0x23, voltage*self.convert_voltage, msg, num_bytes=4)
    def SetOutCurrent(self, current):
        "Sets the output current"
        msg = "Set output current"
        return self.SendIntegerToPS(0x24, current*self.convert_current, msg, num_bytes=2)
    def SetCommunicationAddress(self, address=0):
        '''Sets the communication address.  Note:  this feature is
        not currently supported.  The communication address should always
        be set to 0.
        '''
        msg = "Set communication address"
        return self.SendIntegerToPS(0x25, address, msg, num_bytes=1)
    def GetReading(self):
        '''Returns the values for present current, present voltage, max.
        voltage, set voltage, set current, and state of power supply
        '''
        cmd = self.StartCommand(0x26)
        cmd += self.Reserved(3)
        cmd += chr(self.CalculateChecksum(cmd))
        assert(self.CommandProperlyFormed(cmd))
        response = self.SendCommand(cmd)
        self.PrintCommandAndResponse(cmd, response, "Get Reading values")
        presout_current = self.DecodeInteger(response[3:5])/self.convert_current
        presout_voltage = self.DecodeInteger(response[5:9])/self.convert_voltage
        ps_state = self.DecodeInteger(response[9])
        state_bin = self.Dec2Bin(ps_state)
        stateStr = self.StateBinStr(state_bin)
        setout_current = self.DecodeInteger(response[10:12])/self.convert_current
        max_voltage = self.DecodeInteger(response[12:16])/self.convert_voltage
        setout_voltage = self.DecodeInteger(response[16:20])/self.convert_voltage
        s = ["Current output current: " + str(presout_current) + " A", "Current output voltage: " + str(presout_voltage) + " V",
             "Power supply state: \t" + str(stateStr), "Output current set to: " + str(setout_current), "Maximum output voltage: " + str(max_voltage),
             "Output voltage set to: " + str(setout_voltage)]
        return join(s, "\t")
    def GetProductInformation(self):
        "Returns model number, serial number, and firmware version"
        cmd = self.StartCommand(0x31)
        cmd += self.Reserved(3)
        cmd += chr(self.CalculateChecksum(cmd))
        assert(self.CommandProperlyFormed(cmd))
        response = self.SendCommand(cmd)
        self.PrintCommandAndResponse(cmd, response, "Get product info")
        model = response[3:8]
        fw = hex(ord(response[9]))[2:] + "."
        fw += hex(ord(response[8]))[2:] 
        serial_number = response[10:20]
        return join(("Model " + str(model), "Serial no. " + str(serial_number), "Firmware version " + str(fw)), "\t")
    def EnableLocalControl(self):
        "Enable local control (i.e., key presses work) of the power supply"
        msg = "Enable local control"
        enabled = 1
        return self.SendIntegerToPS(0x37, enabled, msg, num_bytes=1)
    def DisableLocalControl(self):
        "Disable local control of the power supply"
        msg = "Disable local control"
        disabled = 0
        return self.SendIntegerToPS(0x37, disabled, msg, num_bytes=1)


def Register(pyclass=PS178x):
    from win32com.server.register import UseCommandLine
    UseCommandLine(pyclass)
def Unregister(classid=PS178x._reg_clsid_):
    from win32com.server.register import UnregisterServer
    UnregisterServer(classid)

# Run this script to register the COM server.  Use the command line
# argument --unregister to unregister the server.

if __name__ == '__main__':
    Register()
