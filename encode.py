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
    left = bitarray("0"*8)
    right = bitarray("1"*8)

    encoded = ""

    for ch in word:
        #print(ch)
        left = math.ceil(left + (right-left + 1) * dct[ch][0])
        right = math.ceil(left + (right-left + 1) * dct[ch][1])
        #print(left)
        #print(right)

        for i in range(size - 1, 0, -1):
            x = pow(2, i)
            if left & x == right & x:
            else: 
                break

    print(encoded)
    return encoded


if __name__ == "__main__":
    #print(calc_prob(["aaa", "bbbb", "ccc"],255))
    #prob_table = calc_prob(["0101"])
    #print(encode("a", prob_table, 8))
    ba = bitarray("10101010")
    print(ba)
    ba = ba << 1
    print(ba)

