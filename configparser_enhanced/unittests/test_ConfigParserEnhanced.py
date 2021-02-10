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

class ConfigParserEnhancedTest(TestCase):
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

        self.assertIsInstance(parser, ConfigParserEnhanced)


    def test_ConfigParserEnhanced_basic(self):
        """
        Just a baic run of the ConfigParserEnhanced
        This is useful to build other tests from.
        """
        section = "SECTION-A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 0
        parser.exception_control_level = 0
        data = parser.parse_configuration(section)

        print("OK")


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

        parser.parse_configuration(section)

        self.assertIsInstance(parser._loginfo, list)
        self.assertIsInstance(parser._configdata, configparser.ConfigParser)

        parser.inifilepath = "foobar"

        self.assertFalse( hasattr(parser, '_loginfo') )
        self.assertFalse( hasattr(parser, '_configdata') )

        print("OK")


    def test_ConfigParserEnhanced_property_inifilepath_empty(self):
        """
        Tests what happenes if `inifilepath = []` and we try to
        load configdata using configparser.ConfigParser.
        """
        section = "SECTION-A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 1

        parser.inifilepath = []

        with self.assertRaises(ValueError):
            configdata = parser.configdata

        print("OK")


    def test_ConfigParserEnhanced_property_inifilepath_invalid_entry(self):
        """
        Tests what happenes if `inifilepath = []` and we try to
        load configdata using configparser.ConfigParser.
        """
        section = "SECTION-A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 1

        with self.assertRaises(TypeError):
            parser.inifilepath = [ None ]

        # Setter will fail if we tried this but to test a
        # check inside the `configdata` property we'll force
        # it here (whitebox testing FTW)
        parser._inifilepath = [ None ]
        with self.assertRaises(TypeError):
            configdata = parser.configdata

        print("OK")


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
        parser.debug_level = 5

        data = parser.parse_configuration(section)
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
        parser.debug_level = 5

        data = parser.parse_configuration(section)

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

        handler_entry_list_expected = [
            "_handler_use",
            "_handler_generic",
            "_handler_generic",
            "_handler_generic",
            "_handler_generic"
        ]
        handler_exit_list_expected = [
            "_handler_generic",
            "_handler_generic",
            "_handler_generic",
            "_handler_use",
            "_handler_generic"
        ]

        self.assertListEqual(handler_entry_list, handler_entry_list_expected)
        self.assertListEqual(handler_exit_list,  handler_exit_list_expected)

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
        parser.debug_level = 5

        data = parser.parse_configuration(section)

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

        data = parser.parse_configuration(section)

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

        with self.assertRaises(IOError):
            parser.configdata

        print("OK")


    def test_ConfigParserEnhanced_parse_configuration_launch(self):
        """
        Test the `section` parameter checks to `parse_configuration()`.
        """
        parser = ConfigParserEnhanced(filename=self._filename)
        parser.debug_level = 5

        # Trigger a TypeError if `section` is not a string type.
        section = None
        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))
        with self.assertRaises(TypeError):
            data = parser.parse_configuration(section)

        # Trigger a ValueError if `section` is an empty string.
        section = ""
        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))
        with self.assertRaises(ValueError):
            data = parser.parse_configuration(section)

        # Test that calling parse_configuration will reset _loginfo
        # (whitebox)
        section = "SECTION-A"
        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))
        parser._loginfo = [ 1, 2, 3 ]

        data = parser.parse_configuration(section)
        self.assertNotEqual(parser._loginfo, [1,2,3])

        print("OK")


    def test_ConfigParserEnhanced_parse_configuration_handler_fail(self):
        """
        Test that we trigger the failure check if a handler returns a
        nonzero value. This test requires us to derive a subclass of
        `ConfigParserEnhanced` and add a handler that will always fail
        its test.
        """
        class ConfigParserEnhancedTest(ConfigParserEnhanced):

            def _handler_test_handler_fail(self,
                                           section_root,
                                           section_name,
                                           op1, op2,
                                           data,
                                           processed_sections=None,
                                           entry=None) -> int:
                print("_handler_test_handler_fail()")
                return 1

        parser = ConfigParserEnhancedTest(filename=self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 5

        # Test that calling parse_configuration will reset _loginfo
        # (whitebox)
        section = "HANDLER_FAIL_TEST"
        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))
        parser._loginfo = [ 1, 2, 3 ]

        with self.assertRaises(RuntimeError):
            data = parser.parse_configuration(section)

        print("OK")


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
        parser.parse_configuration(section)

        print("OK")


    def test_ConfigParserEnhanced_helper_loginfo_add_badtype(self):
        """
        Test that `_loginfo_add` will fail if we try to give it bad
        data.
        """
        section = "SECTION-A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 1
        parser.exception_control_level = 0
        #data = parser.parse_configuration(section)

        # entry must be a dict type. Throw TypeError if it isn't.
        with self.assertRaises(TypeError):
            parser._loginfo_add(entry=None)

        # entry must have a 'type' key, otherwise throw a ValueError.
        with self.assertRaises(ValueError):
            parser._loginfo_add(entry={})

        print("OK")


    def test_ConfigParserEnhanced_helper_loginfo_print(self):
        """
        Test that `_loginfo_add` will fail if we try to give it bad
        data.
        """
        section = "SECTION-A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 1
        parser.exception_control_level = 0
        data = parser.parse_configuration(section)

        parser._loginfo_print()

        parser._loginfo_print(pretty=False)

        print("OK")


    def test_ConfigParserEnhanced_inner(self):
        """
        """
        section = "SECTION-A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 0
        parser.exception_control_level = 0
        data = parser.parse_configuration(section)

        inst = ConfigParserEnhanced.ConfigParserEnhancedDataSection(parser)

        # Trigger the 'None' default option for owner (when it doesn't exist)
        delattr(inst, '_owner')
        new_owner = inst.owner

        # Test setting owner to something other than a ConfigParserEnhanced
        with self.assertRaises(TypeError):
            inst.owner = None

        # Test setter for the data property.
        # - This isn't really used in our current code, but it's good to have a setter.
        # Should be ok, we want to assign a dict.
        inst.data = {}

        # Throws if the type isn't a dict.
        with self.assertRaises(TypeError):
            inst.data = None

        print("OK")


    def test_ConfigParserEnhanced_property_configdata_parsed(self):
        """
        Test the accessors and lazy evaluation of the configdata_parsed
        property
        """
        section = "SECTION-A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 1
        parser.exception_control_level = 1

        for k,v in parser.configdata_parsed.items():
            print(k,v)

        # iterate over items from a given section
        for k,v in parser.configdata_parsed.items(section):
            print(k,v)

        # Get the keys
        self.assertIn("SECTION-A", parser.configdata_parsed.keys(),
                      "Check `SECTION-A` membership in 'configdata_parsed.keys()")

        # Test iterator (__item__)
        print("\nTest Iterator")
        for i in parser.configdata_parsed:
            print("   ", i)


        # Test __getitem__
        print("\nTest __getitem__")
        sec_b = parser.configdata_parsed["SECTION-B"]
        print("   ", sec_b)

        with self.assertRaises(KeyError):
            parser.configdata_parsed["NonExistentSection"]

        # Test sections
        print("\nTest Sections")
        for i in parser.configdata_parsed.sections():
            print("   ", i)

        # Test length
        print("\nTest __len__")
        self.assertEqual(12, len(parser.configdata_parsed))

        # Test options()
        print("\nTest options()")
        data = parser.configdata_parsed.options("SECTION-A")
        self.assertIsInstance(data, dict, "options() must return a dict")

        subset = {'key1': 'value1'}
        self.assertEqual(dict(data, **subset), data)

        subset = {'key2': 'value2'}
        self.assertEqual(dict(data, **subset), data)

        subset = {'key3': 'value3'}
        self.assertEqual(dict(data, **subset), data)

        with self.assertRaises(KeyError):
            data = parser.configdata_parsed.options("NonExistentSection")


    def test_ConfigParserEnhanced_property_configdata_parsed_has_option(self):
        """
        Test the accessors and lazy evaluation of the configdata_parsed
        property. The has_option needs an unparsed config structure to
        fully be checked.
        """
        section = "SECTION-A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 1
        parser.exception_control_level = 1


        # test has_option()
        print("\nTest has_option(section,option)")
        self.assertTrue( parser.configdata_parsed.has_option("SECTION-A", "key1") )
        self.assertFalse( parser.configdata_parsed.has_option("SECTION-A", "Nonexistent Key") )

        print("OK")


    def test_ConfigParserEnhanced_property_configdata_parsed_get(self):
        """
        Test the `get` method for the configdata_parsed property.
        """
        section = "SECTION-A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 1
        parser.exception_control_level = 1

        # test get(section, option)
        print("\nTest get(section,option) - Valid Entry")
        self.assertEqual(parser.configdata_parsed.get("SECTION-A", "key1"), "value1")

        # test get(section, option) with missing option
        print("\nTest get(section,option) - Section OK, Option Missing")
        with self.assertRaises(KeyError):
            parser.configdata_parsed.get("SECTION-A", "nonexistentkey")

        # test get(section, option) with missing section
        print("\nTest get(section,option) - Section Missing")
        with self.assertRaises(KeyError):
            parser.configdata_parsed.get("Nonexistent Section", "key1")

        # Doing something evil
        parser.configdata_parsed._owner = None
        with self.assertRaises(KeyError):
            parser.configdata_parsed.get("Nonexistent Section", "key1")

        print("OK")


# EOF
