#!/bin/bash

mkdir -p test_project
cd test_project || exit 1

echo 'from setuptools import setup' > setup.py
echo 'print("Hello, world!")' > main.py
mkdir tests
echo 'def test_placeholder(): assert True' > tests/test_sample.py

