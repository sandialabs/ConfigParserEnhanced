#!/usr/bin/env python
# -*- coding: utf-8; mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
"""
from __future__ import print_function
import sys
sys.dont_write_bytecode = True

import os
sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pprint import pprint

import unittest
from unittest import TestCase

# Coverage will always miss one of these depending on the system
# and what is available.
try:                                               # pragma: no cover
    import unittest.mock as mock                   # pragma: no cover
except:                                            # pragma: no cover
    import mock                                    # pragma: no cover

from mock import Mock
from mock import MagicMock
from mock import patch

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

from configparser_enhanced import ConfigparserEnhanced



#===============================================================================
#
# General Utility Functions
#
#===============================================================================

def find_config_ini(filename="config.ini", rootpath="." ):
    """
    Recursively searches for a particular file among the subdirectory structure.
    If we find it, then we return the full relative path to `pwd` to that file.

    The _first_ match will be returned.

    Args:
        filename (str): The _filename_ of the file we're searching for. Default: 'config.ini'
        rootpath (str): The _root_ path where we will begin our search from. Default: '.'

    Returns:
        String containing the path to the file if it was found. If a matching filename is not
        found then `None` is returned.

    """
    output = None
    for dirpath,dirnames,filename_list in os.walk(rootpath):
        if filename in filename_list:
            output = os.path.join(dirpath, filename)
            break
    if output is None:
        raise FileNotFoundError("Unable to find {} in {}".format(filename, os.getcwd()))  # pragma: no cover
    return output




#===============================================================================
#
# Mock Helpers
#
#===============================================================================

def mock_module_noreturn(*args):
    """
    Mock the module() command that has no return value.
    """
    print("\nmock> module({}) ==> NoneType".format(args))


def mock_module_pass(*args):
    """
    Mock the module() command that 'passes', returning a 0.
    """
    print("\nmock> module({}) ==> 0".format(args))
    return 0


def mock_module_fail(*args):
    """
    Mock the module() command that 'fails', returning a 1.
    """
    print("\nmock> module({}) ==> 1".format(args))
    return 1



#===============================================================================
#
# Tests
#
#===============================================================================

class SetEnvironmentTest(TestCase):
    """
    Main test driver for the SetEnvironment class
    """
    def setUp(self):
        print("")
        self.maxDiff = None
        self._filename = find_config_ini(filename="config_test_configparserenhanced.ini")


    def test_ConfigparserEnhanced_test_001(self):
        """
        Stubbed in test that does nothing (yet)
        """
        print("I am a test!")











# EOF
