#010110
# 01010 111 000110 1101 1010 101010 10 1001 01

#1.
# aaabbbbccc
# dct['a'] = 0.3 
# dct['b'] = 0.4

#2.
# 

import math
from bitarray import bitarray
from bitarray.util import ba2int, int2ba

def calc_prob(words):
    dct = dict()
    sum_chars = 0;

    for word in words:
        sum_chars += len(word)

        for ch in word:
            dct[ch] = dct.get(ch,0) + 1

    res = dict()
    dct_sum = 0
    for key in dct:
        dct[key] = dct[key] / sum_chars
        #res[key] = (round(dct_sum * size), round((dct[key] + dct_sum)* size))
        res[key] = (dct_sum, dct[key] + dct_sum)
        dct_sum += dct[key]

    return res




#aaa
#(0 - 0.3) * 255 = 0 - 
#(0, 76)
def encode(word, dct, size):
    left = bitarray("0"*size)
    right = bitarray("1"*size)

    encoded = ""

    for ch in word:
        #print(ch)
        oldleft = left
        left = int2ba(math.ceil(ba2int(left) + (ba2int(right)-ba2int(left) + 1) * dct[ch][0]), length=8)
        right = int2ba(math.ceil(ba2int(oldleft) + (ba2int(right)-ba2int(oldleft) + 1) * dct[ch][1]), length=8)
        #print(left)
        #print(right)

        x = bitarray("1"*size)
        while (left & x) >> 7 == (right & x) >> 7:
            encoded += str(ba2int((left & x) >> 7))
            left = left << 1
            right = (right << 1) | bitarray("00000001")

             

    return encoded


if __name__ == "__main__":
    prob_table = calc_prob(["ab", "aa", "bb", "bc", "cc"])
    print(prob_table)
    print(encode("bb", prob_table, 8))
    # ba = int2ba(ba2int(bitarray("100")) - ba2int(bitarray("001")), length=8)
    # print(ba)
    # ba = (ba << 1) | bitarray("00000001")
    # print(ba)

