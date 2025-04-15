#include <cstdlib>
#include <ctime>
#include <iostream>
#include <fstream>
#include <string>


using namespace std;

int main() {
    srand(static_cast<unsigned int>(time(0)));

    string binary_sequence = "";
    for (int i = 0; i < 128; i++) {
        binary_sequence += (rand() % 2) ? '1' : '0';
    }

    std::ofstream sequence_file("binary_sequence_cpp.txt");
    sequence_file << binary_sequence;
    sequence_file.close();
    return 0;
}