from arithmetic_encoding import *

if __name__ == "__main__":
    word = b"adfgjoahrgb"
    cum_count = calculate_cum_count(word)
    encoded = encode(b"adfgjoahrgb", cum_count)
    decoded = decode(encoded, cum_count)
    print(decoded)