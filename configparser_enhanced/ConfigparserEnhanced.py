#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
# TODO: Implement me!
"""
from __future__ import print_function

#import configparser
#import os
#import pprint
#import re
#import sys


class ConfigparserEnhanced(object):
    """

    Args:
        filename (str): The filename of the .ini file to load.
        profile  (str): The profile or <section> in the .ini file to
            process for an action list.

    Attributes:
        config  ()    : The data from the .ini file as loaded by configparser.
        profile (str) : The profile section from the .ini file that is loaded.
        actions (dict): The actions that would be processed when apply() is called.

    """

    def __init__(self, filename, profile):
        self._file        = filename
        self._profile     = profile
        self._actions     = None
        self._config      = None



