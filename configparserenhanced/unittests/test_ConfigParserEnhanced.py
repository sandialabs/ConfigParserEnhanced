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

from configparserenhanced import *
# from ..HandlerParameters import HandlerParameters

from .common import *



#===============================================================================
#
# General Utility Functions
#
#===============================================================================



#===============================================================================
#
# Mock Helpers
#
#===============================================================================



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


    def test_ConfigParserEnhanced_load_configparserdata(self):
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
        data = parser.parse_section(section)

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

        configparserdata = parser.configparserdata

        self.assertIsInstance(configparserdata, configparser.ConfigParser)

        assert configparserdata.has_section("SECTION-A")
        assert configparserdata.has_section("SECTION-B")
        assert configparserdata.has_section("SECTION C")

        assert configparserdata.has_section("SECTION-A+")
        assert configparserdata.has_section("SECTION-B+")
        assert configparserdata.has_section("SECTION C+")


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

        parser.parse_section(section)

        self.assertIsInstance(parser._loginfo, list)
        self.assertIsInstance(parser._configparserdata, configparser.ConfigParser)

        parser.inifilepath = "foobar"

        self.assertFalse( hasattr(parser, '_loginfo') )
        self.assertFalse( hasattr(parser, '_configparserdata') )

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
            configparserdata = parser.configparserdata

        print("OK")


    def test_ConfigParserEnhanced_property_inifilepath_invalid_entry(self):
        """
        Tests what happenes if `inifilepath = []` and we try to
        load configparserdata using configparser.ConfigParser.
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
        # check inside the `configparserdata` property we'll force
        # it here (whitebox testing FTW)
        parser._inifilepath = [ None ]
        with self.assertRaises(TypeError):
            configparserdata = parser.configparserdata

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
        - `op-1`            --> op1: "op-1"  op2: None
        - `op-1 op2`        --> op1: "op-1"  op2: "op2"
        - `op-1 op2 op3`    --> op1: "op-1"  op2: "op2"
        - `op-1 'op2'`      --> op1: "op-1"  op2: "op2"
        - `op-1 'op2' op3`  --> op1: "op-1"  op2: "op2"
        - `op-1 'op 2'`     --> op1: "op-1"  op2: "op 2"
        - `op-1 'op 2' op3` --> op1: "op-1"  op2: "op 2"
        - `op-1 op-2`       --> op1: "op-1"  op2: "op-2"
        - `op_1 op_2`       --> op1: "op-1"  op2: "op_2"
        """
        section = "OPERAND_TEST"

        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))

        parser = ConfigParserEnhanced(filename=self._filename)
        parser.debug_level = 5

        data = parser.parse_section(section)
        print(data)

        results_expected = [ ('op1', None),
                             ('op1', 'op2'),
                             ('op1', 'op2'),
                             ('op1', 'op 2'),
                             ('op1', 'op2'),
                             ('op1', 'op2'),
                             ('op-1', None),
                             ('op-1', 'op2'),
                             ('op-1', 'op2'),
                             ('op-1', 'op2'),
                             ('op-1', 'op2'),
                             ('op-1', 'op 2'),
                             ('op-1', 'op 2'),
                             ('op-1', 'op-2'),
                             ('op_1', 'op_2'),
                             ('op1',  'op2'),
                             ('op1',  'op2')
        ]
        print("results_expected ({}):".format(len(results_expected)))
        pprint(results_expected)

        results_actual = [ (d['op1'],d['op2']) for d in parser._loginfo if d['type']=='section-operands']
        print("results_actual ({}):".format(len(results_actual)))
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

        data = parser.parse_section(section)

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
            "handler_initialize",
            "_handler_use",
            "handler_generic",
            "handler_generic",
            "handler_generic",
            "handler_generic",
            "handler_finalize"
        ]
        handler_exit_list_expected = [
            "handler_initialize",
            "handler_generic",
            "handler_generic",
            "handler_generic",
            "_handler_use",
            "handler_generic",
            "handler_finalize"
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

        data = parser.parse_section(section)

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

        data = parser.parse_section(section)

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
            parser.configparserdata

        print("OK")


    def test_ConfigParserEnhanced_parse_section_launch(self):
        """
        Test the `section` parameter checks to `parse_section()`.
        """
        parser = ConfigParserEnhanced(filename=self._filename)
        parser.debug_level = 5

        # Trigger a TypeError if `section` is not a string type.
        section = None
        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))
        with self.assertRaises(TypeError):
            data = parser.parse_section(section)

        # Trigger a ValueError if `section` is an empty string.
        section = ""
        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))
        with self.assertRaises(ValueError):
            data = parser.parse_section(section)

        # Test that calling parse_section will reset _loginfo
        # (whitebox)
        section = "SECTION-A"
        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))
        parser._loginfo = [ 1, 2, 3 ]

        data = parser.parse_section(section)
        self.assertNotEqual(parser._loginfo, [1,2,3])

        print("OK")


    def test_ConfigParserEnhanced_parse_section_handler_fail_01(self):
        """
        Test that we trigger the failure check if a handler returns a
        nonzero value. This test requires us to derive a subclass of
        `ConfigParserEnhanced` and add a handler that will always fail
        its test.
        """
        class ConfigParserEnhancedTest(ConfigParserEnhanced):

            def _handler_test_handler_fail(self,
                                           section_name,
                                           handler_parameters,
                                           processed_sections=None) -> int:
                print("_handler_test_handler_fail()")
                print("---> Returns 1!")
                return 1

        parser = ConfigParserEnhancedTest(filename=self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 5

        # Test that calling parse_section will reset _loginfo
        # (whitebox)
        section = "HANDLER_FAIL_TEST"
        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))
        parser._loginfo = [ 1, 2, 3 ]

        with self.assertRaises(RuntimeError):
            data = parser.parse_section(section)

        print("OK")


    def test_ConfigParserEnhanced_parser_handlerparameter_typechecks(self):
        """
        Testing some of the type-checking on HandlerParameter typechecks.
        """
        class ConfigParserEnhancedTest(ConfigParserEnhanced):

            def handler_generic(self, section_name, handler_parameters) -> int:
                """
                Redefine handler_generic so that it changes HandlerParameters
                data_internal['processed_sections'] type to a non-set type.  This
                should trigger a TypeError.
                """
                handler_parameters.data_internal['processed_sections'] = {}
                return 0

        parser = ConfigParserEnhancedTest(filename=self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 5

        # Test that calling parse_section will reset _loginfo
        # (whitebox)
        section = "SECTION-A"
        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))

        with self.assertRaises(TypeError):
            parser.parse_section(section)

        print("OK")
        return


    def test_ConfigParserEnhanced_parser_handler_private(self):
        """
        Testing some of the type-checking on HandlerParameter typechecks.
        """
        class ConfigParserEnhancedTest(ConfigParserEnhanced):
            """
            Test class that defines a custom 'private' handler.
            """
            def _handler_operation(self, section_name, handler_parameters) -> int:
                return 0

        parser = ConfigParserEnhancedTest(filename=self._filename)
        parser.debug_level = 5
        # parser.exception_control_level = 5

        # Test that calling parse_section will reset _loginfo
        # (whitebox)
        section = "AMBIGUOUS_HANDLER_TEST"
        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))

        parser.parse_section(section)

        print("OK")
        return


    def test_ConfigParserEnhanced_parser_handler_public(self):
        """
        Testing some of the type-checking on HandlerParameter typechecks.
        """
        class ConfigParserEnhancedTest(ConfigParserEnhanced):
            """
            Test class that defines a custom 'public' handler.
            """
            def handler_operation(self, section_name, handler_parameters) -> int:
                return 0

        parser = ConfigParserEnhancedTest(filename=self._filename)
        parser.debug_level = 5
        # parser.exception_control_level = 5

        # Test that calling parse_section will reset _loginfo
        # (whitebox)
        section = "AMBIGUOUS_HANDLER_TEST"
        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))

        parser.parse_section(section)

        print("OK")
        return


    def test_ConfigParserEnhanced_parser_handler_ambiguous(self):
        """
        Testing some of the type-checking on HandlerParameter typechecks.
        """
        class ConfigParserEnhancedTest(ConfigParserEnhanced):
            """
            Test class that sets up an ambiguous handler naming scheme
            for an ``operation`` called "operation" (yeah, super creative).

            This should trigger an ``AmbiguousHandlerError`` exception.
            """
            def handler_operation(self, section_name, handler_parameters) -> int:
                return 0

            def _handler_operation(self, section_name, handler_parameters) -> int:
                return 0


        parser = ConfigParserEnhancedTest(filename=self._filename)
        parser.debug_level = 5
        # parser.exception_control_level = 5

        # Test that calling parse_section will reset _loginfo
        # (whitebox)
        section = "AMBIGUOUS_HANDLER_TEST"
        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))

        with self.assertRaises(AmbiguousHandlerError):
            parser.parse_section(section)

        print("OK")


    def test_ConfigParserEnhanced_parse_section_handler_fail_11(self):
        """
        Test that we trigger the failure check if a handler returns a
        nonzero value. This test requires us to derive a subclass of
        `ConfigParserEnhanced` and add a handler that will always fail
        its test.
        """
        class ConfigParserEnhancedTest(ConfigParserEnhanced):

            def _handler_test_handler_fail(self,
                                           section_name,
                                           handler_parameters,
                                           processed_sections=None) -> int:
                print("_handler_test_handler_fail()")
                print("---> This one goes to 11!")
                return 11

        parser = ConfigParserEnhancedTest(filename=self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 5

        # Test that calling parse_section will reset _loginfo
        # (whitebox)
        section = "HANDLER_FAIL_TEST"
        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))
        parser._loginfo = [ 1, 2, 3 ]

        with self.assertRaises(RuntimeError):
            data = parser.parse_section(section)

        print("OK")


    def test_ConfigParserEnhanced_parse_section_HandlerParameters_badtype(self):
        """
        Test that an overridden `new_handler_parameters()` method will
        trigger an error in the parser if it doesn't return a `HandlerParameters`
        type.
        """
        class ConfigParserEnhancedTest(ConfigParserEnhanced):

            def _new_handler_parameters(self):
                print("new_handler_parameters() --> {}")
                return {}

        parser = ConfigParserEnhancedTest(filename=self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 5

        section = "SECTION-A"
        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))

        # This should raise a TypeError because the overridden `new_handler_parameters`
        # method is generating a dict type, but the parser will only work properly
        # if this method generates a HandlerParameters (or a subclass of HandlerParameters)
        # object.
        with self.assertRaises(TypeError):
            data = parser.parse_section(section)

        print("OK")


    def test_ConfigParserEnhanced_assert_parsesection_r_section_None(self):
        """
        Tests that a TypeError will be thrown if the `section` paramter is set to
        `None` when calling ``_parse_section_r``.

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
            parser._parse_section_r(None)

        print("OK")


    def test_ConfigParserEnhanced_assert_parsesection_r_section_missing(self):
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
            parser._parse_section_r('blah blah blah')

        print("OK")


    def test_ConfigParserEnhanced_assert_parsesection_r_op_bad_char(self):
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
        parser.parse_section(section)

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
        #data = parser.parse_section(section)

        # entry must be a dict type. Throw TypeError if it isn't.
        with self.assertRaises(TypeError):
            parser._loginfo_add("test-type", entry=None)

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
        data = parser.parse_section(section)

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
        data = parser.parse_section(section)

        inst = ConfigParserEnhanced.ConfigParserEnhancedData(parser)

        # Trigger the 'None' default option for owner (when it doesn't exist)
        delattr(inst, '_owner_data')
        new_owner = inst._owner

        # Test setting owner to something other than a ConfigParserEnhanced
        with self.assertRaises(TypeError):
            inst._owner = None

        # Test setter for the data property.
        # - This isn't really used in our current code, but it's good to have a setter.
        # Should be ok, we want to assign a dict.
        inst.data = {}

        # Throws if the type isn't a dict.
        with self.assertRaises(TypeError):
            inst.data = None

        print("OK")


    def test_ConfigParserEnhanced_property_configparserdata_parsed(self):
        """
        Test the accessors and lazy evaluation of the configparserenhanceddata
        property
        """
        section = "SECTION-A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 1
        parser.exception_control_level = 1

        for k,v in parser.configparserenhanceddata.items():
            print(k,v)

        # iterate over items from a given section
        for k,v in parser.configparserenhanceddata.items(section):
            print(k,v)

        # Get the keys
        self.assertIn("SECTION-A", parser.configparserenhanceddata.keys(),
                      "Check `SECTION-A` membership in 'configparserenhanceddata.keys()")

        # Test iterator (__item__)
        print("\nTest Iterator")
        for i in parser.configparserenhanceddata:
            print("   ", i)

        # Test __getitem__
        print("\nTest __getitem__")
        sec_b = parser.configparserenhanceddata["SECTION-B"]
        print("   ", sec_b)

        with self.assertRaises(KeyError):
            parser.configparserenhanceddata["NonExistentSection"]

        # Test sections
        print("\nTest Sections")
        for i in parser.configparserenhanceddata.sections():
            print("   ", i)

        # Test length - This should be the # of sections in the .ini file.
        print("\nTest __len__")
        exp_len = 16
        act_len = len(parser.configparserenhanceddata)
        self.assertEqual(exp_len, act_len,
                         "ERROR: Length returned is {} but we expected {}".format(act_len, exp_len))

        # Test options()
        print("\nTest options()")
        data = parser.configparserenhanceddata.options("SECTION-A")
        self.assertIsInstance(data, dict, "options() must return a dict")

        subset = {'key1': 'value1'}
        self.assertEqual(dict(data, **subset), data)
        # self.assertDictContainsSubset is deprecated and will go away, so
        # 'right' syntax for this now is to use dict(data, **subset)
        # to pull the subset out of the dict and check it. :/

        subset = {'key2': 'value2'}
        self.assertEqual(dict(data, **subset), data)

        subset = {'key3': 'value3'}
        self.assertEqual(dict(data, **subset), data)

        with self.assertRaises(KeyError):
            data = parser.configparserenhanceddata.options("NonExistentSection")


    def test_ConfigParserEnhanced_property_configparserenhanceddata_has_option(self):
        """
        Test the accessors and lazy evaluation of the configparserenhanceddata
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
        self.assertTrue( parser.configparserenhanceddata.has_option("SECTION-A", "key1") )
        self.assertFalse( parser.configparserenhanceddata.has_option("SECTION-A", "Nonexistent Key") )

        print("OK")


    def test_ConfigParserEnhanced_property_configparserenhanceddata_get(self):
        """
        Test the `get` method for the configparserenhanceddata property.
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
        self.assertEqual(parser.configparserenhanceddata.get("SECTION-A", "key1"), "value1")

        # test get(section, option) with missing option
        print("\nTest get(section,option) - Section OK, Option Missing")
        with self.assertRaises(KeyError):
            parser.configparserenhanceddata.get("SECTION-A", "nonexistentkey")

        # test get(section, option) with missing section
        print("\nTest get(section,option) - Section Missing")
        with self.assertRaises(KeyError):
            parser.configparserenhanceddata.get("Nonexistent Section", "key1")

        # Doing something evil
        parser.configparserenhanceddata._owner_data = None
        with self.assertRaises(KeyError):
            parser.configparserenhanceddata.get("Nonexistent Section", "key1")

        print("OK")


    def test_ConfigParserEnhanced_property_configparserenhanceddata_deptest(self):
        """
        """
        print("\n")
        print("---[ test_ConfigParserEnhanced_property_configparserenhanceddata_deptest")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.exception_control_level = 1
        parser.debug_level = 1

        print("")
        print("\n-[ DEP-TEST-A ]------------")
        parser.configparserenhanceddata.items("DEP-TEST-A")
        print("\n[DEP-TEST-A]")
        for k,v in parser.configparserenhanceddata.items("DEP-TEST-A"):
            print(k,v)

        print("\n-[ loginfo ]---------------")
        pprint(parser._loginfo)

        self.assertEqual("value1-A", parser.configparserenhanceddata.get('DEP-TEST-A', 'key1'))
        self.assertEqual("value2-A", parser.configparserenhanceddata.get('DEP-TEST-A', 'key2'))

        print("")
        print("\n-[ DEP-TEST-B ]------------")
        parser.configparserenhanceddata.items("DEP-TEST-B")
        print("\n[DEP-TEST-B]")
        for k,v in parser.configparserenhanceddata.items("DEP-TEST-B"):
            print(k,v)

        print("\n-[ loginfo ]---------------")
        parser._loginfo_print()

        print("\n-[ Validate ]--------------")
        self.assertEqual("value1-A", parser.configparserenhanceddata.get('DEP-TEST-A', 'key1'))
        self.assertEqual("value2-A", parser.configparserenhanceddata.get('DEP-TEST-A', 'key2'))

        self.assertEqual("value1-B", parser.configparserenhanceddata.get('DEP-TEST-B', 'key1'))
        self.assertEqual("value2-A", parser.configparserenhanceddata.get('DEP-TEST-B', 'key2'))

        print("OK")


# EOF
