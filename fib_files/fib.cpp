#include <iostream>
#include <fstream>
#include <chrono>
#include <vector>
using namespace std;

int fib(int n) {
    if (n < 2)
        return 1;
    return fib(n - 1) + fib(n - 2);
}

int main() {
    int n = 40;
    vector<long long> sequence;
    auto start = chrono::high_resolution_clock::now();

    for (int i = 1; i <= n; ++i) {
        long long val = fib(i);
        sequence.push_back(val);
        cout << i << " . fibonacci: " << val << endl;
    }

    auto end = chrono::high_resolution_clock::now();
    double seconds = chrono::duration<double>(end - start).count();

    ofstream f("result_cpp.json");
    f << "{\n"
      << "  \"language\": \"C++\",\n"
      << "  \"n\": " << n << ",\n"
      << "  \"sequence\": [";
    for (size_t i = 0; i < sequence.size(); ++i) {
        f << sequence[i];
        if (i + 1 < sequence.size()) f << ", ";
    }
    f << "],\n"
      << "  \"seconds\": " << seconds << "\n}\n";
    f.close();
}
