from encode import *
from decode import *

if __name__ == "__main__":
    encoded, cum_count = encode(b"ARYTMETYKA")
    decoded = decode(encoded, cum_count)
    print(decoded)