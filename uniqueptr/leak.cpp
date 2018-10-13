#include <iostream>
#include <vector>
#include "unistd.h"


using namespace std;

int main(int argc, char **argv) {
  std::vector<double*> ss;
  for (int k = 0; k < 10000; k++) {
    ss.clear();
    for (int i = 0; i < 6000; i++) {
      ss.push_back(new double(i + k));
    }
  }
  std::cout << *ss[1] << "\n";
  sleep(15);
}
