
import sys

from ctypes import *

# load DAQMX library
dll = windll.LoadLibrary("nicaiu.dll")

# CONST from NIDAQmx.h
DAQmx_Val_Rising  = 10280
DAQmx_Val_Falling = 10171
DAQmx_Val_CountUp = 10128
DAQmx_Val_ContSamps  = 10123

## Shorthand for the task
class Task():
    def __init__(self):
        self.handle = c_int(0)           #DAQmx TaskHandle
        self.name = "DigitalCounter"             #Task Name
        self.data = c_uint * 1000

        print "Creating a Task"

        #First create the task and get a handle to the task that will be used for all subsequenct operations
        #Function Prototype: int32 DAQmxCreateTask (const char taskName[], TaskHandle *taskHandle);
        
            
     
        self.physical_channel = "Dev1/ctr0"    #Physical Channel: DI0 on Dev1
        self.channel_name = ""             
        

        # Create the task
        self.error(   dll.DAQmxCreateTask(self.name, byref(self.handle))   )
        
        # Add a counter Edge
        # Prototype DAQmxCreateCICountEdgesChan(TaskHandle taskHandle, const char counter[],
        #                   const char nameToAssignToChannel[], int32 edge, uInt32 initialCount, int32 countDirection);
        self.error(   dll.DAQmxCreateCICountEdgesChan(self.handle, self.physical_channel,
                        self.channel_name, DAQmx_Val_Rising, 0 , DAQmx_Val_CountUp))
        
        # Set the clock.
        
        self.error(   dll.DAQmxCfgSampClkTiming(self.handle, "/Dev1/PFI9",
                                    c_double(1000.0), DAQmx_Val_Rising, DAQmx_Val_ContSamps, c_int(1000),1 ) )

    def read(self):
        read = c_int()
        dll.DAQmxReadCounterU32(self.handle,1000,c_double(10.0), self.data(), 1000,byref(read),pointer(c_bool()))
        return read
        
    def error(self,return_value):
        if return_value != 0:
            raise Exception("Error: %d"%return_value)
    
    
class App():
    
    
t = Task()
while True:
    print t.read()    


    
    # app = wx.PySimpleApp( 0 )
    # frame = wx.Frame( None, wx.ID_ANY, 'WxPython and Matplotlib', size=(300,300) )
    # panel = DemoPlotPanel( frame, points, clrs )
    # frame.Show()
    # app.MainLoop()
