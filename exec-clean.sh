#!/usr/bin/env bash

find . -name "*.py?" -exec rm {} \;
find . -name "__pycache__" -exec rm -rf {} \;
find . -name ".DS_Store" -exec rm {} \;
find . -name "._.DS_Store" -exec rm {} \;

rm -rf build          > /dev/null 2>&1
rm -rf tests/htmlcov  > /dev/null 2>&1
rm -rf doc/html       > /dev/null 2>&1
rm -rf dist           > /dev/null 2>&1
rm -rf tests          > /dev/null 2>&1
rm -rf .pytest_cache  > /dev/null 2>&1
rm .coverage          > /dev/null 2>&1

