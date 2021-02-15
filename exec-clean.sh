#!/usr/bin/env bash

find . -name "*.py?" -exec rm {} \;
find . -name "__pycache__" -exec rm -rf {} \;
find . -name ".DS_Store" -exec rm {} \;
find . -name "._.DS_Store" -exec rm {} \;

rm -rf build
rm -rf tests/htmlcov
rm -rf doc/html

