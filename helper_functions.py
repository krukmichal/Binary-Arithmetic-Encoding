# Helper Functions Below
def zero_out(array,length): # zero out the array from 0 to 256
    for i in range(length):  # zero out count array
        array.insert(i,0)
    return array

# Populates the Cum_Count Array
def cdf(count,cum_count): # populate cum_count array
    for i in range(1,257):
        cum_count[i] += count[i-1]
        cum_count[i] += cum_count[i-1]
    return cum_count

def fill(count,seq):
    total_count = 0
    for byte in seq: # fill count and total_count
        count[byte] += 1
        total_count += 1
    return count,total_count

def flipBit(string):
    bits = int(string,base=2)
    bits = bin(int(string,base=2))[2:].zfill(8)
    bitz = bits[0]
    if bitz == '0':
        bits = '1'+string[1:]
    if bitz == '1':
        bits = '0'+string[1:]
    return bits
def giveCoB(string):
    bits = int(string,base=2)
    bits = bin(int(string,base=2))[2:].zfill(8)
    bitz = bits[0]
    if bitz == '0':
        bits = '1'
    if bitz == '1':
        bits = '0'
    return bits

def count_decode(cum_count):
    count=info
    #print("info:",info)
    for i in range(256):
        count[i] = 0

    return count

def binary(num):
    byte = bin(num)[2:].zfill(8)
    return byte