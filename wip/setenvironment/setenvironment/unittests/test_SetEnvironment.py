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



class mock_popen(object):
    """
    Abstract base class for popen mock
    """
    def __init__(self, cmd, stdout=None, stderr=None):
        print("mock_popen> {}".format(cmd))
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = None

    def communicate(self):
        print("mock_popen> communicate()")
        stdout = b"os.environ['__foobar__'] ='baz'\ndel os.environ['__foobar__']"
        stderr = b"stderr=1"
        self.returncode = 0
        return (stdout,stderr)



class mock_popen_status_ok(mock_popen):
    """
    Specialization of popen mock that will return with success.
    """
    def __init__(self, cmd, stdout=None, stderr=None):
        super(mock_popen_status_ok, self).__init__(cmd,stdout,stderr)



class mock_popen_status_error_rc0(mock_popen):
    """
    Specialization of popen mock.

    Simulates the results from a modulecmd operation that had
    an error loading a module (maybe not found). Modulecmd will tend
    to have a message like "ERROR: could not load module" in its stderr
    field but it will generally return an exit status of 0.
    """
    def __init__(self, cmd, stdout=None, stderr=None):
        super(mock_popen_status_error_rc0, self).__init__(cmd,stdout,stderr)

    def communicate(self):
        print("mock_popen> communicate()")
        stdout = b"_mlstatus = False\n"
        stderr = b"ERROR: Unable to locate a modulefile for 'gcc/1.2.3'\n"
        self.returncode = 0
        return (stdout,stderr)



class mock_popen_status_error_rc1(mock_popen):
    """
    Specialization of popen mock that will return with error.

    Test the condition where modulecmd returned a status of 1 and
    has `ERROR:` in its stderr field.
    """
    def __init__(self, cmd, stdout=None, stderr=None):
        super(mock_popen_status_error_rc1, self).__init__(cmd,stdout,stderr)

    def communicate(self):
        print("mock_popen> communicate()")
        stdout = b"_mlstatus = False\n"
        stderr = b"ERROR: Unable to locate a modulefile for 'gcc/1.2.3'\n"
        self.returncode = 1
        return (stdout,stderr)



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


    def test_SetEnvironment_Template(self):
        """
        Basic template test for SetEnvironment.

        This test doesn't really validate any output -- it just runs a basic check.
        """
        section = "CONFIG_A+"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 5

        print("-----[ TEST BEGIN ]----------------------------------------")

        # parse a section
        data = parser.parse_section(section)

        # Pretty print the actions (unchecked)
        print("")
        parser.pretty_print_actions()

        print("-----[ TEST END ]------------------------------------------")

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
        section = "MODULE_USE_BADPATH"

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
        # - the missing file will generate a RuntimeError, but the message
        #   that will get generated down in the ``exception_control_event``
        #   should have the details.
        with self.assertRaises(RuntimeError):
            parser.apply()

        print("OK")
        return


    def test_SetEnvironment_method_apply_module_load_noexist(self):
        """
        Test that we correctly deal with module loads that fail
        because the module didn't exist.

        This might not really easily be testable because applications
        like ``modulecmd`` and ``lmod`` tend to "fail gracefully" without
        returning a nonzero status code.

        This kind of stuff is why we might want to roll our own wrapper
        to those commands someday that is better than what we currently
        have in ModuleHelper.
        """
        section = "MODULE_LOAD_NOEXIST"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 5

        # parse a section
        data = parser.parse_section(section)

        # Pretty print the actions
        print("")
        parser.pretty_print_actions()

        # Apply the actions but use our popen mock routine that emulates
        # a bad output.
        with self.assertRaises(RuntimeError):

            # Patch in our version of Popen which will emulate what a 'module load'
            # of a missing module will return. This is for consistency because it
            # seems modulecmd does slightly different things across different
            # platforms.
            # This should ensure that we take the 'right' path in ModuleHelper.module
            # that we want to test here and trigger the RuntimeError.
            with patch('subprocess.Popen', side_effect=mock_popen_status_error_rc0):
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


    def test_SetEnvironment_method_apply_envvar_parameter_check(self):
        """
        Test the ``_apply_envvar()`` method's type checking of parameters.
        """
        section = "ENVVAR_VAR_EXPANSION"   # envvars

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 1

        # Test #1 : TypeError should be raised if operation is not a str type.
        operation    = None
        envvar_name  = "FOO"
        envvar_value = "BAR"
        with self.assertRaises(TypeError):
            parser._apply_envvar(operation, envvar_name, envvar_value)

        # Test #2 : TypeError should be raised if envvar_name is not a str type.
        operation    = "envvar-set"
        envvar_name  = None
        envvar_value = "BAR"
        with self.assertRaises(TypeError):
            parser._apply_envvar(operation, envvar_name, envvar_value)

        # Test #3 : TypeError should be raised if envvar_value is not a str or None type.
        operation    = "envvar-set"
        envvar_name  = "FOO"
        envvar_value = 12345
        with self.assertRaises(TypeError):
            parser._apply_envvar(operation, envvar_name, envvar_value)

        # Test #4 : A ValueError will be raised if an unknown operation is given.
        operation    = "envvar-unknown"
        envvar_name  = "FOO"
        envvar_value = "BAR"
        with self.assertRaises(ValueError):
            parser._apply_envvar(operation, envvar_name, envvar_value)



        print("OK")
        return


    def test_SetEnvironment_method_apply_module_parameter_check(self):
        """
        Test the ``_apply_module()`` method's type checking of parameters.
        """
        section = "MODULE_LOAD_OK"   # envvars

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 5

        # Test #1 : TypeError should be raised if operation is not a str type.
        operation    = None
        module_name  = "gcc"
        module_value = "7.3.0"
        with self.assertRaises(TypeError):
            with patch('subprocess.Popen', side_effect=mock_popen_status_ok):
                parser._apply_module(operation, module_name, module_value)

        # Test #2 : TypeError should be raised if envvar_name is not a str or None type.
        operation    = "module-load"
        module_name  = 12345
        module_value = "7.3.0"
        with self.assertRaises(TypeError):
            with patch('subprocess.Popen', side_effect=mock_popen_status_ok):
                parser._apply_module(operation, module_name, module_value)

        # Test #3 : TypeError should be raised if envvar_value is not a str or None type.
        operation    = "module-load"
        module_name  = "gcc"
        module_value = 12345
        with self.assertRaises(TypeError):
            with patch('subprocess.Popen', side_effect=mock_popen_status_ok):
                parser._apply_module(operation, module_name, module_value)

        # Test #4 : ValueError is raised if an unknown module operation is provided.
        operation    = "module-undefined"
        module_name  = "gcc"
        module_value = "7.3.0"
        with self.assertRaises(ValueError):
            with patch('subprocess.Popen', side_effect=mock_popen_status_ok):
                parser._apply_module(operation, module_name, module_value)
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


    def test_SetEnvironment_parse_section_generic_options_missing(self):
        """
        A basic test that checks parsing via the ``configparserenhanceddata``
        object. If we parse via that then we probably *should* get an actions
        list constructed since it also calls the ``parse_section()`` method
        under the hood.
        """
        section = "CONFIG_A"

        actions_expect = [
            {'op': 'envvar-set',     'envvar': 'FOO', 'value': 'bar'},
            {'op': 'envvar-append',  'envvar': 'FOO', 'value': 'baz'},
            {'op': 'envvar-prepend', 'envvar': 'FOO', 'value': 'foo'},
            {'op': 'envvar-set',     'envvar': 'BAR', 'value': 'foo'},
            {'op': 'envvar-unset',   'envvar': 'FOO', 'value': None }
        ]

        rval_expect_cped = {}

        self._helper_parse_section(section, actions_expect, rval_expect_cped)

        return


    def test_SetEnvironment_parse_section_generic_options_exist(self):
        """
        Testing the use of parsing a section with operations and generic options
        """
        section = "CONFIG_ENVVAR_WITH_GENERIC_OPTION"

        actions_expect = [
            {'op': 'envvar-set',     'envvar': 'FOO', 'value': 'bar'},
            {'op': 'envvar-append',  'envvar': 'FOO', 'value': 'baz'},
            {'op': 'envvar-prepend', 'envvar': 'FOO', 'value': 'foo'}
        ]

        rval_expect_cped = {'key1': 'value1'}

        self._helper_parse_section(section, actions_expect, rval_expect_cped)

        return


    def test_SetEnvironment_write_actions_to_file_bash(self):
        """
        Test the ``write_actions_to_file`` method with a ``bash`` target.
        """
        section = "CONFIG_A+"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 5

        print("-----[ TEST BEGIN ]----------------------------------------")

        # parse a section
        data = parser.parse_section(section)

        # Pretty print the actions (unchecked)
        print("")
        parser.pretty_print_actions()

        filename_out = "___apply_configuration.sh"
        interpreter  = "bash"
        rval_expect  = 0
        rval_actual  = parser.write_actions_to_file(filename_out, interpreter)

        self.assertEqual(rval_expect, rval_actual)

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return


    def test_SetEnvironment_write_actions_to_file_python(self):
        """
        Test the ``write_actions_to_file`` method with a ``python`` target.
        """
        section = "CONFIG_A+"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 5

        print("-----[ TEST BEGIN ]----------------------------------------")

        # parse a section
        data = parser.parse_section(section)

        # Pretty print the actions (unchecked)
        print("")
        parser.pretty_print_actions()

        filename_out = "___apply_configuration.py"
        interpreter  = "python"
        rval_expect  = 0

        rval_actual  = parser.write_actions_to_file(filename_out, interpreter)
        self.assertEqual(rval_expect, rval_actual)

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return


    # =================
    #   H E L P E R S
    # =================



    def _helper_parse_section(self, section, actions_expect, rval_expect_cped):
        """
        Generic helper routine to test various ways of parsing a section
        with verification that the results we get are expected.
        """
        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = SetEnvironment()
        parser.inifilepath = self._filename
        parser.debug_level = 5

        print("-----[ TEST BEGIN ]----------------------------------------")

        ## parse section via configparserenhanceddata accessor
        print("Parse using configparserenhanceddata[{}]:".format(section))
        rval_actual_cped = parser.configparserenhanceddata[section]
        parser.pretty_print_actions()
        actions_actual_cped = parser.actions

        self.assertDictEqual(rval_expect_cped, rval_actual_cped)

        # Reset parser and parse section via parse_section
        parser = SetEnvironment(self._filename)
        parser.debug_level = 5

        # Parse the section using `parse_section()`
        print("Parse using parse_section({}):".format(section))
        rval_expect = { "setenvironment": actions_expect }
        rval_actual = parser.parse_section(section)
        actions_actual_ps = parser.actions

        self.assertDictEqual(rval_expect, rval_actual)

        # Check results

        self.assertListEqual(actions_actual_cped, actions_actual_ps,
                             "Mismatch in result across methods.")

        self.assertListEqual(actions_expect, actions_actual_cped,
                             "configparserenhanceddata[] results validation failed.")

        self.assertListEqual(actions_expect, actions_actual_ps,
                             "parse_section() results validation failed.")

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return



# EOF
