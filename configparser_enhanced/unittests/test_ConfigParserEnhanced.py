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
try:                                                                            # pragma: no cover
    import unittest.mock as mock                                                # pragma: no cover
except:                                                                         # pragma: no cover
    import mock                                                                 # pragma: no cover

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
    print("\nmock> f({}) ==> NoneType".format(args))                            # pragma: no cover


def  mock_function_pass(*args):
    """
    Mock a function that 'passes', i.e., returns a 0.
    """
    print("\nmock> f({}) ==> 0".format(args))                                   # pragma: no cover
    return 0                                                                    # pragma: no cover


def mock_function_fail(*args):
    """
    Mock a function that 'fails', i.e., returns a 1.
    """
    print("\nmock> f({}) ==> 1".format(args))                                   # pragma: no cover
    return 1                                                                    # pragma: no cover



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

        configdata = parser.configdata

        self.assertIsInstance(configdata, configparser.ConfigParser)

        assert configdata.has_section("SECTION-A")
        assert configdata.has_section("SECTION-B")
        assert configdata.has_section("SECTION C")

        assert configdata.has_section("SECTION-A+")
        assert configdata.has_section("SECTION-B+")
        assert configdata.has_section("SECTION C+")


    def test_ConfigParserEnhanced_property_inifilepath_changed(self):
        """
        Tests that changing the inifile will properly reset the data structure.
        """
        section = "SECTION-A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 1
        parser.section = section

        parser.parse_configuration()

        self.assertIsInstance(parser._loginfo, list)
        self.assertIsInstance(parser._configdata, configparser.ConfigParser)

        parser.inifilepath = "foobar"

        self.assertFalse( hasattr(parser, '_loginfo') )
        self.assertFalse( hasattr(parser, '_configdata') )

        print("OK")


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


    def test_ConfigParserEnhanced_property_section_changed(self):
        """
        Test cleanup operations when we change the section name
        """
        section = "SECTION-A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 1
        parser.section = section

        parser.parse_configuration()

        self.assertIsInstance(parser._loginfo, list)
        self.assertIsInstance(parser._configdata, configparser.ConfigParser)

        parser.section = "SECTION-B"

        self.assertFalse( hasattr(parser, '_loginfo') )
        self.assertTrue( hasattr(parser, '_configdata') )

        print("OK")


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

        # check that the setter returns None if we try and assign it None
        val = parser.section = None
        self.assertIsNone(val)

        # Check what happens if some jokester force-changes the _section data entry
        # to a nonstring without going through the property interface.
        parser._section = 1234
        with self.assertRaises(TypeError):
            parser.section


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


    def test_ConfigParserEnhanced_keyword_use(self):
        """
        Test the handler and parser for `use` commands to make sure we recurse properly.
        """
        section = "SECTION C+"

        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))

        parser = ConfigParserEnhanced(filename=self._filename)
        parser.section = section
        parser.debug_level = 5

        self.assertEqual(parser.section, section)

        data = parser.parse_configuration()

        parser._loginfo_print(pretty=True)

        # Extract the list of sections entered by the parser (in the order they were accessed)
        # and check that the list of sections entered is the reverse of exited sections
        section_entry_list = [ d['name'] for d in parser._loginfo if d['type']=='section-entry']
        section_exit_list  = [ d['name'] for d in parser._loginfo if d['type']=='section-exit']
        self.assertListEqual(section_entry_list, section_exit_list[::-1])

        # Same for handlers - This requires that we log both entry and exit events for a handler.
        # - if this trick fails to work in the future, we can always use self.assertListEqual()
        #   to check the log data against some ground-truth.
        handler_entry_list = [ d['name'] for d in parser._loginfo if d['type']=='handler-entry']
        handler_exit_list  = [ d['name'] for d in parser._loginfo if d['type']=='handler-exit']
        self.assertListEqual(handler_entry_list, handler_exit_list[::-1])

        print("OK")


    def test_ConfigParserEnhanced_keyword_use_cycle_exists(self):
        """
        Test the handler and parser for `use` commands to make sure we recurse properly.

        The test layout in the config.ini test file is this:

        CYCLE_TEST_A
          |--> CYCLE_TEST_B
          |      |--> CYCLE_TEST_C
          |             |--> CYCLE_TEST_A (NOT ALLOWED DUE TO CYCLE)
          |--> CYCLE_TEST_B
          |      |--> CYCLE_TEST_C
          |             |--> CYCLE_TEST_A (NOT ALLOWED DUE TO CYCLE)

        Todo:
            There is some discussion needed on whether or not we should just issue a warning
            when breaking a cycle or if we should throw some error(s).
        """
        section = "CYCLE_TEST_A"

        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))

        parser = ConfigParserEnhanced(filename=self._filename)
        parser.section = section
        parser.debug_level = 5

        self.assertEqual(parser.section, section)

        data = parser.parse_configuration()

        parser._loginfo_print(pretty=True)

        # Check that we only entered the right sections and that we didn't recurse through the
        # cycle.
        section_entry_list_actual = [ d['name'] for d in parser._loginfo if d['type']=='section-entry']

        # What did we expect to get?
        section_entry_list_expected = ['CYCLE_TEST_A',
                                       'CYCLE_TEST_B', 'CYCLE_TEST_C',
                                       'CYCLE_TEST_B', 'CYCLE_TEST_C']

        print("section_entry_list_expected: {}".format(section_entry_list_expected))
        print("section_entry_list_actual  : {}".format(section_entry_list_actual))

        self.assertListEqual(section_entry_list_actual, section_entry_list_expected)

        print("OK")


    def test_ConfigParserEnhanced_debug_default(self):
        """
        Tests the basic ConfigParserEnhanced class if we don't specify a debug level.

        This basic test passes if we just don't throw an error.
        """
        section = "SECTION-A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.section = section

        data = parser.parse_configuration()

        print("OK")


    def test_ConfigParserEnhanced_assert_inifilepath_missing(self):
        """
        Tests a throw if we somehow are missing the `inifilepath` property.

        This normally shouldn't be possible in the base class because this is a required
        parameter to the c'tor but a derived class might not implement a proper c'tor so
        let's make sure that we throw our `ValueError` if we try to access the property
        if it hasn't been set.
        """
        section = "SECTION-A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.section = section

        # remove the _filename entry from the parser instance.
        delattr(parser, '_inifilepath')

        with self.assertRaises(ValueError):
            inifilepath = parser.inifilepath

        print("OK")


    def test_ConfigParserEnhanced_assert_inifilepath_not_str(self):
        """
        Tests that we properly raise the exception if we try and set the `inifilepath`
        property to something that is not a string.
        """
        section = "SECTION-A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.section = section

        # remove the _filename entry from the parser instance.
        delattr(parser, '_inifilepath')

        with self.assertRaises(TypeError):
            parser.inifilepath = 12345

        print("OK")


    def test_ConfigParserEnhanced_assert_inifilepath_filenotfound(self):
        """
        Tests that changing the inifile will properly reset the data structure.
        """
        section  = "SECTION-A"
        filename = "./filenotfound.ini"

        print("\n")
        print("Load file: {}".format(filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(filename)
        parser.debug_level = 1
        parser.section = section

        with self.assertRaises(IOError):
            parser.configdata

        print("OK")


    def test_ConfigParserEnhanced_assert_section_empty(self):
        """
        Tests a throw if we give an empty string as the section name.

        This should throw during the call to the `section` property setter.
        """
        section = ""

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)

        with self.assertRaises(ValueError):
            parser.section = section

        print("OK")


    def test_ConfigParserEnhanced_assert_section_setter_typeerror(self):
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


    def test_ConfigParserEnhanced_assert_parseconfiguration_r_section_None(self):
        """
        Tests that a TypeError will be thrown if the `section` paramter is set to
        `None` when calling `_parse_configuration_r`.

        This is unlikely to happen from the top-level call -- it's more likely to happen
        if we mess up something in the recursion (i.e., a handler tries to invoke recursion
        with bad args).
        """
        section = "SECTION-A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 1

        with self.assertRaises(TypeError):
            parser._parse_configuration_r(None)

        print("OK")


    def test_ConfigParserEnhanced_assert_parseconfiguration_r_section_missing(self):
        """
        Test a `KeyError` that should get thrown if the recursive parser
        is given a section name that does not exist.
        """
        section = "SECTION-A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 1

        with self.assertRaises(KeyError):
            parser._parse_configuration_r('blah blah blah')

        print("OK")


    def test_ConfigParserEnhanced_assert_parseconfiguration_r_op_bad_char(self):
        """
        This is a test to get a coverage line forced. The parser will skip over
        lines that don't properly parse.

        This should just cause the parser to skip to the next entry since this entry
        doesn't look like one of our ops.
        """
        section = "BAD_CHAR_IN_OP"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 1
        parser.section = section
        parser.parse_configuration()

        print("OK")




# EOF
