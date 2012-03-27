""" ATDM GB2 Board """

# Address offset
TDCH0 = 0
TDCL0 = 4
MC0   = 6
MBS   = 8
DAC   = 0
STAT0 = 0

## Load ATMD dll
## int GetATMDPCIBoardCount()
## bool GetATMDPCIBaseAddr(int index, DWORD& addr)
## bool EnablePortAccess()

from ctypes import *
atmd_dll = windll.LoadLibrary("ATDM_PCI")

## Init board and find address
def init_atdm():
	if atdm_dll.GetATMDPCIBoardCount() <= 1:
		print "No board found"
	base = c_short()
	if atdm_dll.GetATMDPCIBaseAddr(0, byref(base)):
		print "Board Initializated at addr %o"%base
		return base
	print "Board not initialized (missing giveio.sys?)"
	return 0

## Parallel port
## Inp32(short addr)
## Out32(short addr, short datum)

p = windll.inpout32  ## not standard in win7 (but it is compatible, just download and place)

def test():
	base = init_atdm()
	