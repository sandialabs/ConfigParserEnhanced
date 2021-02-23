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
        parser.print_actions()

        print("OK")


    def test_SetEnvironment_property_actions_default(self):
        """
        Test the ``actions`` property default value.
        """
        section = "CONFIG_A"

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
        section = "CONFIG_A"

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


    def test_SetEnvironment_method_print_actions_coverage_01(self):
        """
        Coverage check in actions print_actions

        Mostly this test just ensures we're getting coverage.

        Todo: add a value check to the output at some point. For now, it doesn't make
              sense due to ongoing development.
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

        # inject an 'unknown-op' into the actions list.
        parser.actions.append({'module': '???', 'op': 'unknown-op', 'value': '???'})

        # Pretty print the actions (unchecked)
        print("")
        parser.print_actions()

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


# EOF
