#include <iostream>
#include <vector>
#include "unistd.h"
#include <memory>

using namespace std;

int main(int argc, char **argv) {
  std::vector<std::unique_ptr<double>> ss;
  for (int k = 0; k < 10000; k++) {
    ss.clear();
    for (int i = 0; i < 6000; i++) {
      ss.push_back(make_unique<double>(i+k));
    }
  }
  std::cout << *ss[1] << "\n";
  sleep(15);
}
