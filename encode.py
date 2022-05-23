from bitarray import bitarray
from math import floor
from helper_functions import *

def encode(seq):

    count = [] 
    cum_count = [] 
    outbytes = [] 
    scale3 = 0 
    lower = 0 
    upper = 255 

    count = zero_out(count,256) 
    count,total_count = fill(count,seq)
    cum_count = zero_out(cum_count, 257) 
    cum_count = cdf(count, cum_count) 

    for byte in seq: 
        bin_low = bin(lower)[2:].zfill(8)
        bin_up = bin(upper)[2:].zfill(8)

        lower_old = lower
        upper_old = upper
        lower = floor(lower_old + ((upper_old - lower_old  +1) * cum_count[byte]) / total_count) 
        upper = floor(lower_old + (((upper_old - lower_old + 1) * cum_count[byte + 1]) / total_count) - 1)

        bin_low = bin(lower)[2:].zfill(8)
        bin_up = bin(upper)[2:].zfill(8)

        while ( (bin_low[0] == bin_up[0]) or ((bin_low[1] == '1') and (bin_up[1] == '0')) ):
            bin_low = bin(lower)[2:].zfill(8)
            bin_up = bin(upper)[2:].zfill(8)

            if bin_low[0] == bin_up[0]:
                outbytes.append(bin_low[0]) 
                lower = int(bin_low[1:8] + '0', base = 2) 
                upper = int(bin_up[1:8] + '1', base = 2) 

                while scale3 > 0:
                    outbytes.append(giveCoB(bin_low))
                    scale3 += -1

            else:
                if ((bin_low[1] == '1') and (bin_up[1] == '0') ): 
                    lower = int(bin_low[0] + bin_low[2:8] + '0', base = 2) 
                    upper = int(bin_up[0] + bin_up[2:8] + '1', base = 2) 
                    bin_low = bin(lower)[2:].zfill(8)
                    bin_up = bin(upper)[2:].zfill(8)
                    scale3 += 1

    outbytes.append(bin_low[0])

    while scale3 > 0:
        outbytes.append('1')
        scale3 += -1

    outbytes.append(bin_low[1:8])

    out = "".join(outbytes)

    output = bitarray(out)
    outbytes = out
    outstuff = output.tobytes()
    
    return (outstuff, cum_count)