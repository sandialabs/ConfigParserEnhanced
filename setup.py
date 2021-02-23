#!/usr/bin/env python3
"""
Setup app using setuptools.

See: https://pypi.org/classifiers/ for classifiers
"""
from setuptools import setup
from setuptools import find_packages

import configparserenhanced


with open('requirements.txt', 'r') as ifp:
    required = ifp.read().splitlines()


print("Required Packages:")
print(required)


setup(
    name="configparserenhanced",
    version=configparserenhanced.__version__,
    description="Extensible configuration .ini file parser helper.",
    url="https://gitlab-ex.sandia.gov/trilinos-devops-consolidation/code/ConfigParserEnhanced",
    author="William McLendon",
    author_email="wcmclen@sandia.gov",
    packages=find_packages(),
    install_requires=required,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Devops',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        ],
    )


