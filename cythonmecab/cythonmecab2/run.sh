#!/bin/bash
set -eux
pyversion=`pyenv version | cut -f 1 -d ' '`
rm -rf cymecab.cpp build
echo $LD_LIBRARY_PATH
python setup.py build_ext -i
rm -f cymecab.cpython-35m-x86_64-linux-gnu.so

g++ -pthread -shared -L~/.pyenv/versions/$pyversion/lib build/temp.linux-x86_64-3.5/cymecab.o build/temp.linux-x86_64-3.5/cymecab_.o -o cymecab.cpython-35m-x86_64-linux-gnu.so -lmecab -lstdc++
python sample.py
