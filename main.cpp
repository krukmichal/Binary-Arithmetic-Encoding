#include <iostream>
#include <map>
#include <vector>
#include <fstream>
#include <algorithm>
#include <bitset>
#include <stack>
#include <chrono>
#include <random>

#define BITS 0x100000000
#define HALF_BITS 0x80000000
#define QUARTER_BITS 0x40000000


std::vector<unsigned char> read_file_bytes(std::string filename)
{
	std::ifstream input(filename, std::ios::binary);

	std::vector<unsigned char> bytes(
		(std::istreambuf_iterator<char>(input)),
		(std::istreambuf_iterator<char>()));

	input.close();
	return bytes;
}

void write_file_bytes(std::string filename, std::vector<unsigned char> bytes)
{
	std::ofstream output(filename, std::ios::binary);

	output.write(reinterpret_cast<char const*>(&bytes[0]), bytes.size());

	output.close();
}

std::pair<unsigned int, unsigned int> calc_bits(std::vector<unsigned char> bytes)
{
	unsigned int c1 = 0;
	unsigned int c2 = 0;
	for (auto byte : bytes)
	{
		std::bitset<8> b(byte);
		c1 += b.count();
		c2 += 8 - b.count();
	}
	return std::make_pair(c1, c2);
}

void normalize_encode(unsigned int& lower, unsigned int& scale3, unsigned long long& width, std::vector<unsigned char>& encoded)
{
	while (width <= QUARTER_BITS)
	{
		if (lower >= HALF_BITS)
		{
			encoded.push_back(1);
			while (scale3 > 0)
			{
				encoded.push_back(0);
				scale3 -= 1;
			}
			lower -= HALF_BITS;
		}
		else if (lower + width <= HALF_BITS)
		{
			encoded.push_back(0);
			while (scale3 > 0)
			{
				encoded.push_back(1);
				scale3 -= 1;
			}
		}
		else
		{
			scale3 += 1;
			lower -= QUARTER_BITS;
		}
		lower <<= 1;
		width <<= 1;
	}
}

void add_bits_from_lower(unsigned int& lower, unsigned int& scale3, std::vector<unsigned char>& encoded)
{
	std::stack<unsigned char> ending;
	for (int i = 0; i < 32; ++i)
	{
		unsigned int last_bit = lower & 1;
		lower >>= 1;
		if (i == 31)
		{
			while (scale3 > 0)
			{
				ending.push((unsigned int)1 - last_bit);
				scale3 -= 1;
			}
		}
		ending.push(last_bit);
	}
	while (!ending.empty())
	{
		encoded.push_back(ending.top());
		ending.pop();
	}
}

std::vector<unsigned char> binary_encode(std::vector<unsigned char> bytes, unsigned int c1, unsigned int c2)
{
	std::vector<unsigned char> encoded;
	unsigned int lower = 0;
	unsigned long long width = 4294967296;
	unsigned int scale3 = 0;

	for (auto byte : bytes)
	{
		std::bitset<8> b(byte);
		for (int i = 7; i >= 0; --i)
		{
			bool bit = b[i];
			unsigned long long r1 = width * c1/(unsigned long long)(c1 + c2);
			unsigned long long r2 = width - r1;

			if (bit)
			{
				width = r1;
				lower = lower + r2;
			}
			else
			{
				width = r2;
			}
			normalize_encode(lower, scale3, width, encoded);
		}
	}
	add_bits_from_lower(lower, scale3, encoded);
	return encoded;
}

void normalize_decode(unsigned int& lower, unsigned int& input_buffer, unsigned long long& width, std::vector<unsigned char>& encoded, unsigned int& seen_bits)
{
	while (width <= QUARTER_BITS)
	{
		if (lower + width <= HALF_BITS);
		else if (lower >= HALF_BITS)
		{
			lower -= HALF_BITS;
			input_buffer -= HALF_BITS;
		}
		else
		{
			lower -= QUARTER_BITS;
			input_buffer -= QUARTER_BITS;
		}
		lower <<= 1;
		width <<= 1;

		unsigned char next_input_bit;
		if (seen_bits < encoded.size())
		{
			next_input_bit = encoded[seen_bits];
		}
		else
		{
			next_input_bit = 0;
		}
		input_buffer <<= 1;
		input_buffer |= next_input_bit;
		seen_bits += 1;
	}
}

std::vector<unsigned char> binary_decode(std::vector<unsigned char> encoded, unsigned int c1, unsigned int c2)
{
	std::vector<unsigned char> decoded;
	
	unsigned int lower = 0;
	unsigned long long width = 4294967296;

	std::vector<unsigned char> input_array(encoded.begin(), encoded.begin() + 32);
	unsigned int k = 0;
	unsigned int seen_bits = 32;

	unsigned int input_buffer = 0;
	for (int i = 0; i < 32; ++i)
	{
		input_buffer += input_array[i] * std::pow(2, 31 - i);
	}
	
	while (k < c1 + c2) 
	{
		unsigned long long r1 = width * c1 / (unsigned long long)(c1 + c2);
		unsigned long long r2 = width - r1;

		if ((unsigned long long)(input_buffer - lower) >= r2) 
		{
			width = r1;
			lower = lower + r2;
			decoded.push_back(1);
		}
		else 
		{
			width = r2;
			decoded.push_back(0);
		}
		normalize_decode(lower, input_buffer, width, encoded, seen_bits);
		k += 1;
	}
	return decoded;
}

long double binary_entropy(unsigned int c1, unsigned int c2)
{
	long double p1 = (long double)c1 / (long double)(c1 + c2);
	long double p2 = (long double)c2 / (long double)(c1 + c2);
	return -(p1 * std::log2(p1) + p2 * std::log2(p2));
}


double entropy(std::vector<unsigned char> bytes)
{
	std::map<unsigned char, unsigned int> histogram;
	for (auto byte : bytes)
	{
		histogram[byte] += 1;
	}
	double entropy = 0;
	for (auto& pair : histogram)
	{
		double p = (double)pair.second / (double)bytes.size();
		entropy += p * log2(p);
	}
	return -entropy;
}

void test_file(std::vector<unsigned char> bytes, std::string out_file)
{
	std::pair<unsigned int, unsigned int> counts = calc_bits(bytes);
	

	auto encode_begin = std::chrono::high_resolution_clock::now();

	std::vector<unsigned char> encoded = binary_encode(bytes, counts.first, counts.second);

	auto encode_end = std::chrono::high_resolution_clock::now();
	std::chrono::duration<double> encode_time = std::chrono::duration_cast<std::chrono::nanoseconds>(encode_end - encode_begin);
	

	auto decode_begin = std::chrono::high_resolution_clock::now();

	std::vector<unsigned char> decoded = binary_decode(encoded, counts.first, counts.second);

	auto decode_end = std::chrono::high_resolution_clock::now();
	std::chrono::duration<double> decode_time = std::chrono::duration_cast<std::chrono::nanoseconds>(decode_end - decode_begin);

	std::vector<unsigned char> decoded_file;
	int offset = 0;
	while (decoded.size() >= offset + 8)
	{
		std::vector<unsigned char> bytes(decoded.begin() + offset, decoded.begin() + offset + 8);
		unsigned char byte = 0;

		for (int i = 0; i < 8; ++i)
		{
			byte += bytes[i] * std::pow(2, 7 - i);
		}
		decoded_file.push_back(byte);
		offset += 8;
	}
	write_file_bytes(out_file, decoded_file);

	std::cout << "Original size: " << bytes.size() * 8 << " bits" << std::endl;
	std::cout << "Encoded size: " << encoded.size() << " bits" << std::endl;
	std::cout << "Compression ratio: " << (double)encoded.size() / (double)(bytes.size() * 8) << std::endl;
	std::cout << "Compression factor: " << (double)((double)bytes.size() * 8) / (double)encoded.size() << std::endl;
	std::cout << "Saving percentage: " << (double)((double)bytes.size() * 8 - (double)encoded.size()) / (double)(bytes.size() * 8) << std::endl;
	std::cout << "Entropy (8 bit words): " << entropy(bytes) << std::endl;
	std::cout << "Entropy (1 bit words): " << binary_entropy(counts.first, counts.second) << std::endl;
	std::cout << "Encode time: " << encode_time.count() << " ns" << std::endl;
	std::cout << "Decode time: " << decode_time.count() << " ns" << std::endl;
	if (bytes == decoded_file)
	{
		std::cout << "Decoding successful" << std::endl;
	}
	else
	{
		std::cout << "Decoding failed" << std::endl;
	}
	std::cout << std::endl;
}

void test_all_files() 
{
	std::vector<std::string> distributions = {
		"geometr_05.pgm", "geometr_09.pgm", "geometr_099.pgm",
		"laplace_10.pgm", "laplace_20.pgm", "laplace_30.pgm",
		"normal_10.pgm", "normal_30.pgm", "normal_50.pgm", "uniform.pgm"
	};

	std::vector<std::string> images = {
		"barbara.pgm", "boat.pgm", "chronometer.pgm", 
		"lena.pgm",	"mandril.pgm", "peppers.pgm"
	};

	std::vector<std::string> natural_images = {
		"obraz_naturalny_1.jpg", "obraz_naturalny_2.jpg", "obraz_naturalny_3.jpg",
		"obraz_naturalny_4.jpg", "obraz_naturalny_5.jpg", "obraz_naturalny_6.jpg"
	};

	std::cout << "Distributions" << std::endl;
	for (int i = 0; i < distributions.size(); ++i)
	{
		std::vector<unsigned char> bytes = read_file_bytes("data/" + distributions[i]);
		std::cout << "File: " << distributions[i] << std::endl;
		std::string file_path = "out/distributions/" + distributions[i];
		test_file(bytes, file_path);
	}
	std::cout << std::endl;

	std::cout << "Images" << std::endl;
	for (int i = 0; i < images.size(); ++i)
	{
		std::vector<unsigned char> bytes = read_file_bytes("data/" + images[i]);
		std::cout << "File: " << images[i] << std::endl;
		std::string file_path = "out/images/" + images[i];
		test_file(bytes, file_path);
	}
	std::cout << std::endl;
	
	std::cout << "Natural images" << std::endl;
	for (int i = 0; i < natural_images.size(); ++i)
	{
		std::vector<unsigned char> bytes = read_file_bytes("data/natural-images/" + natural_images[i]);
		std::cout << "File: " << natural_images[i] << std::endl;
		std::string file_path = "out/natural-images/" + natural_images[i];
		test_file(bytes, file_path);
	}
	std::cout << std::endl;
}

std::vector<unsigned char> random_bytes(unsigned int count) 
{
	std::random_device device;
	std::mt19937 generator(device());
	std::uniform_int_distribution<unsigned int> distribution(0, 255);
	std::vector<unsigned char> bytes;
	for (int i = 0; i < count; ++i)
	{
		bytes.push_back(distribution(generator));
	}
	return bytes;
}

int main()
{
	test_all_files();
	return 0;
}
