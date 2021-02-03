#!/usr/bin/env python3
"""
Setup app using setuptools.

See: https://pypi.org/classifiers/ for classifiers
"""

from setuptools import setup

setup(
    name="configparser_enhanced",
    version="0.0.1",
    description="Environment Modules / LMOD helper",
    url="https://gitlab-ex.sandia.gov/trilinos-devops-consolidation/code/ConfigParserEnhanced",
    author="William McLendon",
    author_email="wcmclen@sandia.gov",
    packages=['configparser_enhanced'],
    install_requires=['configparser'],
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


