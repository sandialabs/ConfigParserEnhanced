#!/usr/bin/env bash

find . -name "*.py?" -exec rm {} \;
find . -name "__pycache__" -exec rm -rf {} \;
find . -name ".DS_Store" -exec rm {} \;
find . -name "._.DS_Store" -exec rm {} \;

rm -rf build
rm -rf tests/htmlcov
rm -rf tests/coverage.json
rm -rf tests/coverage.xml
rm -rf doc/html
rm -rf dist
