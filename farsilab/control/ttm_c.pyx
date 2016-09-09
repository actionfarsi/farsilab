import numpy as np
cimport numpy as np

ctypedef unsigned long long uint64
ctypedef unsigned short   uint16

cdef extern from "ttm_structs.h":
    struct Timetag_I64:
        uint64 time
        uint64 slope
        uint64 channel

    struct TTMDataHeader_t:
        uint16  TTMPacketMagicA
        uint16  TTMPacketMagicB
        uint16 PacketCnt
        uint16 DataSize

def DecodeNetPacket(char* data_p):
    cdef TTMDataHeader_t* data
    data = <TTMDataHeader_t*>data_p

    print(data.TTMPacketMagicA)
    header = {'data_size': data.DataSize,
              'mode': 'i64u', ### TODO
              'packet_n': data.PacketCnt}
    return  header

def eventCounter(int data_size, char* data_p, packet_mode = 'i64u'):
    """ Process a packet and count events
        returns how many events per each channel, 
        and the TT of the first event in the packet.. packet happen at least every 50 ms,
        we dont need much better timescale for caluclating #/s

    """
    cdef Timetag_I64* data 
    cdef int ch
    cdef long[8] event_count
    event_count[:] = [0,0,0,0,0,0,0,0]

    data = <Timetag_I64*>data_p

    for d in range(data_size):
        ch = data[d].channel
        event_count[ch] += 1
    
    return np.array(event_count), data[0].time

def printPacket(int data_size, char* data_p, packet_mode = 'i64u'):
    cdef Timetag_I64* data 
    cdef int ch
    cdef long[8] event_count
    event_count[:] = [0,0,0,0,0,0,0,0]

    data = <Timetag_I64*>data_p

    print(data_size)
    for d in range(data_size):
        print(d, data[d].channel, data[d].time)


def coincidenceCounter(int data_size, char* data_p,
                int start_ch, int stop_ch, unordered,
                last_tt = np.zeros(8, dtype = np.uint64),
                trigger_armed = False,
                packet_mode = 'i64u'):
    """ Process a packet """

    cdef Timetag_I64* data 

    data = <Timetag_I64*>data_p

    cdef np.ndarray[np.uint64_t, ndim=1] last_tt_c = last_tt
    cdef np.ndarray[np.uint64_t, ndim=2] coinc_tags = np.zeros([data_size, 2], dtype=np.uint64)
    #cdef uint64[2][500] coinc_tags  # Prepare a buffer to store the coincidences events
    cdef int coinc_tags_counter = 0

    for d in range(data_size):
        ## If is a start event, arm or rearm the trigger
        if data[d].channel == start_ch:

            #last_tt_c[data[d].channel] = data[d].time
            ## if armed, check if there was a count before the start 
            #if trig_armed and unordered:
            #    if last_tt_c[stop_ch] != 0:
            #        coinc_tags[coinc_tags_counter, 0] = last_tt_c[start_ch]
            #        coinc_tags[coinc_tags_counter, 1] = last_tt_c[stop_ch]
            #        coinc_tags_counter += 1
            #        trig_armed = False
            ## else arm the trigger and update the counter
            #else:
            trig_armed = True
                
        ## If it is a stop event
        elif data[d].channel == stop_ch:
            if trig_armed:
                if unordered and last_tt_c[stop_ch] != 0:
                    ## match with the previous event if it happened closer
                    if (last_tt_c[start_ch]-last_tt_c[stop_ch])<(data[d].time - last_tt_c[start_ch]): 
                        coinc_tags[coinc_tags_counter,0] = last_tt_c[start_ch]
                        coinc_tags[coinc_tags_counter,1] = last_tt_c[stop_ch]
                        coinc_tags_counter += 1
                else:
                    coinc_tags[coinc_tags_counter,0] = last_tt_c[start_ch]
                    coinc_tags[coinc_tags_counter,1] = data[d].time
                    coinc_tags_counter += 1
                trig_armed = False

        last_tt_c[data[d].channel] = data[d].time
    
    return coinc_tags[:coinc_tags_counter,:], last_tt_c, trigger_armed
