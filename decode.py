import time
from math import floor
from helper_functions import *

def decode(seq, info):
    """
    Args:
        seq (Bytes): Byte sequence to be decompressed.
        info (Array): cumulative frequency array which is a sum of all
                    frequencies preceding the byte at location info[byte].

    Returns:
        output (Bytes): Orginal compressed message.
    """
    start_time = time.time()

    print()
    print("BEGINNING DECODING CALCULATIONS... ")
    
    cum_count = info # cum_count:cdf array.
    message = "" # outbytes:output sequnce of bytes
    lower = 0 # lower:lower bound
    upper = 255 # upper bound
    total_count = info[len(info)-1]
    m = 8 # number of bits in buffer
    offset=0
    output = bytearray()
    
    k = 0
    
    for byte in seq:
        message = message + binary(byte)
    
    for _ in range(total_count):
        
        t_bin = message[offset:offset+8] # **(read first m bits of received bitstream into tag t)**
        t = int(t_bin,base=2)
        x = ( (((t - lower + 1) * total_count) - 1 ) / (upper - lower + 1))
        
        for j in range(256):
            if x >= cum_count[j]:
                varx = 0
            else:
                output.append(j-1)
                lower_old = lower
                upper_old = upper
                lower = floor(lower_old + (( upper_old - lower_old + 1 ) * cum_count[j-1]) / total_count)
                upper = floor(lower_old + ((( upper_old - lower_old + 1 ) * cum_count[j]) / total_count) - 1)
                bin_low = binary(lower)
                bin_up = binary(upper)
                
                # COMPARE MSB OF LOWER AND UPPER
                while(True):
                    if bin_low[0] == bin_up[0]:
                        
                        #shift out msb
                        lower = int(bin_low[1:8] + '0',base = 2)
                        upper = int(bin_up[1:8] + '1', base = 2)
                        bin_low = binary(lower)
                        bin_up = binary(upper)
                        
                        offset += 1
                    else:
                        break
                        
                #check E3
                while(True):
                    bin_low = binary(lower)
                    bin_up = binary(upper)
                    
                    if ( (bin_low[1] == '1') and (bin_up[1] == '0')):
                       # print("**SHIFT E3**")
                        lower = int(bin_low[0] + bin_low[2:8] + '0', base = 2)
                        upper = int(bin_up[0] + bin_up[2:8] + '1', base = 2)
                        bin_low = binary(lower)
                        bin_up = binary(upper)
                        message = message[:offset] + str(1 - int(message[offset+1])) + message[offset+2:]
                        # tag = message[offset:offset+m]
                        # int_tag = int(tag,base = 2)   
                    else:
                        break
                break
            
    output = bytes(output)

    end_time = time.time()
    print("\t INPUT FILE SIZE : ",len(seq), " BYTES.")
    print("\t OUTPUT FILE SIZE : ", len(output), " BYTES.")
    print("\t TIME ELAPSED {:.5f}".format((end_time-start_time)), "SECONDS.")
    print("DONE DECODING.")
    print("-----------------------")
    print()
    return output