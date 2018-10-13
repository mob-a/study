#!/bin/bash
set -eux
echo "watch memory usage"
g++ -O0 leak.cpp -std=c++14 && ./a.out
g++ -O0 uniq.cpp -std=c++14 && ./a.out
