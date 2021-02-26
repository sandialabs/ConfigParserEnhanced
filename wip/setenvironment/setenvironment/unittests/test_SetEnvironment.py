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
try:                                                                                                # pragma: no cover
    import unittest.mock as mock                                                                    # pragma: no cover
except:                                                                                             # pragma: no cover
    import mock                                                                                     # pragma: no cover

from mock import Mock
from mock import MagicMock
from mock import patch

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

from setenvironment import *

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



class SetEnvironmentTest(TestCase):
    """
    Main test driver for the SetEnvironment class
    """
    def setUp(self):
        print("")
        self.maxDiff = None
        self._filename = find_config_ini(filename="config_test_setenvironment.ini")


    def test_SetEnvironment_basic(self):
        """
        Basic template test for SetEnvironment.

        This test doesn't really validate any output -- it just runs a basic check.
        """
        section = "CONFIG_A+"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 1
        #parser.exception_control_level = 4

        # parse a section
        data = parser.parse_section(section)

        # Pretty print the actions (unchecked)
        print("")
        parser.pretty_print_actions()

        print("OK")
        return


    def test_SetEnvironment_load_envvars_sec(self):
        """
        Load just the section that contains the ENVVAR commands.
        """
        section = "CONFIG_A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 1
        #parser.exception_control_level = 4

        # parse a section
        data = parser.parse_section(section)

        # Pretty print the actions (unchecked)
        print("")
        parser.pretty_print_actions()

        print("OK")
        return


    def test_SetEnvironment_load_modules_sec(self):
        """
        Load just the section that contains the MODULE commands.
        """
        section = "CONFIG_B"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 1
        #parser.exception_control_level = 4

        # parse a section
        data = parser.parse_section(section)

        # Pretty print the actions (unchecked)
        print("")
        parser.pretty_print_actions()

        print("OK")
        return


    def test_SetEnvironment_property_actions_default(self):
        """
        Test the ``actions`` property default value.
        """
        section = "CONFIG_A+"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 1

        # Check the default value
        actions_default_expected = []
        actions_default_actual   = parser.actions
        print("Default `actions` property = {}".format(actions_default_actual))
        self.assertEqual(actions_default_actual,
                         actions_default_expected,
                         msg="Default actions property value should be `[]`")

        print("OK")


    def test_SetEnvironment_property_actions_setter(self):
        """
        Test the ``actions`` property setter
        """
        section = "CONFIG_A+"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 1

        # Check a valid assignment
        actions_value_new       = [1,2,3]
        parser.actions          = actions_value_new
        parser_actions_expected = actions_value_new
        parser_actions_actual   = parser.actions
        self.assertListEqual(parser_actions_actual, parser_actions_expected)

        # Check an invalid type assignment
        actions_value_new = None
        with self.assertRaises(TypeError):
            parser.actions = actions_value_new

        print("OK")


    def test_SetEnvironment_method_print_actions(self):
        """
        Coverage check in actions print_actions

        Mostly this test just ensures we're getting coverage.

        Todo: add a value check to the output at some point. For now, it doesn't make
              sense due to ongoing development.
        """
        section = "CONFIG_A+"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 2
        #parser.exception_control_level = 4

        # parse a section
        data = parser.parse_section(section)

        # inject an 'unknown-op' into the actions list.
        parser.actions.append({'module': '???', 'op': 'unknown-op', 'value': '???'})

        # Pretty print the actions (unchecked)
        print("")
        parser.pretty_print_actions()

        print("OK")


    def test_SetEnvironment_handler_envvar_remove(self):
        """
        Additional checks for envvar_remove
        """
        section = "CONFIG_TEST_ENVVAR_REMOVE"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 1
        #parser.exception_control_level = 4

        # parse a section
        data = parser.parse_section(section)

        # Validate the output
        actions_expected = [
            {'op': 'module-use', 'module': None,  'value': '/foo/bar/baz'},
            {'op': 'envvar-set', 'envvar': 'BAR', 'value': 'foo'}
        ]

        print("Verify Matching `actions`:")
        print("Expected:")
        pprint(actions_expected, width=90, indent=4)
        print("Actual")
        pprint(parser.actions, width=90, indent=4)

        self.assertListEqual(actions_expected, parser.actions)

        print("OK")


    def test_SetEnvironment_method_pretty_print_envvars(self):
        """

        """
        section = "CONFIG_A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 1

        #parser.exception_control_level = 4
        print("")
        envvar_include_filter = [
            "SETENVIRONMENT_TEST_"
            ]

        os.environ["SETENVIRONMENT_TEST_ENVVAR_001"]   = "foobar"
        os.environ["SETENVIRONMENT_HIDDEN_ENVVAR_001"] = "baz"

        with patch('sys.stdout', new=StringIO()) as m_stdout:
            parser.pretty_print_envvars(envvar_filter=envvar_include_filter)
            self.assertIn("SETENVIRONMENT_TEST_ENVVAR_001 = foobar", m_stdout.getvalue())
            self.assertIn("SETENVIRONMENT_HIDDEN_ENVVAR_001", m_stdout.getvalue())
            self.assertNotIn("SETENVIRONMENT_HIDDEN_ENVVAR_001 = baz", m_stdout.getvalue())

        # Filtered + keys_only should print out only the one key
        with patch('sys.stdout', new=StringIO()) as m_stdout:
            parser.pretty_print_envvars(envvar_filter=envvar_include_filter, filtered_keys_only=True)
            self.assertIn("SETENVIRONMENT_TEST_ENVVAR_001 = foobar", m_stdout.getvalue())
            self.assertNotIn("SETENVIRONMENT_HIDDEN", m_stdout.getvalue())

        # No options should print all envvars + values
        with patch('sys.stdout', new=StringIO()) as m_stdout:
            parser.pretty_print_envvars()
            self.assertIn("SETENVIRONMENT_TEST", m_stdout.getvalue())
            self.assertIn("SETENVIRONMENT_HIDDEN", m_stdout.getvalue())

        # No filter but we say show filtered keys only should result in
        # print all keys + values.
        with patch('sys.stdout', new=StringIO()) as m_stdout:
            parser.pretty_print_envvars(filtered_keys_only=True)
            self.assertIn("SETENVIRONMENT_TEST", m_stdout.getvalue())
            self.assertIn("SETENVIRONMENT_HIDDEN", m_stdout.getvalue())

        # cleanup
        del os.environ["SETENVIRONMENT_TEST_ENVVAR_001"]
        del os.environ["SETENVIRONMENT_HIDDEN_ENVVAR_001"]

        return


    def test_SetEnvironment_method_apply_envvar_test(self):
        """
        """
        section = "CONFIG_A"   # envvars

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 1

        # parse a section
        data = parser.parse_section(section)

        # Pretty print the actions (unchecked)
        print("")
        parser.pretty_print_actions()

        # Apply the actions
        parser.apply()

        self.assertTrue("BAR" in os.environ.keys())
        self.assertEqual("foo", os.environ["BAR"])

        parser.pretty_print_envvars(["BAR"], True)

        print("OK")
        return


    def test_SetEnvironment_method_apply_module_test(self):
        """
        """
        section = "CONFIG_B"   # envvars

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 1

        # parse a section
        data = parser.parse_section(section)

        # Pretty print the actions (unchecked)
        print("")
        parser.pretty_print_actions()

        # Apply the actions
        parser.apply()

        envvar_truth = [
            ("TEST_SETENVIRONMENT_GCC_VER", "7.3.0")
        ]
        for ienvvar_name,ienvvar_val in envvar_truth:
            self.assertTrue(ienvvar_name in os.environ.keys())
            self.assertEqual(ienvvar_val, os.environ[ienvvar_name])

        print("")
        envvar_filter = ["TEST_SETENVIRONMENT_"]
        parser.pretty_print_envvars(envvar_filter, True)

        print("OK")
        return


    def test_SetEnvironment_method_apply_module_use_badpath(self):
        """
        Test that a `module use <badpath>` will trigger an
        appropriate exception.
        """
        section = "MODULE_USE_BADPATH"   # envvars

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 1

        # parse a section
        data = parser.parse_section(section)

        # Pretty print the actions
        print("")
        parser.pretty_print_actions()

        # Apply the actions
        with self.assertRaises(FileNotFoundError):
            parser.apply()

        print("OK")
        return


    def test_SetEnvironment_method_apply_envvar_expansion(self):
        """
        Tests that an envvar expansion will properly be executed
        during ``apply()``. Uses the following ``.ini`` file section:

            [ENVVAR_VAR_EXPANSION]
            envvar-set ENVVAR_PARAM_01 : "AAA"
            envvar-set ENVVAR_PARAM_02 : "B${ENVVAR_PARAM_01}B"

        The expected result should be:
        - ``ENVVAR_PARAM_01`` = "AAA"
        - ``ENVVAR_PARAM_02`` = "BAAAB"

        """
        section = "ENVVAR_VAR_EXPANSION"   # envvars

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 1

        # parse a section
        data = parser.parse_section(section)

        # Pretty print the actions
        print("")
        parser.pretty_print_actions()

        # Apply the actions
        parser.apply()

        envvar_truth = [
            ("ENVVAR_PARAM_01", "AAA"),
            ("ENVVAR_PARAM_02", "BAAAB")
        ]
        for ienvvar_name,ienvvar_val in envvar_truth:
            self.assertTrue(ienvvar_name in os.environ.keys())
            self.assertEqual(ienvvar_val, os.environ[ienvvar_name])

        print("")
        envvar_filter = ["ENVVAR_PARAM_"]
        parser.pretty_print_envvars(envvar_filter, True)

        print("OK")
        return


    def test_SetEnvironment_method_apply_envvar_expansion_missing(self):
        """
        Tests that an envvar expansion will properly handle a missing envvar
        during expansion. The following .ini section is used to test this:

            [ENVVAR_VAR_EXPANSION_BAD]
            envvar-set ENVVAR_PARAM_01 : "B${ENVVAR_PARAM_MISSING}B"

        This should cause a ``KeyError`` to be raised during ``apply()``
        """
        section = "ENVVAR_VAR_EXPANSION_BAD"   # envvars

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 1

        # parse a section
        data = parser.parse_section(section)

        # Pretty print the actions
        print("")
        parser.pretty_print_actions()

        # Apply the actions
        with self.assertRaises(KeyError):
            parser.apply()

        print("OK")
        return


# EOF


