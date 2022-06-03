#include <iostream>
#include <map>
#include <vector>
#include <fstream>
#include <algorithm>

std::vector<unsigned char> read_file_bytes(char const* filename)
{
    std::ifstream input(filename, std::ios::binary);

    std::vector<unsigned char> bytes(
         (std::istreambuf_iterator<char>(input)),
         (std::istreambuf_iterator<char>()));

    input.close();
	return bytes;
}


std::map<unsigned char, std::pair<double, double>> calc_prob(std::vector<unsigned char> bytes)
{
    std::sort(bytes.begin(), bytes.end());
	std::map<unsigned char, long long> ocurrences;
	std::map<unsigned char, std::pair<double, double>> probabilities;
	for (auto byte : bytes)
	{
		ocurrences[byte]++;
	}
	double ocurrences_sum = 0.0;
	for (auto pair : ocurrences)
	{
		probabilities[pair.first] = std::make_pair(ocurrences_sum, ((double)pair.second / (double)bytes.size()) + ocurrences_sum);
		ocurrences_sum += ((double)pair.second / (double)bytes.size());
	}
	return probabilities;
	
}

unsigned char msb(unsigned char byte)
{
	return (byte >> 7);
}

unsigned char second_msb(unsigned char byte)
{
	return (byte & 0x7F) >> 6;
}

unsigned char negate_msb(unsigned char byte) 
{
	if ((byte & 0x80) > 0) 
	{
		return byte & 0xFF;
	}
	else 
	{
		return byte | 0x80;
	}
}

void write_four_msb_to_the_end(unsigned char lower, std::vector<unsigned char>& encoded) 
{
	for(int i = 7; i >= 4; i--)
	{
		unsigned char byte = (lower >> i) & 0x01;
		encoded.push_back(byte);
	}
}

//integer arithmetic encoding
std::vector<unsigned char> encode_bytes(std::vector<unsigned char> bytes, std::map<unsigned char, std::pair<double, double>> probabilities) 
{
	std::vector<unsigned char> encoded;
	unsigned char scale3 = 0;
	unsigned char lower = 0;
	unsigned char upper = 255;
	unsigned short width = upper - lower + 1;

	for (auto byte : bytes)
	{
		unsigned char lower_old = lower;
		lower = (unsigned char)(lower + (width * probabilities[byte].first));
		upper = (unsigned char)(lower_old + (width * probabilities[byte].second) - 1);
		width = upper - lower + 1;

		while(msb(lower) == msb(upper) || (second_msb(lower == 1 && second_msb(upper) == 0)))
		{
			if (msb(lower) == msb(upper)) 
			{
				encoded.push_back(msb(upper));
				lower = (unsigned char)(lower << 1);
				upper = (unsigned char)(upper << 1) + (unsigned char)1;
				width = upper - lower + 1;

				while (scale3 > 0) 
				{
					encoded.push_back((unsigned char)1 - msb(upper));
					scale3 -= 1;
				}
			}
			else if (second_msb(lower == 1 && second_msb(upper) == 0)) 
			{
				lower = (unsigned char)(lower << 1);
				upper = (unsigned char)(upper << 1) + 1;
				
				lower = negate_msb(lower);
				upper = negate_msb(upper);
				width = upper - lower + 1;
				
				scale3 += 1;
			}
		}
	}
	write_four_msb_to_the_end(lower, encoded);
	return encoded;
		
}
	


int main()
{
	std::vector<unsigned char> bytes = read_file_bytes("data/lena.pgm");
	std::vector<unsigned char> bytes1{ 'A', 'R', 'Y', 'T', 'M', 'E', 'T', 'Y', 'K', 'A' };
	std::map<unsigned char, std::pair<double, double>> probabilities = calc_prob(bytes1);
	std::vector<unsigned char> encoded = encode_bytes(bytes1, probabilities);
    return 0;
}
