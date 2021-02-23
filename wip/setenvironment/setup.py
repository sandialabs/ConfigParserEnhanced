#!/usr/bin/env python3
"""
Setup app using setuptools.

See: https://pypi.org/classifiers/ for classifiers
"""

import os
from setuptools import setup
from setuptools import find_packages

import setenvironment


with open('requirements.txt', 'r') as ifp:
    required = ifp.read().splitlines()


#print("Required Packages:")
#print(required)
#print("SetEnvironment Version")
#print(setenvironment.__version__)


setup(
    name="setenvironment",
    version=setenvironment.__version__,
    description="Environment Modules / LMOD helper",
    url="https://internal.gitlab.server/trilinos-devops-consolidation/code/SetEnvironment",
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
