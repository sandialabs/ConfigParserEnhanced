#!/usr/bin/env python
# -*- coding: utf-8; mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
#===============================================================================
# Copyright Notice
# ----------------
# Copyright 2021 National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS,
# the U.S. Government retains certain rights in this software.
#
# License (3-Clause BSD)
# ----------------------
# Copyright 2021 National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS,
# the U.S. Government retains certain rights in this software.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#===============================================================================
"""
"""
from __future__ import print_function
import sys


sys.dont_write_bytecode = True

import os


sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pprint import pprint
import textwrap              # for dedent

import unittest
from unittest import TestCase

# Coverage will always miss one of these depending on the system
# and what is available.
try:                             # pragma: no cover
    import unittest.mock as mock # pragma: no cover
except:                          # pragma: no cover
    import mock                  # pragma: no cover

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
    Main test driver for the ConfigParserEnhanced class
    """

    def setUp(self):
        print("")
        self.maxDiff = None
        self._filename = find_config_ini(filename="config_test_configparserenhanced.ini")
        return 0

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
        return 0

    def test_ConfigParserEnhanced_Template(self):
        """
        Basic test template
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        print("----[ TEST BEGIN ]----------------------------------")

        section = "SECTION-A"
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 5

        data = parser.parse_section(section)

        print("----[ TEST END   ]----------------------------------")

        print("OK")
        return 0

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

    def test_ConfigParserEnhanced_property_inifilepath(self):
        """
        Test that everything works if we don't give a filename
        argument to the c'tor but instead use the inifilepath.
        """
        section = "SECTION-A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced()
        parser.inifilepath = self._filename
        parser.debug_level = 1

        parser.parse_section(section)

        self.assertIsInstance(parser._loginfo, list)
        self.assertIsInstance(parser._configparserdata, configparser.ConfigParser)

        print("OK")

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

        self.assertFalse(hasattr(parser, '_loginfo'))
        self.assertFalse(hasattr(parser, '_configparserdata'))

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
            parser.inifilepath = [None]

        # Setter will fail if we tried this but to test a
        # check inside the `configparserdata` property we'll force
        # it here (whitebox testing FTW)
        parser._inifilepath = [None]
        with self.assertRaises(TypeError):
            configparserdata = parser.configparserdata

        print("OK")

    def test_ConfigParserEnhanced_operand_variations_test(self):
        """
        This test will verify that ConfigParserEnhanced can properly parse out the op1, op2
        entries from a variety of different configurations in the .ini file.

        Examples, the following `key` options should properly be evaluated:
        - `op1`             -->
        - `op1 op2`         -->
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
        - `opA`             --> op1: "opA"   op2: None
        - `op-A`            --> op1: "op-A"  op2: None
        """
        section = "OPERAND_TEST"

        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))

        parser = ConfigParserEnhanced(filename=self._filename)
        parser.debug_level = 5

        data = parser.parse_section(section)
        print(data)

        results_expected = [
            ('op1', []),
            ('op1', ['op2']),
            ('op1', ['op2']),
            ('op1', ['op 2']),
            ('op1', ['op2', 'op3']),
            ('op1', ['op2', 'op3']),
            ('op_1', []),
            ('op_1', ['op2']),
            ('op_1', ['op2', 'op3']),
            ('op_1', ['op2']),
            ('op_1', ['op2', 'op3']),
            ('op_1', ['op 2']),
            ('op_1', ['op 2', 'op3']),
            ('op_1', ['op-2']),
            ('op_1', ['op_2']),
            ('op1', ['op2']),
            ('op1', ['op2', '+++']),
            ('opA', []),
            ('op_A', []),
        ]
        print("results_expected ({}):".format(len(results_expected)))
        pprint(results_expected)

        results_actual = [(d['op'], d['params']) for d in parser._loginfo if d['type'] == 'section-operation']
        print("results_actual ({}):".format(len(results_actual)))
        pprint(results_actual)

        self.assertListEqual(results_expected, results_actual)

        print("OK")
        return 0

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

        options_actual = parser.configparserenhanceddata.get(section)
        options_expect = {'key 1': 'value 1', 'key 2': 'value 2', 'key 3': 'value 3', 'key 4': 'value 4'}
        self.assertDictEqual(options_expect, options_actual)

        # Extract the list of sections entered by the parser (in the order they were accessed)
        # and check that the list of sections entered is the reverse of exited sections
        section_entry_list = [d['name'] for d in parser._loginfo if d['type'] == 'section-entry']
        section_exit_list = [d['name'] for d in parser._loginfo if d['type'] == 'section-exit']

        self.assertListEqual(section_entry_list, section_exit_list[::-1])

        # Same for handlers - This requires that we log both entry and exit events for a handler.
        # - if this trick fails to work in the future, we can always use self.assertListEqual()
        #   to check the log data against some ground-truth.
        handler_entry_list = [d['name'] for d in parser._loginfo if d['type'] == 'handler-entry']
        handler_exit_list = [d['name'] for d in parser._loginfo if d['type'] == 'handler-exit']

        handler_entry_list_expected = [
            "handler_initialize",
            "_handler_use",
            "_generic_option_handler",
            "_generic_option_handler",
            "_generic_option_handler",
            "_generic_option_handler",
            "handler_finalize"
        ]
        handler_exit_list_expected = [
            "handler_initialize",
            "_generic_option_handler",
            "_generic_option_handler",
            "_generic_option_handler",
            "_handler_use",
            "_generic_option_handler",
            "handler_finalize"
        ]

        self.assertListEqual(handler_entry_list_expected, handler_entry_list)
        self.assertListEqual(handler_exit_list_expected, handler_exit_list)

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
        section_entry_list_actual = [d['name'] for d in parser._loginfo if d['type'] == 'section-entry']

        # What did we expect to get?
        section_entry_list_expect = [
            'CYCLE_TEST_A', 'CYCLE_TEST_B', 'CYCLE_TEST_C', 'CYCLE_TEST_B', 'CYCLE_TEST_C'
        ]

        print("section_entry_list_expect: {}".format(section_entry_list_expect))
        print("section_entry_list_actual: {}".format(section_entry_list_actual))

        self.assertListEqual(section_entry_list_expect, section_entry_list_actual)

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
        section = "SECTION-A"
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
        parser._loginfo = [1, 2, 3]

        data = parser.parse_section(section)
        self.assertNotEqual(parser._loginfo, [1, 2, 3])

        print("OK")

    def test_ConfigParserEnhanced_parse_section_handler_fail_01(self):
        """
        Test that we trigger the failure check if a handler returns a
        nonzero value. This test requires us to derive a subclass of
        `ConfigParserEnhanced` and add a handler that will always fail
        its test.
        """

        class ConfigParserEnhancedTest(ConfigParserEnhanced):

            @ConfigParserEnhanced.operation_handler
            def _handler_test_handler_fail(
                self, section_name, handler_parameters, processed_sections=None
            ) -> int:
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
        parser._loginfo = [1, 2, 3]

        with self.assertRaises(RuntimeError):
            data = parser.parse_section(section)

        print("OK")

    def test_ConfigParserEnhanced_parser_handlerparameter_typechecks(self):
        """
        Testing some of the type-checking on HandlerParameter typechecks.
        """

        class ConfigParserEnhancedTest(ConfigParserEnhanced):

            def _generic_option_handler(self, section_name, handler_parameters) -> int:
                """
                Redefine _generic_option_handler so that it changes HandlerParameters
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

            @ConfigParserEnhanced.operation_handler
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

            @ConfigParserEnhanced.operation_handler
            def handler_operation(self, section_name, handler_parameters) -> int:
                return 0

            @ConfigParserEnhanced.operation_handler
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
        return

    def test_ConfigParserEnhanced_parser_handler_rval_reserved_warning(self):
        """
        Test a WARNING event if a handler returns a reserved value (1..10)
        """

        class ConfigParserEnhancedTest(ConfigParserEnhanced):
            """
            Test class that sets up an ambiguous handler naming scheme
            for an ``operation`` called "operation" (yeah, super creative).

            This should trigger an ``AmbiguousHandlerError`` exception.
            """

            @ConfigParserEnhanced.operation_handler
            def handler_test_handler_fail(self, section_name, handler_parameters) -> int:
                return 5

        print("Load file  : {}".format(self._filename))

        parser = ConfigParserEnhancedTest(filename=self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 4

        section = "HANDLER_FAIL_TEST"
        print("\n")
        print("section    : {}".format(section))

        with patch('sys.stdout', new=StringIO()) as fake_out:
            parser.parse_section(section)
            stdout = fake_out.getvalue()
            self.assertIn("EXCEPTION SKIPPED", stdout)
            self.assertIn("Handler `handler_test_handler_fail` returned 5", stdout)

        print("OK")
        return

    def test_ConfigParserEnhanced_parse_section_handler_fail_5(self):
        """
        Test a WARNING event if a handler returns a reserved value (1..10)
        that will raise an exception because ``exception_control_level`` is set
        to 5.
        """

        class ConfigParserEnhancedTest(ConfigParserEnhanced):
            """
            Test class that sets up an ambiguous handler naming scheme
            for an ``operation`` called "operation" (yeah, super creative).

            This should trigger an ``AmbiguousHandlerError`` exception.
            """

            @ConfigParserEnhanced.operation_handler
            def handler_test_handler_fail(self, section_name, handler_parameters) -> int:
                return 5

        print("Load file  : {}".format(self._filename))

        parser = ConfigParserEnhancedTest(filename=self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 5

        section = "HANDLER_FAIL_TEST"
        print("\n")
        print("section    : {}".format(section))

        with self.assertRaises(RuntimeError):
            parser.parse_section(section)

        print("OK")
        return

    def test_ConfigParserEnhanced_parse_section_handler_fail_11(self):
        """
        Test that we trigger the failure check if a handler returns a
        nonzero value. This test requires us to derive a subclass of
        `ConfigParserEnhanced` and add a handler that will always fail
        its test.
        """

        class ConfigParserEnhancedTest(ConfigParserEnhanced):

            @ConfigParserEnhanced.operation_handler
            def _handler_test_handler_fail(
                self, section_name, handler_parameters, processed_sections=None
            ) -> int:
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
        parser._loginfo = [1, 2, 3]

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
        return

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
        return

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

        for k, v in parser.configparserenhanceddata.items():
            print(k, v)

        # iterate over items from a given section
        for k, v in parser.configparserenhanceddata.items(section):
            print(k, v)

        # Get the keys
        self.assertIn(
            "SECTION-A",
            parser.configparserenhanceddata.keys(),
            "Check `SECTION-A` membership in 'configparserenhanceddata.keys()"
        )

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

        num_sections_expected = len(parser.configparserdata.sections())
        num_sections_actual = len(parser.configparserenhanceddata)
        print("- num sections expected: {}".format(num_sections_expected))
        print("- num sections actual  : {}".format(num_sections_actual))
        self.assertEqual(
            num_sections_expected,
            num_sections_actual,
            "ERROR: Length returned is {} but we expected {}".format(
                num_sections_actual, num_sections_expected
            )
        )

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

        return 0

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
        self.assertTrue(parser.configparserenhanceddata.has_option("SECTION-A", "key1"))
        self.assertFalse(parser.configparserenhanceddata.has_option("SECTION-A", "Nonexistent Key"))

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
        for k, v in parser.configparserenhanceddata.items("DEP-TEST-A"):
            print(k, v)

        print("\n-[ loginfo ]---------------")
        pprint(parser._loginfo)

        self.assertEqual("value1-A", parser.configparserenhanceddata.get('DEP-TEST-A', 'key1'))
        self.assertEqual("value2-A", parser.configparserenhanceddata.get('DEP-TEST-A', 'key2'))

        print("")
        print("\n-[ DEP-TEST-B ]------------")
        parser.configparserenhanceddata.items("DEP-TEST-B")
        print("\n[DEP-TEST-B]")
        for k, v in parser.configparserenhanceddata.items("DEP-TEST-B"):
            print(k, v)

        print("\n-[ loginfo ]---------------")
        parser._loginfo_print()

        print("\n-[ Validate ]--------------")
        self.assertEqual("value1-A", parser.configparserenhanceddata.get('DEP-TEST-A', 'key1'))
        self.assertEqual("value2-A", parser.configparserenhanceddata.get('DEP-TEST-A', 'key2'))

        self.assertEqual("value1-B", parser.configparserenhanceddata.get('DEP-TEST-B', 'key1'))
        self.assertEqual("value2-A", parser.configparserenhanceddata.get('DEP-TEST-B', 'key2'))

        print("OK")

    def test_ConfigParserEnhanced_configparser_IdenticalKeyError(self):
        """
        Tests that an exception gets fired when configparser.ConfigParser
        encounters a section with two options that have identical key
        values.
        """
        filename_bad = find_config_ini(filename="config_test_configparserenhanced_badkeys.ini")

        print("\n")
        print("Load file: {}".format(filename_bad))

        parser = ConfigParserEnhanced(filename_bad)
        parser.debug_level = 1
        parser.exception_control_level = 0

        with self.assertRaises(configparser.DuplicateOptionError):
            data = parser.parse_section("SECTION-A")

        with self.assertRaises(configparser.DuplicateOptionError):
            data = parser.parse_section("SECTION-B")

        print("OK")

    def test_ConfigParserEnhanced_ini_NoValue(self):
        """
        Tests that we properly handle situations where configparser
        returns a key with ``None`` as the value.

        This can happen when we have an entry in a .ini file like this:

        ```ini
        [NOVALUE_TEST]
        key1:
        key2
        key3:
        ```

        ``key1`` and ``key3`` will both have an empty string ("") as their value
        ``key2`` will be given a ``None`` value by configparser.

        ConfigParserEnhanced should match this behaviour.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 1
        parser.exception_control_level = 0

        expected = {'key1': '', 'key2': None, 'key3': 'value3'}

        actual = parser.configparserenhanceddata["NOVALUE_TEST"]

        print("Expected Section Data:")
        pprint(expected, indent=4, width=40)

        print("Actual Section Data:")
        pprint(actual, indent=4, width=40)

        self.assertDictEqual(expected, actual)

        print("OK")

    def test_ConfigParserEnhanced_test_key_variants(self):
        """
        Test some key variants for unhandled sections (i.e., generic_handler)
        items and make sure we get the right thing.
        """
        section = "KEY_VARIANT_TEST"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 0
        parser.exception_control_level = 0

        data_actual = parser.configparserenhanceddata["KEY_VARIANT_TEST"]

        data_expected = {
            "key1": "value1",
            "key two": "value two",
            "key 'three A'": "value string",
            "key four": "",
            "key five": None
        }

        print("")
        print("Data Expected:")
        pprint(data_expected)
        print("")
        print("Data Actual:")
        pprint(data_actual)
        print("")

        self.assertDictEqual(data_expected, data_actual, "Expected vs. Actual lists do not match.")

        print("OK")

    def test_ConfigParserEnhanced_handler_use_issue010(self):
        """
        Test section names that include dots ``.`` in them.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 5

        print("----[ TEST BEGIN ]----------------------------------")

        section = "TEST_SECTION-0.2.0"
        print("Section  : {}".format(section))
        data_expect = {}
        data_actual = parser.parse_section(section)
        self.assertDictEqual(data_expect, data_actual)

        cped_expect = {'key-0.1.0': 'value-0.1.0', 'key-0.2.0': 'value-0.2.0'}
        cped_actual = parser.configparserenhanceddata[section]
        self.assertDictEqual(cped_expect, cped_actual)

        print("----[ TEST END   ]----------------------------------")

        print("OK")
        return 0

    def test_ConfigParserEnhanced_write(self):
        """
        Test the method :py:meth:`ConfigParserEnahnced.write`
        """
        section = "SECTION-A+"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        self.assertIsInstance(parser, ConfigParserEnhanced)

        with open("___ConfigParserEnhanced_cpe_write.ini", "w") as ofp:
            parser.write(ofp)

        with open("___ConfigParserEnhanced_cpe_write.ini", "w") as ofp:
            parser.write(ofp, section=section)

        with open("___ConfigParserEnhanced_cpe_write.ini", "w") as ofp:
            parser.write(ofp, space_around_delimiters=False)

        with self.assertRaises(KeyError):
            with open("___ConfigParserEnhanced_cpe_write.ini", "w") as ofp:
                parser.write(ofp, space_around_delimiters=False, section="ASDFASDFASDFASDF")

        return 0

    def test_ConfigParserEnhanced_unroll_to_str(self):
        """
        Basic test template
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        print("----[ TEST BEGIN ]----------------------------------")
        section = "SECTION-A"
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 5

        text_expect = textwrap.dedent(
            """\
        [SECTION-A]
        key1:value1
        key2:value2
        key3:value3
        """
        )

        text_actual = parser.unroll_to_str(
            section=section, space_around_delimiters=False, use_base_class_parser=False
        )

        print("Expected:\n{}".format(text_expect))
        print("Actual  :\n{}".format(text_expect))

        self.assertEqual(text_expect, text_actual)
        print("----[ TEST END   ]----------------------------------")

        print("OK")
        return 0

    def test_ConfigParserEnhanced_DEFAULT_parsed(self):
        """
        Test that the DEFAULT section does get parsed.
        """
        filename_ini = find_config_ini(filename="config_test_configparserenhanced_default.ini")
        print("\n")
        print("Load file: {}".format(filename_ini))

        print("----[ TEST BEGIN ]----------------------------------")
        section = "SECTION-A+"
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(filename_ini)
        parser.debug_level = 5
        parser.exception_control_level = 5

        # execute the parse of the section
        parser.parse_section(section)

        ref_cpedata = parser.configparserenhanceddata

        section_data_expect = {
            'Key D1': 'value A+D1', # overwritten in section A+
            'key A1': 'value A1',
            'key A2': 'value A2',
            'key A3': 'value A+3',  # overwritten in section A+
            'key A+4': 'value A+4'
        }

        # retrieves the _cached_ result from the earlier parse.
        # - Note: if we omit the `parse_section` command above then
        #         this call would trigger the parse.
        section_data_actual = ref_cpedata.get(section)

        self.assertDictEqual(section_data_expect, section_data_actual)
        print("----[ TEST END   ]----------------------------------")

        print("----[ TEST BEGIN ]----------------------------------")
        # Test what happens if we load a different section, do we still
        # get the DEFAUL in _that_ sections data?

        section = "SECTION-A"

        ref_cpedata = parser.configparserenhanceddata

        section_data_expect = {
            'Key D1': 'value D1', 'key A1': 'value A1', 'key A2': 'value A2', 'key A3': 'value A3'
        }

        section_data_actual = ref_cpedata.get(section)
        self.assertDictEqual(section_data_expect, section_data_actual)

        print("----[ TEST END   ]----------------------------------")

        print("OK")
        return 0

    def test_ConfigParserEnhanced_EMPTY_SECTION(self):
        """
        Check that an empty section is handled ok.
        """
        filename_ini = find_config_ini(filename="config_test_configparserenhanced.ini")
        print("\n")
        print("Load file: {}".format(filename_ini))

        print("----[ TEST BEGIN ]----------------------------------")
        section = "EMPTY_SECTION"
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(filename_ini)
        parser.debug_level = 5
        parser.exception_control_level = 5

        ref_cpedata = parser.configparserenhanceddata

        section_data_expect = {}
        section_data_actual = ref_cpedata.get(section)

        self.assertDictEqual(section_data_expect, section_data_actual)
        print("----[ TEST END   ]----------------------------------")
        print("OK")
        return 0

    def test_ConfigParserEnhanced_VALIDATOR_01(self):
        """
        Check that section validation operates correctly.
        """
        filename_ini = find_config_ini(filename="config_test_configparserenhanced_validation_01.ini")
        print("\n")
        print("Load file: {}".format(filename_ini))

        # Test just `SECTION B` which should PASS
        print("----[ TEST BEGIN ]----------------------------------")
        section = "SECTION B"
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(filename_ini)
        parser.debug_level = 0
        parser.exception_control_level = 5

        rval = parser.assert_section_all_options_handled(section)
        self.assertEqual(0, rval)
        print("----[ TEST END   ]----------------------------------")

        # Test the whole file. this file should PASS
        print("----[ TEST BEGIN ]----------------------------------")
        rval = parser.assert_file_all_sections_handled()
        self.assertEqual(0, rval)
        print("----[ TEST END   ]----------------------------------")

        print("OK")
        return 0

    def test_ConfigParserEnhanced_VALIDATOR_02(self):
        """
        Check that section validation operates correctly.
        """
        filename_ini = find_config_ini(filename="config_test_configparserenhanced_validation_02.ini")
        print("\n")
        print("Load file: {}".format(filename_ini))

        # Test individual section, `SECTION B` which should PASS
        print("----[ TEST BEGIN A ]----------------------------------")
        section = "SECTION B"
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(filename_ini)
        parser.debug_level = 0
        parser.exception_control_level = 5

        rval = parser.assert_section_all_options_handled(section)
        self.assertEqual(0, rval)
        print("----[ TEST END A  ]----------------------------------")

        # Test individual section, `SECTION C` which should FAIL
        print("----[ TEST BEGIN B ]----------------------------------")
        section = "SECTION C"
        print("Section  : {}".format(section))

        with self.assertRaises(ValueError):
            rval = parser.assert_section_all_options_handled(section)
        print("----[ TEST END B   ]----------------------------------")

        # Test whole-file parsing which should FAIL due to sections
        # C and D.
        print("----[ TEST BEGIN C ]----------------------------------")
        with self.assertRaises(ValueError):
            parser.assert_file_all_sections_handled()
        print("----[ TEST END C   ]----------------------------------")

        print("OK")
        return 0

    def test_ConfigParserEnhanced_VALIDATOR_03(self):
        """
        Check that section validation operates correctly.
        - Multi-ini file test.
        """
        filename_ini = []
        filename_ini.append(find_config_ini(filename="config_test_configparserenhanced_validation_03a.ini"))
        filename_ini.append(find_config_ini(filename="config_test_configparserenhanced_validation_03b.ini"))

        print("\n")
        print("Load file: {}".format(filename_ini))

        # Test individual section, `SECTION B` which should PASS
        print("----[ TEST BEGIN A ]----------------------------------")
        section = "SECTION B"
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(filename_ini)
        parser.debug_level = 0
        parser.exception_control_level = 5

        rval = parser.assert_section_all_options_handled(section)
        self.assertEqual(0, rval)
        print("----[ TEST END A  ]----------------------------------")

        # Test individual section, `SECTION C` which should FAIL
        print("----[ TEST BEGIN B ]----------------------------------")
        section = "SECTION C"
        print("Section  : {}".format(section))

        with self.assertRaises(ValueError):
            rval = parser.assert_section_all_options_handled(section)
        print("----[ TEST END B   ]----------------------------------")

        # Test whole-file parsing which should FAIL due to sections
        # C and D.
        print("----[ TEST BEGIN C ]----------------------------------")
        with self.assertRaises(ValueError):
            parser.assert_file_all_sections_handled()
        print("----[ TEST END C   ]----------------------------------")

        print("OK")
        return 0

    def test_ConfigParserEnhanced_get_known_operations(self):
        """
        Check that section validation operates correctly.
        """

        class ConfigParserEnhancedTest(ConfigParserEnhanced):

            @ConfigParserEnhanced.operation_handler
            def _handler_handlebars_are_cool(
                self, section_name, handler_parameters, processed_sections=None
            ) -> int:
                print("Handlebars are cool!")
                return 0

        filename_ini = find_config_ini(filename="config_test_configparserenhanced_validation_02.ini")
        print("\n")
        print("Load file: {}".format(filename_ini))

        # Test individual section, `SECTION B` which should PASS
        print("----[ TEST BEGIN A ]----------------------------------")
        section = "SECTION B"
        print("Section  : {}".format(section))

        parser = ConfigParserEnhancedTest(filename_ini)
        parser.debug_level = 0
        parser.exception_control_level = 5

        known_operations = parser.get_known_operations()

        #self.assertIn("handlebars-are-cool", known_operations)
        #self.assertIn("use", known_operations)
        print("----[ TEST END A  ]----------------------------------")

        print("OK")
        return 0



# ===========================================================
#   Test ConfigParserEnhancedDataTest
# ===========================================================



class ConfigParserEnhancedDataTest(TestCase):
    """
    Main test driver for the ConfigParserEnhancedData class

    This is heavily tied to ConfigParserEnhanced because this class
    can't really exist outside of it.
    """

    def setUp(self):
        print("")
        self.maxDiff = None
        self._filename = find_config_ini(filename="config_test_configparserenhanced.ini")
        return 0

    def test_ConfigParserDataEnhanced_Template(self):
        """
        This is the basic test template
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 3
        parser.exception_control_level = 5
        parser.exception_control_compact_warnings = False

        print("-----[ TEST START ]--------------------------------------------------")
        print("<description>")

        section = "SECTION-A"
        print("Section  : {}".format(section))

        print("-----[ TEST END   ]--------------------------------------------------\n")

        print("OK")
        return 0

    def test_ConfigParserDataEnhanced_repr(self):
        """
        Test the __repr__ method
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 3
        parser.exception_control_level = 5
        parser.exception_control_compact_warnings = False

        print("-----[ TEST START ]--------------------------------------------------")
        print("<description>")

        section = "SECTION-A"
        print("Section  : {}".format(section))

        parser.parse_section(section)

        # This should trigger the __repr__ method.
        print(parser.configparserenhanceddata)
        print("-----[ TEST END   ]--------------------------------------------------\n")

        print("OK")
        return 0

    def test_ConfigParserDataEnhanced_property_configparser_delimiters(self):
        """
        Test the ``configparser_delimiters`` property
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 3
        parser.exception_control_level = 5
        parser.exception_control_compact_warnings = False

        print("-----[ TEST START ]--------------------------------------------------")
        print("Get the default value when the property doesn't already exist")
        parser._reset_configparserdata()
        rval_expect = ('=', ':')
        rval_actual = parser.configparser_delimiters
        self.assertTupleEqual(rval_expect, rval_actual)
        print("-----[ TEST END   ]--------------------------------------------------\n")

        print("-----[ TEST START ]--------------------------------------------------")
        print("assign a new value to the delimiters")
        parser.configparser_delimiters = '='
        print("-----[ TEST END   ]--------------------------------------------------\n")

        print("-----[ TEST START ]--------------------------------------------------")
        print("Load the existing internal value.")
        rval_expect = ('=', )
        rval_actual = parser.configparser_delimiters
        self.assertTupleEqual(rval_expect, rval_actual)
        print("-----[ TEST END   ]--------------------------------------------------\n")

        print("-----[ TEST START ]--------------------------------------------------")
        print("assign an invalid type to the delimiters.")
        with self.assertRaises(TypeError):
            parser.configparser_delimiters = None
        print("-----[ TEST END   ]--------------------------------------------------\n")

        print("OK")
        return 0

    def test_ConfigParserDataEnhanced_method_parse_all_sections(self):
        """
        This is the basic test template
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 1
        parser.exception_control_level = 3
        parser.exception_control_compact_warnings = True

        print("-----[ TEST START ]--------------------------------------------------")
        parser.parse_all_sections()
        print("-----[ TEST END   ]--------------------------------------------------")

        print("OK")
        return

    def test_ConfigParserDataEnhanced_property_data(self):
        """
        Testing of some options for the ``data`` property.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 3
        parser.exception_control_level = 5
        parser.exception_control_compact_warnings = True

        default_section_name = parser._internal_default_section_name

        print("-----[ TEST START ]--------------------------------------------------")
        parser.configparserenhanceddata.data = {}
        self.assertFalse(default_section_name in parser.configparserenhanceddata.data.keys())
        print("-----[ TEST END   ]--------------------------------------------------")

        print("OK")
        return 0

    def test_ConfigParserEnhancedData_Miscellaneous_01(self):
        """
        """
        section = "SECTION-A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 5

        print("-----[ TEST START ]--------------------------------------------------")

        parser.parse_section(section)

        inst = ConfigParserEnhanced.ConfigParserEnhancedData(parser)

        # Trigger the 'None' default option for owner (when it doesn't exist)
        delattr(inst, '_owner_data')
        # new_owner = inst._owner

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

        print("-----[ TEST END   ]--------------------------------------------------")

        print("OK")
        return 0

    def test_ConfigParserDataEnhanced_ini_section_has_empty_section(self):
        """
        Test what happens if we load an empty section.
        """
        section = "SEC_EMPTY"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 3
        parser.exception_control_level = 5

        print("-----[ TEST START ]--------------------------------------------------")

        result_expect = {}
        result_actual = parser.configparserenhanceddata[section]
        self.assertDictEqual(result_expect, result_actual)

        print("-----[ TEST END   ]--------------------------------------------------")

        print("OK")
        return 0

    def test_ConfigParserDataEnhanced_ini_section_has_no_generic_entries(self):
        """
        Test what happens if we load a section that has no 'generic operations'
        """
        section = "SEC_ALL_HANDLED"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 3
        parser.exception_control_level = 5

        print("-----[ TEST START ]--------------------------------------------------")

        result_expect = {}
        result_actual = parser.configparserenhanceddata[section]
        self.assertDictEqual(result_expect, result_actual)

        print("-----[ TEST END   ]--------------------------------------------------")

        print("OK")
        return

    def test_ConfigParserDataEnhanced_method_get_01(self):
        """
        Test ``ConfigParserDataEnhanced.get()`` method.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 3
        parser.exception_control_level = 5

        print("-----[ TEST START ]--------------------------------------------------")
        section = "SECTION-A"
        print("Section  : {}".format(section))
        result_expect = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
        result_actual = parser.configparserenhanceddata.get(section)
        self.assertDictEqual(result_expect, result_actual)
        print("-----[ TEST END   ]--------------------------------------------------")

        print("-----[ TEST START ]--------------------------------------------------")
        section = "SECTION-A"
        print("Section  : {}".format(section))
        result_expect = 'value2'
        result_actual = parser.configparserenhanceddata.get(section, "key2")
        self.assertEqual(result_expect, result_actual)
        print("-----[ TEST END   ]--------------------------------------------------")

        print("-----[ TEST START ]--------------------------------------------------")
        section = "SECTION-A"
        print("Section  : {}".format(section))
        result_expect = 'value2'
        with self.assertRaises(KeyError):
            result_actual = parser.configparserenhanceddata.get(section, "key400")
            self.assertEqual(result_expect, result_actual)
        print("-----[ TEST END   ]--------------------------------------------------")

        print("OK")
        return

    def test_ConfigParserDataEnhanced_method_getitem_01(self):
        """
        Test ``ConfigParserDataEnhanced.__getitem__`` method.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 3
        parser.exception_control_level = 5

        print("-----[ TEST START ]--------------------------------------------------")

        section = "SECTION-A"
        print("Section  : {}".format(section))
        result_expect = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
        result_actual = parser.configparserenhanceddata[section]
        self.assertDictEqual(result_expect, result_actual)

        print("-----[ TEST END   ]--------------------------------------------------")

        print("OK")
        return

    def test_ConfigParserDataEnhanced_method_getitem_02(self):
        """
        Test ``ConfigParserDataEnhanced.__getitem__`` method.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 3
        parser.exception_control_level = 5

        print("-----[ TEST START ]--------------------------------------------------")

        section = "SECTION-A+"
        print("Section  : {}".format(section))
        result_expect = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3', 'key4': 'value4'}
        result_actual = parser.configparserenhanceddata[section]
        self.assertDictEqual(result_expect, result_actual)

        print("-----[ TEST END   ]--------------------------------------------------")

        print("OK")
        return 0

    def test_ConfigParserDataEnhanced_method_getitem_03(self):
        """
        Test ``ConfigParserDataEnhanced.__getitem__`` method.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 3
        parser.exception_control_level = 5

        print("-----[ TEST START ]--------------------------------------------------")

        section = "KEY_VARIANT_TEST"
        print("Section  : {}".format(section))
        result_expect = {
            'key1': 'value1',
            'key two': 'value two',
            "key 'three A'": 'value string',
            'key four': '',
            'key five': None
        }
        result_actual = parser.configparserenhanceddata[section]
        self.assertDictEqual(result_expect, result_actual)

        print("-----[ TEST END   ]--------------------------------------------------")

        print("OK")
        return 0

    def test_ConfigParserDataEnhanced_method_getitem_04(self):
        """
        Test ``ConfigParserDataEnhanced.__getitem__`` method.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 3
        parser.exception_control_level = 5

        print("-----[ TEST START ]--------------------------------------------------")

        section = parser._internal_default_section_name
        print("Section  : {}".format(section))

        with self.assertRaises(KeyError):
            parser.configparserenhanceddata[section]

        print("-----[ TEST END   ]--------------------------------------------------")

        print("OK")
        return 0

    def test_ConfigParserDataEnhanced_len_01(self):
        """
        Test ``ConfigParserDataEnhanced.__len__`` method.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 3
        parser.exception_control_level = 5

        num_sections_in_ini = len(parser.configparserdata.sections())

        print("-----[ TEST START ]--------------------------------------------------")

        section = "SECTION-A"
        print("Section  : {}".format(section))
        parser.parse_section(section)
        result_expect = num_sections_in_ini
        result_actual = len(parser.configparserenhanceddata)
        self.assertEqual(result_expect, result_actual)

        section = "SECTION-A+"
        print("Section  : {}".format(section))
        parser.parse_section(section)
        result_expect = num_sections_in_ini
        result_actual = len(parser.configparserenhanceddata)
        self.assertEqual(result_expect, result_actual)

        # this will add `SECTION-B+` and `SECTION-B`
        section = "SECTION-B+"
        print("Section  : {}".format(section))
        data = parser.parse_section(section)
        result_expect = num_sections_in_ini
        result_actual = len(parser.configparserenhanceddata)
        self.assertEqual(result_expect, result_actual)

        section = "SEC_EMPTY"
        print("Section  : {}".format(section))
        parser.parse_section(section)
        result_expect = num_sections_in_ini
        result_actual = len(parser.configparserenhanceddata)
        self.assertEqual(result_expect, result_actual)

        section = "SEC_ALL_HANDLED"
        print("Section  : {}".format(section))
        parser.parse_section(section)
        result_expect = num_sections_in_ini
        result_actual = len(parser.configparserenhanceddata)
        self.assertEqual(result_expect, result_actual)

        print("-----[ TEST END   ]--------------------------------------------------")

        print("OK")
        return 0

    def test_ConfigParserDataEnhanced_iter_01(self):
        """
        Test the iterator ``__iter__`` for ``ConfigParserDataEnhanced``
        which will iterate over sections that have been added so far
        to ConfigParserDataEnhanced.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 0
        parser.exception_control_level = 5

        print("-----[ TEST START ]--------------------------------------------------")

        section = "SECTION-A+"
        parser.configparserenhanceddata[section]
        section = "SECTION-B+"
        parser.configparserenhanceddata[section]

        for isec in parser.configparserenhanceddata:
            print("isec: {}".format(isec))
            bkpt = None

        print("-----[ TEST END   ]--------------------------------------------------")

        print("OK")
        return

    def test_ConfigParserDataEnhanced_keys(self):
        """
        Test the ``keys()`` method.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 5

        print("-----[ TEST START ]--------------------------------------------------")
        key_list_expect = [
            'SECTION-A',
            'SECTION-B',
            'SECTION C',
            'SECTION-A+',
            'SECTION-B+',
            'SECTION C+',
            'OPERAND_TEST',
            'BAD_CHAR_IN_OP',
            'CYCLE_TEST_A',
            'CYCLE_TEST_B',
            'CYCLE_TEST_C',
            'ENVVAR-PREPEND-TEST',
            'HANDLER_FAIL_TEST',
            'DEP-TEST-A',
            'DEP-TEST-B',
            'AMBIGUOUS_HANDLER_TEST',
            'NOVALUE_TEST',
            'KEY_VARIANT_TEST',
            'SEC_EMPTY',
            'SEC_ALL_HANDLED',
            'TEST_SECTION-0.1.0',
            'TEST_SECTION-0.2.0',
            'EMPTY_SECTION'
        ]
        len_expect = len(key_list_expect)

        keys = parser.configparserenhanceddata.keys()

        for ikey in keys:
            print("key: {}".format(ikey))

        len_actual = len(keys)
        self.assertEqual(len_expect, len_actual, "Key length mismatch")
        self.assertListEqual(key_list_expect, list(keys))
        print("-----[ TEST END   ]--------------------------------------------------")

        print("OK")
        return

    def test_ConfigParserDataEnhanced_sections(self):
        """
        Test the ``sections`` entry in ``ConfigParserEnhancedData``
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 3
        parser.exception_control_level = 5

        print("-----[ TEST START ]--------------------------------------------------")
        sec_list_expect = [
            'SECTION-A',
            'SECTION-B',
            'SECTION C',
            'SECTION-A+',
            'SECTION-B+',
            'SECTION C+',
            'OPERAND_TEST',
            'BAD_CHAR_IN_OP',
            'CYCLE_TEST_A',
            'CYCLE_TEST_B',
            'CYCLE_TEST_C',
            'ENVVAR-PREPEND-TEST',
            'HANDLER_FAIL_TEST',
            'DEP-TEST-A',
            'DEP-TEST-B',
            'AMBIGUOUS_HANDLER_TEST',
            'NOVALUE_TEST',
            'KEY_VARIANT_TEST',
            'SEC_EMPTY',
            'SEC_ALL_HANDLED',
            'TEST_SECTION-0.1.0',
            'TEST_SECTION-0.2.0',
            'EMPTY_SECTION'
        ]
        len_expect = len(sec_list_expect)

        sections = parser.configparserenhanceddata.sections()

        for isec in sections:
            print(isec)

        len_actual = len(sections)
        self.assertEqual(len_expect, len_actual, "Section list length mismatch")
        self.assertListEqual(sec_list_expect, list(sections))

        print("-----[ TEST END   ]--------------------------------------------------")

        print("OK")
        return

    def test_ConfigParserDataEnhanced_sections_arg_parse(self):
        """
        Test ``sections(parse=True)`` in ``ConfigParserEnhancedData``
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 3
        parser.exception_control_level = 4
        parser.exception_control_compact_warnings = True
        parser.exception_control_silent_warnings = False

        print("-----[ TEST START ]--------------------------------------------------")
        sections = parser.configparserenhanceddata.sections(parse=True)

        print("Section names:")
        for isec in sections:
            print(isec)

        # Note: the _loginfo data will only contain the data from the _last_ section
        #       in the .ini file.
        self.assertTrue(hasattr(parser, '_loginfo'))
        section_entry_list = [d['name'] for d in parser._loginfo if d['type'] == 'section-entry']
        section_exit_list = [d['name'] for d in parser._loginfo if d['type'] == 'section-exit']
        self.assertListEqual(section_entry_list, section_exit_list[::-1])

        # Just checking that we _did_ parse sections is sufficient here
        # to prove that this _did_ trigger the parses.
        self.assertTrue(len(section_entry_list) > 0)
        print("-----[ TEST END   ]--------------------------------------------------")

        print("-----[ TEST START ]--------------------------------------------------")
        # Round 2 - Everything would be cached so we shouldn't need to re-parse things.

        # Wipe the loginfo, it should remain empty the 2nd time we list the sections.
        parser._reset_lazy_attr("_loginfo")

        sections = parser.configparserenhanceddata.sections(parse=True)

        print("Section names:")
        for isec in sections:
            print(isec)

        # _loginfo isn't generated because we didn't re-parse anything.
        self.assertFalse(hasattr(parser, '_loginfo'))
        print("-----[ TEST END   ]--------------------------------------------------")

        print("-----[ TEST START ]--------------------------------------------------")
        # Round 3 - Setting parse = "force" will force a re-parse of the data. In this
        # case we should now have a _loginfo object created.

        # Wipe the loginfo, it should remain empty the 2nd time we list the sections.
        parser._reset_lazy_attr("_loginfo")

        sections = parser.configparserenhanceddata.sections(parse="force")

        print("Section names:")
        for isec in sections:
            print(isec)

        # Let's pull only the "entry" list from _loginfo and compare it to the
        # reversed "exit" list from the time we first parsed the data.  They
        # should be equal.
        self.assertTrue(hasattr(parser, '_loginfo'))
        section_entry_list = [d['name'] for d in parser._loginfo if d['type'] == 'section-entry']
        self.assertListEqual(section_entry_list, section_exit_list[::-1])
        print("-----[ TEST END   ]--------------------------------------------------")

        print("-----[ TEST START ]--------------------------------------------------")
        # Check for a bad-type assigned to `parse`
        with self.assertRaises(TypeError):
            sections = parser.configparserenhanceddata.sections(parse=None)
        print("-----[ TEST END   ]--------------------------------------------------")

        print("-----[ TEST START ]--------------------------------------------------")
        # Check for a bad-value assigned to `parse`
        with self.assertRaises(ValueError):
            sections = parser.configparserenhanceddata.sections(parse="definitely not the right value")
        print("-----[ TEST END   ]--------------------------------------------------")

        print("OK")
        return

    def test_ConfigParserDataEnhanced_has_section(self):
        """
        Test the ``has_section`` method.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 3
        parser.exception_control_level = 5

        print("-----[ TEST START ]--------------------------------------------------")

        section = "SECTION-A"
        print("Section  : {}".format(section))
        result_expect = True
        result_actual = parser.configparserenhanceddata.has_section(section)
        print("Results: {} == {} ?".format(result_expect, result_actual))
        self.assertEqual(result_expect, result_actual, "Expected section not found.")

        section = "JELLY DOUGHNUT"
        print("Section  : {}".format(section))
        result_expect = False
        result_actual = parser.configparserenhanceddata.has_section(section)
        print("Results: {} == {} ?".format(result_expect, result_actual))
        self.assertEqual(result_expect, result_actual, "Expected section not found.")

        print("-----[ TEST END   ]--------------------------------------------------")

        print("OK")
        return

    def test_ConfigParserDataEnhanced_has_option(self):
        """
        This is the basic test template
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 5

        print("-----[ TEST START ]--------------------------------------------------")

        section = "SECTION-A"
        option = "key1"
        print("has_option : {} in {} ?".format(option, section))
        result_expect = True
        result_actual = parser.configparserenhanceddata.has_option(section, option)
        self.assertEqual(result_expect, result_actual, "has_option failed to find existing option.")

        section = "SECTION-A"
        option = "key4"
        print("has_option : {} in {} ?".format(option, section))
        result_expect = False
        result_actual = parser.configparserenhanceddata.has_option(section, option)
        self.assertEqual(result_expect, result_actual, "has_option found missing option?")

        section = "SECTION-A"
        option = "definitely does not exist"
        print("has_option : {} in {} ?".format(option, section))
        result_expect = False
        result_actual = parser.configparserenhanceddata.has_option(section, option)
        self.assertEqual(result_expect, result_actual, "has_option found missing option?")

        print("-----[ TEST END   ]--------------------------------------------------")

        print("OK")
        return

    def test_ConfigParserDataEnhanced_has_option_no_owner(self):
        """
        This is the basic test template
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 3
        parser.exception_control_level = 5

        print("-----[ TEST START ]--------------------------------------------------")
        # deleting the owner will force the property to be `None`
        delattr(parser.configparserenhanceddata, '_owner_data')

        section = "SECTION-A"
        option = "key1"
        print("has_option : {} in {} ?".format(option, section))
        result_expect = False
        result_actual = parser.configparserenhanceddata.has_option(section, option)
        print("-----[ TEST END   ]--------------------------------------------------")

        print("OK")
        return 0

    def test_ConfigParserDataEnhanced_has_section_no_parse(self):
        """
        This is the basic test template
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 3
        parser.exception_control_level = 5

        print("-----[ TEST START ]--------------------------------------------------")

        section = "SECTION-A"
        print("Section  : {}".format(section))
        result_expect = False
        result_actual = parser.configparserenhanceddata.has_section_no_parse(section)
        print("Results: {} == {} ?".format(result_expect, result_actual))
        self.assertEqual(result_expect, result_actual, "Expected section not found.")

        print("initiate a parse of section {}".format(section))
        parser.configparserenhanceddata[section]

        # now it should exist in the 'parsed' set of data keys.
        result_expect = True
        result_actual = parser.configparserenhanceddata.has_section_no_parse(section)
        print("Results: {} == {} ?".format(result_expect, result_actual))
        self.assertEqual(result_expect, result_actual, "Expected section not found.")

        print("-----[ TEST END   ]--------------------------------------------------")

        print("OK")
        return

    def test_ConfigParserDataEnhanced_items(self):
        """
        This is the basic test template
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 5

        parser.exception_control_level = 4

        # With no parameters to items() the behaviour is to loop over the
        # whole structure -- all sections.
        print("-----[ TEST START ]--------------------------------------------------")
        count_expect = len(parser.configparserdata.sections())
        count_actual = 0
        for k, v in parser.configparserenhanceddata.items():
            pass
        for k, v in parser.configparserenhanceddata.items():
            print("{}:{}".format(k, v))
            count_actual += 1
        self.assertEqual(count_expect, count_actual)
        print("-----[ TEST END   ]--------------------------------------------------")

        # with a specific section provided, we loop over the options in just that section.
        print("-----[ TEST START ]--------------------------------------------------")
        section = "SECTION-A"
        count_expect = 3
        count_actual = 0
        for k, v in parser.configparserenhanceddata.items(section):
            print("{}:{}".format(k, v))
            count_actual += 1
        self.assertEqual(count_expect, count_actual)

        print("-----[ TEST END   ]--------------------------------------------------")
        print("OK")
        return 0

    def test_ConfigParserDataEnhanced_owner_default(self):
        """
        Check that the property ``_owner`` will default to ``None``
        if it wasn't set but the property is accessed.

        In practice, this should not happen within ``ConfigParserEnhanced``
        because it will always set the ``_owner`` property when creating
        the structure. This test is mainly here to provide coverage or catch
        someone being naughty.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 3
        parser.exception_control_level = 5

        print("-----[ TEST START ]--------------------------------------------------")

        delattr(parser.configparserenhanceddata, '_owner_data')

        default_owner_expect = None
        default_owner_actual = parser.configparserenhanceddata._owner
        self.assertEqual(default_owner_expect, default_owner_actual)

        print("-----[ TEST END   ]--------------------------------------------------")

        print("-----[ TEST START ]--------------------------------------------------")

        # Test what happens if we set the owner options but _owner is none.

        parser.configparserenhanceddata.exception_control_level = 0
        parser.configparserenhanceddata.debug_level = 0

        # This is basically a noop so we should _not_ get the debug_level and
        # exception_control_level from the _owner.
        parser.configparserenhanceddata._set_owner_options()

        self.assertEqual(0, parser.configparserenhanceddata.debug_level)
        self.assertEqual(0, parser.configparserenhanceddata.exception_control_level)

        print("-----[ TEST END   ]--------------------------------------------------")

        print("-----[ TEST START ]--------------------------------------------------")

        # Test what happens if we set the owner options but _owner is none.

        parser.configparserenhanceddata.exception_control_level = 0
        parser.configparserenhanceddata.debug_level = 0

        # This is basically a noop.
        # - Nothing should be parsed
        # - _set_owner_options should also not be called so we
        #   can use the same test we used in the previous test.
        parser.configparserenhanceddata._parse_owner_section("SECTION-A")

        self.assertEqual(0, parser.configparserenhanceddata.debug_level)
        self.assertEqual(0, parser.configparserenhanceddata.exception_control_level)
        print("-----[ TEST END   ]--------------------------------------------------")

        print("-----[ TEST START ]--------------------------------------------------")
        # Check that if we try and get the keys() data and we have no _owner
        # then we'll just get whatever is in ``data.keys()``.

        parser.configparserenhanceddata.data["TEST"] = "FOO"

        # Test what happens if we set the owner options but _owner is none.
        keys_expect = parser.configparserenhanceddata.data.keys()
        keys_actual = parser.configparserenhanceddata.keys()

        self.assertListEqual(list(keys_expect), list(keys_actual))

        del parser.configparserenhanceddata.data["TEST"]
        print("-----[ TEST END   ]--------------------------------------------------")

        print("OK")
        return

    def test_ConfigParserDataEnhanced__parse_owner_section(self):
        """
        Test parameter options for `_parse_owner_section()`
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = ConfigParserEnhanced(self._filename)
        parser.debug_level = 3
        parser.exception_control_level = 5
        parser.exception_control_compact_warnings = True

        print("-----[ TEST START ]--------------------------------------------------")
        # _parse_owner_section should throw a TypeError if force_parse isn't a bool.
        with self.assertRaises(TypeError):
            parser.configparserenhanceddata._parse_owner_section("SECTION-A", force_parse=None)
        print("-----[ TEST END   ]--------------------------------------------------")

        print("OK")
        return



# EOF
