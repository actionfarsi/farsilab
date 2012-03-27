# Voltage Supply
from ps178x import PS178x

# init voltage supply
vs = PS178x()
vs.Initialize(4, 9800) # Open a serial connection

vs.SetLocalControl()

del vs
