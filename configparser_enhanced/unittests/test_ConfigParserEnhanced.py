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

import configparser

from configparser_enhanced import ConfigParserEnhanced



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

def mock_function_noreturn(*args):
    """
    Mock a function that does not return a value (i.e., returns NoneType)
    """
    print("\nmock> f({}) ==> NoneType".format(args))


def  mock_function_pass(*args):
    """
    Mock a function that 'passes', i.e., returns a 0.
    """
    print("\nmock> f({}) ==> 0".format(args))
    return 0


def mock_function_fail(*args):
    """
    Mock a function that 'fails', i.e., returns a 1.
    """
    print("\nmock> f({}) ==> 1".format(args))
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


    def test_ConfigParserEnhanced_load_configdata(self):
        """
        Tests the basic loading of a configuration .ini file using the lazy-evaluated
        `config` function.
        """
        section = None

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.section = section

        self.assertIsInstance(parser, ConfigParserEnhanced)


    def test_ConfigParserEnhanced_property_config(self):
        """
        Test the ConfigParserEnhanced property `config`
        """
        section = None

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 5
        parser.section = section

        configdata = parser.config

        self.assertIsInstance(configdata, configparser.ConfigParser)

        assert configdata.has_section("SECTION-A")
        assert configdata.has_section("SECTION-B")
        assert configdata.has_section("SECTION C")

        assert configdata.has_section("SECTION-A+")
        assert configdata.has_section("SECTION-B+")
        assert configdata.has_section("SECTION C+")


    def test_ConfigParserEnhanced_property_section_missing(self):
        """
        Test accessing the `section` property of ConfigParserEnhanced.
        """
        section = None

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 5

        # Trying to access parser.section if no section has been set should
        # throw a ValueError
        with self.assertRaises(ValueError):
            parser.section


    def test_ConfigParserEnhanced_property_section_provided(self):
        """
        Test accessing the `section` property of ConfigParserEnhanced.
        """
        section = "SECTION-A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(filename=self._filename)
        parser.debug_level = 5
        parser.section = section

        self.assertEqual(parser.section, section)


    def test_ConfigParserEnhanced_property_section_setter(self):
        """
        Test the setter property for sections.
        """
        section = "SECTION-A"

        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))

        parser = ConfigParserEnhanced(filename=self._filename)
        parser.section = section
        parser.debug_level = 5

        self.assertEqual(parser.section, section)

        section = "SECTION C"
        print("new section: {}".format(section))
        parser.section = section
        self.assertEqual(parser.section, section)


    def test_ConfigParserEnhanced_property_section_setter_typeerror(self):
        """
        Test the setter property when it gets a non-string type in assignment.
        It should raise a TypeError.
        """
        section = 100

        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))

        parser = ConfigParserEnhanced(filename=self._filename)
        parser.debug_level = 5

        print("new section: {}".format(section))
        with self.assertRaises(TypeError):
            parser.section = section


    def test_ConfigParserEnhanced_operand_variations_test(self):
        """
        This test will verify that ConfigParserEnhanced can properly parse out the op1, op2
        entries from a variety of different configurations in the .ini file.

        Examples, the following `key` options should properly be evaluated:
        - `op1`             --> op1: "op1"   op2: None
        - `op1 op2`         --> op1: "op1"   op2: "op2"
        - `op1 'op2'`       --> op1: "op1"   op2: "op2"
        - `op1 'op 2'`      --> op1: "op1"   op2: "op 2"
        - `op1 op2 op3`     --> op1: "op1"   op2: "op2"
        - `op1 'op2' op3`   --> op1: "op1"   op2: "op2"
        - `op-1`            --> op1: "op_1"  op2: None
        - `op-1 op2`        --> op1: "op_1"  op2: "op2"
        - `op-1 op2 op3`    --> op1: "op_1"  op2: "op2"
        - `op-1 'op2'`      --> op1: "op_1"  op2: "op2"
        - `op-1 'op2' op3`  --> op1: "op_1"  op2: "op2"
        - `op-1 'op 2'`     --> op1: "op_1"  op2: "op 2"
        - `op-1 'op 2' op3` --> op1: "op_1"  op2: "op 2"
        - `op-1 op-2`       --> op1: "op_1"  op2: "op-2"
        - `op_1 op_2`       --> op1: "op_1"  op2: "op_2"
        """
        section = "OPERAND_TEST"

        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))

        parser = ConfigParserEnhanced(filename=self._filename)
        parser.section = section
        parser.debug_level = 5

        data = parser.parse_configuration()
        print(data)

        results_expected = [ ('op1', None),
                             ('op1', 'op2'),
                             ('op1', 'op2'),
                             ('op1', 'op 2'),
                             ('op1', 'op2'),
                             ('op1', 'op2'),
                             ('op_1', None),
                             ('op_1', 'op2'),
                             ('op_1', 'op2'),
                             ('op_1', 'op2'),
                             ('op_1', 'op2'),
                             ('op_1', 'op 2'),
                             ('op_1', 'op 2'),
                             ('op_1', 'op-2'),
                             ('op_1', 'op_2')
        ]
        print("results_expected:")
        pprint(results_expected)

        results_actual = [ (d['op1'],d['op2']) for d in parser._loginfo if d['type']=='section-operands']
        print("results_actual:")
        pprint(results_actual)

        self.assertListEqual(results_expected, results_actual)
        print("Test Complete.")








# EOF
