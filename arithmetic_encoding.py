import time
from bitarray import bitarray
from math import floor


def calc_prob(word):
    word = "".join(sorted(word))
    dct = dict()
    total_count = len(word)

    for num in word:
        dct[num] = dct.get(num, 0) + 1

    res = dict()
    dct_sum = 0
    for key in dct:
        dct[key] = dct[key] / total_count
        res[key] = (dct_sum, dct[key] + dct_sum)
        dct_sum += dct[key]

    return res


def zero_out(array, length):  # zero out the array from 0 to 256
    for i in range(length):  # zero out count array
        array.insert(i, 0)
    return array


# Populates the Cum_Count Array
def cdf(count, cum_count):  # populate cum_count array
    for i in range(1, 257):
        cum_count[i] += count[i - 1]
        cum_count[i] += cum_count[i - 1]
    return cum_count


def fill_count(count, seq):
    for byte in seq:  # fill count
        count[byte] += 1
    return count


def fill_total_count(seq):
    total_count = 0
    for _ in seq:
        total_count += 1
    return total_count


def flipBit(string):
    bits = int(string, base=2)
    bits = bin(int(string, base=2))[2:].zfill(8)
    bitz = bits[0]
    if bitz == '0':
        bits = '1' + string[1:]
    if bitz == '1':
        bits = '0' + string[1:]
    return bits


def giveCoB(bit):
    if bit == '0':
        return '1'
    if bit == '1':
        return '0'


# def count_decode(cum_count):
#     count=info
#     #print("info:",info)
#     for i in range(256):
#         count[i] = 0

#     return count

def binary(num):
    byte = bin(num)[2:].zfill(8)
    return byte


def calculate_cum_count(seq):
    count = []
    cum_count = []
    count = zero_out(count, 256)
    count = fill_count(count, seq)
    cum_count = zero_out(cum_count, 257)
    cum_count = cdf(count, cum_count)
    return cum_count


def encode(seq, prob_table):
    start_time = time.time()
    print()
    print("Compression start...")
    # count = [] 
    # cum_count = [] 
    outbytes = []
    scale3 = 0
    lower = 0
    upper = 255

    # count = zero_out(count,256) 
    # count,total_count = fill(count,seq)
    # cum_count = zero_out(cum_count, 257) 
    # cum_count = cdf(count, cum_count) 

    # total_count = fill_total_count(seq)

    # print("\t Initial word : ", seq)
    print("\t Input size: ", len(seq) * 8, " bits")

    for byte in seq:
        bin_low = binary(lower)
        bin_up = binary(upper)

        lower_old = lower
        upper_old = upper
        lower = floor(lower_old + ((upper_old - lower_old + 1) * prob_table[byte][0]))
        upper = floor(lower_old + ((upper_old - lower_old + 1) * prob_table[byte][1]) - 1)

        bin_low = binary(lower)
        bin_up = binary(upper)

        while (bin_low[0] == bin_up[0]) or ((bin_low[1] == '1') and (bin_up[1] == '0')):
            # bin_low = binary(lower)
            # bin_up = binary(upper)

            if bin_low[0] == bin_up[0]:
                outbytes.append(bin_low[0])
                lower = int(bin_low[1:8] + '0', base=2)
                upper = int(bin_up[1:8] + '1', base=2)
                bin_low = binary(lower)
                bin_up = binary(upper)

                while scale3 > 0:
                    outbytes.append(giveCoB(bin_low[0]))
                    scale3 += -1

            else:
                if (bin_low[1] == '1') and (bin_up[1] == '0'):
                    lower = int(bin_low[0] + bin_low[2:8] + '0', base=2)
                    upper = int(bin_up[0] + bin_up[2:8] + '1', base=2)
                    bin_low = binary(lower)
                    bin_up = binary(upper)
                    scale3 += 1

    i = 0
    while bin_low[i] != '0' and i < 8:
        outbytes.append(bin_low[i])
        i += 1

    # while scale3 > 0:
    #     outbytes.append('1')
    #     scale3 += -1
    #
    # outbytes.append(bin_low[1:8])

    out = "".join(outbytes)

    added_bits = 8 - len(out) % 8
    for _ in range(added_bits):
        out = '0' + out



    output = bitarray(out)
    outbytes = out
    outstuff = output.tobytes()

    end_time = time.time()
    print("\t Output size : ", len(out), " bits")
    print("\t Compression ratio : {:.1f}".format(len(seq) * 8 / len(out)), " input bytes per output byte")
    print("\t Time elapsed {:.5f}".format((end_time - start_time)), "secomds")
    print("End of compression...")
    print()
    print("Encoded: ", out)

    return outstuff, scale3, added_bits


def decode(seq, prob_table, scale3):
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
    print("Decompression start...")

    # cum_count = info  # cum_count:cdf array.
    message = ""  # outbytes:output sequnce of bytes
    lower = 0  # lower:lower bound
    upper = 255  # upper bound
    # total_count = info[len(info) - 1]
    decoded_count = 1
    m = 8  # number of bits in buffer
    offset = 0
    output = []

    # k = 0

    for byte in seq:
        message = message + binary(byte)

    while offset + m <= len(message):

        t_bin = message[offset:offset + m]  # **(read first m bits of received bitstream into tag t)**
        # print(t_bin)
        t = int(t_bin, base=2)
        x = (t - lower) / (upper - lower + 1)

        for prob_range in prob_table:
            if prob_table[prob_range][0] <= x < prob_table[prob_range][1]:
                output.append(prob_range)
                lower_old = lower
                upper_old = upper
                lower = floor(lower_old + ((upper_old - lower_old + 1) * prob_table[prob_range][0]))
                upper = floor(lower_old + ((upper_old - lower_old + 1) * prob_table[prob_range][1]) - 1)

                bin_low = binary(lower)
                bin_up = binary(upper)

                while (bin_low[0] == bin_up[0]) or ((bin_low[1] == '1') and (bin_up[1] == '0')):

                    if bin_low[0] == bin_up[0]:
                        lower = int(bin_low[1:8] + '0', base=2)
                        upper = int(bin_up[1:8] + '1', base=2)
                        bin_low = binary(lower)
                        bin_up = binary(upper)
                        offset += 1

                    else:
                        if (bin_low[1] == '1') and (bin_up[1] == '0'):
                            for _ in range(scale3):
                                lower = int(bin_low[0] + bin_low[1] + bin_low[3:8] + '0', base=2)
                                upper = int(bin_up[0] + bin_up[1] + bin_up[3:8] + '1', base=2)
                                offset += 1
                                bin_low = binary(lower)
                                bin_up = binary(upper)

                # # COMPARE MSB OF LOWER AND UPPER
                # while True:
                #     if bin_low[0] == bin_up[0]:
                #
                #         # shift out msb
                #         lower = int(bin_low[1:8] + '0', base=2)
                #         upper = int(bin_up[1:8] + '1', base=2)
                #         bin_low = binary(lower)
                #         bin_up = binary(upper)
                #
                #         offset += 1
                #     else:
                #         break
                #
                # # check E3
                # while True:
                #     bin_low = binary(lower)
                #     bin_up = binary(upper)
                #
                #     if (bin_low[1] == '1') and (bin_up[1] == '0'):
                #         # print("**SHIFT E3**")
                #         lower = int(bin_low[0] + bin_low[2:8] + '0', base=2)
                #         upper = int(bin_up[0] + bin_up[2:8] + '1', base=2)
                #         bin_low = binary(lower)
                #         bin_up = binary(upper)
                #         message = message[:offset] + str(1 - int(message[offset + 1])) + message[offset + 2:]
                #         # tag = message[offset:offset+m]
                #         # int_tag = int(tag,base = 2)
                #     else:
                #         break
                # break

    #output = bytes(output)

    end_time = time.time()
    print("\t Input size : ", len(seq) * 8, " bits")
    print("\t Output size : ", len(output) * 8, " bits")
    print("\t Time elapsed {:.5f}".format((end_time - start_time)), "seconds")
    print("End of decompression")
    print()
    return output
