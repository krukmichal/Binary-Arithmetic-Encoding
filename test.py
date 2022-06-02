from arithmetic_encoding import *
from bitarray import *
import matplotlib.pyplot as plt


def get_bytes_from_file(filename):
    with open(filename, 'rb') as pgmf:
        return plt.imread(pgmf)


if __name__ == "__main__":
    #mybytearray = get_bytes_from_file("./test_data/geometr_05.pgm")
    # word = get_bytes_from_file("./test_data/uniform.pgm")
    # new_word = []
    # for a in word:
    #     for b in a:
    #         new_word.append(b)
    #
    # sorted_word = new_word.copy()
    # sorted_word.sort()
    # prob = calc_prob(sorted_word)
    # cum_count = calculate_cum_count(new_word)
    # print(cum_count)
    # encoded = encode(new_word, cum_count)
    # print(encoded)
    # # print(encoded)
    # # print(len(encoded))
    # decoded = decode(encoded, cum_count)
    # # print(decoded)
    #
    # if new_word == decoded:
    #     print("Success")
    # else:
    #     print("Fail")

    word = "ARYTMETYKA"
    prob_table = calc_prob(word)
    print("Prob table", prob_table)

    encoded, scale3, added_bits = encode("ARYTMETYKA", prob_table)


    decoded = decode(encoded, prob_table, scale3)
    print("Decoded: ", decoded)
