import ctypes
void = ctypes.c_void_p

ttm_c = ctypes.CDLL('LibTTM')
TTMCntr = void()

print(ttm_c.TTMCntrl_GetVersion())
print(ctypes.create_string_buffer(ttm_c.TTMCntrl_GetErrorName(0)),size = 2000)

