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

import filecmp
from textwrap import dedent

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


def mock_function_return_1(*args, **kwargs):
    print("[mock] Generic function override - returns 1")
    return 1



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

        # Get the location of the unit testing scripts (for file writing tests)
        unit_test_path = os.path.realpath(__file__)
        self.unit_test_file = os.path.basename(unit_test_path)
        self.unit_test_path = os.path.dirname(unit_test_path)


    def test_SetEnvironment_Template(self):
        """
        Basic template test for SetEnvironment.

        This test doesn't really validate any output -- it just runs a basic check.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 5

        print("-----[ TEST BEGIN ]----------------------------------------")

        section = "CONFIG_A+"
        print("Section  : {}".format(section))

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
            {'op': 'module_use', 'module': None,  'value': '/foo/bar/baz'},
            {'op': 'envvar_set', 'envvar': 'BAR', 'value': 'foo'}
        ]

        print("Verify Matching `actions`:")
        print("Expected:")
        pprint(actions_expected, width=90, indent=4)
        print("Actual")
        pprint(parser.actions, width=90, indent=4)

        self.assertListEqual(actions_expected, parser.actions)

        print("OK")
        return


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


    def test_SetEnvironment_method_apply_envvar_test_01(self):
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


    def test_SetEnvironment_method_apply_envvar_test_02(self):
        """
        """

        print("\n")
        print("Load file: {}".format(self._filename))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 5

        print("-----[ TEST BEGIN ]----------------------------------------")

        section = "ENVVAR_UNSET_TEST"
        print("Section  : {}".format(section))

        # parse a section
        data = parser.parse_section(section)

        print("")
        parser.pretty_print_actions()

        # Apply the actions
        parser.apply()

        self.assertFalse("FOO" in os.environ.keys())

        print("-----[ TEST END ]------------------------------------------")

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
            envvar_set ENVVAR_PARAM_01 : "AAA"
            envvar_set ENVVAR_PARAM_02 : "B${ENVVAR_PARAM_01}B"

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
        operation    = "envvar_set"
        envvar_name  = None
        envvar_value = "BAR"
        with self.assertRaises(TypeError):
            parser._apply_envvar(operation, envvar_name, envvar_value)

        # Test #3 : TypeError should be raised if envvar_value is not a str or None type.
        operation    = "envvar_set"
        envvar_name  = "FOO"
        envvar_value = 12345
        with self.assertRaises(TypeError):
            parser._apply_envvar(operation, envvar_name, envvar_value)

        # Test #4 : A ValueError will be raised if an unknown operation is given.
        operation    = "envvar_unknown"
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
        operation    = "module_load"
        module_name  = 12345
        module_value = "7.3.0"
        with self.assertRaises(TypeError):
            with patch('subprocess.Popen', side_effect=mock_popen_status_ok):
                parser._apply_module(operation, module_name, module_value)

        # Test #3 : TypeError should be raised if envvar_value is not a str or None type.
        operation    = "module_load"
        module_name  = "gcc"
        module_value = 12345
        with self.assertRaises(TypeError):
            with patch('subprocess.Popen', side_effect=mock_popen_status_ok):
                parser._apply_module(operation, module_name, module_value)

        # Test #4 : ValueError is raised if an unknown module operation is provided.
        operation    = "module_undefined"
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
            envvar_set ENVVAR_PARAM_01 : "B${ENVVAR_PARAM_MISSING}B"

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
            {'op': 'envvar_set',           'envvar': 'FOO', 'value': 'bar'},
            {'op': 'envvar_append',        'envvar': 'FOO', 'value': 'baz'},
            {'op': 'envvar_prepend',       'envvar': 'FOO', 'value': 'foo'},
            {'op': 'envvar_set',           'envvar': 'BAR', 'value': 'foo'},
            {'op': 'envvar_remove_substr', 'envvar': 'FOO', 'value': 'bar'},
            {'op': 'envvar_unset',         'envvar': 'FOO', 'value': None }
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
            {'op': 'envvar_set',     'envvar': 'FOO', 'value': 'bar'},
            {'op': 'envvar_append',  'envvar': 'FOO', 'value': 'baz'},
            {'op': 'envvar_prepend', 'envvar': 'FOO', 'value': 'foo'}
        ]

        rval_expect_cped = {'key1': 'value1'}

        self._helper_parse_section(section, actions_expect, rval_expect_cped)

        return


    def test_SetEnvironment_helper_apply_envvar_failure(self):
        """
        Simulate a failure to set an envvar.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 5

        section = "CONFIG_A"
        print("Section  : {}".format(section))

        # parse a section
        data = parser.parse_section(section)

        # Pretty print the actions (unchecked)
        print("")
        parser.pretty_print_actions()

        print("-----[ TEST BEGIN ]----------------------------------------")

        # Override the _exec_helper call to force a rvalue of 1. This should
        # trigger the `if output != 0` check at the end of `_apply_envvar`

        # In this case, the RuntimeError exception will be thrown.
        parser.exception_control_level = 5
        with patch.object(SetEnvironment, '_exec_helper', mock_function_return_1 ):
            with self.assertRaises(RuntimeError):
                rval = parser._apply_envvar("envvar_set", "FOO", "BAR")
                self.assertEqual(1, rval)


        # In this case, `exception_control_level` is set to 0 so the RuntimeError
        # isn't raised but the command should still return a nonzero value.
        parser.exception_control_level = 0
        with patch.object(SetEnvironment, '_exec_helper', mock_function_return_1 ):
            rval = parser._apply_envvar("envvar_set", "FOO", "BAR")
            self.assertNotEqual(0, rval)

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return


    def test_SetEnvironment_helper_gen_actions_script_nohdr(self):
        """
        Test `_gen_actions_script` without a header
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = SetEnvironment(self._filename)
        parser.exception_control_level = 5
        parser.debug_level = 5

        section = "CONFIG_A"
        print("Section  : {}".format(section))

        # parse a section
        parser.parse_section(section)

        # Pretty print the actions (unchecked)
        print("")
        parser.pretty_print_actions()

        print("-----[ TEST BEGIN ]----------------------------------------")
        test_incl_hdr = False
        test_interp = "bash"
        rval_expect = dedent("""\
                        # -------------------------------------------------
                        #   S E T E N V I R O N M E N T   C O M M A N D S
                        # -------------------------------------------------
                        envvar_op set FOO bar
                        envvar_op append FOO baz
                        envvar_op prepend FOO foo
                        envvar_op set BAR foo
                        envvar_op remove_substr FOO bar
                        envvar_op unset FOO
                        """).strip()
        rval_actual = parser._gen_actions_script(incl_hdr=test_incl_hdr, interp=test_interp)
        rval_actual = rval_actual.strip()

        self.assertEqual(rval_expect, rval_actual)

        print("-----[ TEST END ]------------------------------------------")
        print("OK")
        return


    def test_SetEnvironment_helper_gen_actions_script_badinterp(self):
        """
        Test `_gen_actions_script` with a bad interpreter
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = SetEnvironment(self._filename)
        parser.exception_control_level = 5
        parser.debug_level = 5

        section = "CONFIG_A"
        print("Section  : {}".format(section))

        # parse a section
        parser.parse_section(section)

        # Pretty print the actions (unchecked)
        print("")
        parser.pretty_print_actions()

        print("-----[ TEST BEGIN ]----------------------------------------")

        # This should throw a ValueError because the `exception_control_event`
        # that gets raised is a `SERIOUS` one which causes a throw if
        # `exception_control_level` is >= 3.
        test_incl_hdr = True
        test_interp = "invalid_interpreter"
        with self.assertRaises(ValueError):
            parser._gen_actions_script(incl_hdr=test_incl_hdr, interp=test_interp)

        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")

        # Test what happens if ECL is low enough to cause the SERIOUS event to
        # _not_ raise the ValueError but instead print out a big warning.
        # Setting `exception_control_level` to 2 will cause only CRITICAL events
        # to raise the exception.
        parser.exception_control_level = 2
        test_incl_hdr = True
        test_interp   = "invalid_interpreter"
        rval_expect   = ""
        rval_actual   = parser._gen_actions_script(incl_hdr=test_incl_hdr, interp=test_interp)
        self.assertEqual(rval_expect, rval_actual)
        parser.exception_control_level = 5

        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")

        # Test what happens when there's an action entry that is missing either
        # `envvar` or `module` in its key(). This should throw a ValueError.
        test_incl_hdr = True
        test_interp   = "bash"

        # add a bogus action that is missing either 'envvar' or 'module' from its
        # keys.
        parser.actions.append( {'op': 'envvar_set', 'value': "thevalue", "newkey": "???"} )

        with self.assertRaises(ValueError):
            parser._gen_actions_script(incl_hdr=test_incl_hdr, interp=test_interp)

        # Cleanup: Remove the bogus entry from the actions.
        del parser.actions[-1]

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return


    def test_SetEnvironment_helper_gen_actioncmd_module_badinterp(self):
        """
        Test the ``_gen_actioncmd_module`` command.

        Test that an exception is raised if ``interp`` is sent a bad
        parameter for the interpreter.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 5

        print("-----[ TEST BEGIN ]----------------------------------------")

        operation   = "module_load"
        module_name = "gcc"
        module_ver  = "7.2.0"
        interpreter = "bad interpreter name"
        with self.assertRaises(ValueError):
            parser._gen_actioncmd_module(operation, module_name, module_ver, interp=interpreter)

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return


    def test_SetEnvironment_helper_gen_actioncmd_envvar_badinterp(self):
        """
        Test the ``_gen_actioncmd_envvar`` command

        Test that an exception is raised if ``interp`` is sent a bad
        parameter for the interpreter.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 5

        print("-----[ TEST BEGIN ]----------------------------------------")
        operation   = "envvar_set"
        envvar_name = "FOO"
        envvar_val  = "BAR"
        interpreter = "bad interpreter name"
        with self.assertRaises(ValueError):
            parser._gen_actioncmd_envvar(operation, envvar_name, envvar_val, interp=interpreter)
        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return


    def test_SetEnvironment_helper_gen_actioncmd_envvar_badnumargs(self):
        """
        Test the ``_gen_actioncmd_envvar`` command

        Test what happens if the wrong # of parameters is sent in for commands.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 5

        envvar_name = "FOO"
        envvar_val  = "BAR"
        interpreter = "python"

        print("-----[ TEST BEGIN ]----------------------------------------")
        # envvar_set requires 2 parameters.
        operation   = "envvar_set"
        with self.assertRaises(IndexError):
            parser._gen_actioncmd_envvar(operation, envvar_name, interp=interpreter)
        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")
        # envvar_append requires 2 parameters.
        operation   = "envvar_append"
        with self.assertRaises(IndexError):
            parser._gen_actioncmd_envvar(operation, envvar_name, interp=interpreter)
        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")
        # envvar_prepend requires 2 parameters.
        operation   = "envvar_prepend"
        with self.assertRaises(IndexError):
            parser._gen_actioncmd_envvar(operation, envvar_name, interp=interpreter)
        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")
        # envvar_unset requires 1 parameters.
        operation   = "envvar_unset"
        with self.assertRaises(IndexError):
            parser._gen_actioncmd_envvar(operation, interp=interpreter)
        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return


    def test_SetEnvironment_helper_gen_actioncmd_module_badnumargs(self):
        """
        Test the ``_gen_actioncmd_module`` command

        Test what happens if the wrong # of parameters is sent in for commands.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 5

        module_name = "gcc"
        module_val  = "7.3.0"
        interpreter = "python"

        print("-----[ TEST BEGIN ]----------------------------------------")
        # module_load requires 2 parameters.
        operation = "module_load"
        with self.assertRaises(IndexError):
            parser._gen_actioncmd_module(operation, module_name, interp=interpreter)
        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")
        # module_unload requires 1 parameters.
        operation = "module_unload"
        with self.assertRaises(IndexError):
            parser._gen_actioncmd_module(operation, interp=interpreter)
        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")
        # module_use requires 1 parameters
        operation = "module_use"
        with self.assertRaises(IndexError):
            parser._gen_actioncmd_module(operation, interp=interpreter)
        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")
        # module_swap requires 2 parameters
        operation = "module_swap"
        with self.assertRaises(IndexError):
            parser._gen_actioncmd_module(operation, module_name, interp=interpreter)
        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")
        # module_purge requires 0 parameters
        operation  = "module_purge"
        cmd_expect = 'ModuleHelper.module("purge")'
        cmd_actual = parser._gen_actioncmd_module(operation, interp=interpreter)
        self.assertEqual(cmd_expect, cmd_actual)
        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return


    def test_SetEnvironment_helper_remove_prefix(self):
        """
        Test the ``_remove_prefix`` method.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 5

        print("-----[ TEST BEGIN ]----------------------------------------")
        text        = "envvar_use"
        prefix      = "envvar_"
        rval_expect = "use"
        rval_actual = parser._remove_prefix(text, prefix)
        self.assertEqual(rval_expect, rval_actual)
        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")
        text        = "envvar_use"
        prefix      = "varuse"
        rval_expect = "envvar_use"
        rval_actual = parser._remove_prefix(text, prefix)
        self.assertEqual(rval_expect, rval_actual)
        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")
        text        = None
        prefix      = "envvar_"
        rval_expect = "envvar_use"
        with self.assertRaises(TypeError):
            rval_actual = parser._remove_prefix(text, prefix)
            self.assertEqual(rval_expect, rval_actual)
        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")
        text        = "envvar_use"
        prefix      = None
        rval_expect = "envvar_use"
        with self.assertRaises(TypeError):
            rval_actual = parser._remove_prefix(text, prefix)
            self.assertEqual(rval_expect, rval_actual)
        print("-----[ TEST END ]------------------------------------------")


        print("OK")
        return


    def test_SetEnvironment_handler_envvar_remove_substr(self):
        """
        Test the ``envvar_remove_substr`` handler.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 5

        print("-----[ TEST BEGIN ]----------------------------------------")

        section = "ENVVAR_REMOVE_SUBSTR_TEST"
        print("Section  : {}".format(section))

        # parse a section
        data = parser.parse_section(section)

        # Pretty print the actions (unchecked)
        print("")
        parser.pretty_print_actions()

        parser.apply()
        parser.pretty_print_envvars(envvar_filter=["FOO"], filtered_keys_only=True)

        envvar_foo_expect = "BB"
        envvar_foo_actual = os.environ["FOO"]

        self.assertEqual(envvar_foo_expect, envvar_foo_actual)

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return


    def test_SetEnvironment_handler_envvar_remove_substr_envvar_missing(self):
        """
        Test the ``envvar_remove_substr`` handler when the envvar is missing / unset.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 5

        print("-----[ TEST BEGIN ]----------------------------------------")

        section = "ENVVAR_REMOVE_SUBSTR_TEST_NO_ENVVAR"
        print("Section  : {}".format(section))

        # parse a section
        data = parser.parse_section(section)

        # Pretty print the actions (unchecked)
        print("")
        parser.pretty_print_actions()

        parser.apply()
        parser.pretty_print_envvars(envvar_filter=["FOO"], filtered_keys_only=True)

        self.assertTrue("FOO" not in os.environ.keys())

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return


    def test_SetEnvironment_handler_envvar_remove_path_entry(self):
        """
        Test the ``envvar_remove_path_entry`` handler.
        """
        print("\n")
        print("Load file: {}".format(self._filename))

        parser = SetEnvironment(self._filename)
        parser.debug_level = 5


        section = "ENVVAR_REMOVE_PATH_ENTRY_TEST"
        print("Section  : {}".format(section))

        # parse a section
        data = parser.parse_section(section)

        # Pretty print the actions (unchecked)
        print("")
        parser.pretty_print_actions()

        parser.apply()

        print("-----[ TEST BEGIN ]----------------------------------------")
        parser.pretty_print_envvars(envvar_filter=["TEST_PATH1"], filtered_keys_only=True)
        envvar_expect = os.pathsep.join(["/foo", "/bar/baz", "/bif"])
        envvar_actual = os.environ["TEST_PATH1"]
        self.assertEqual(envvar_expect, envvar_actual)
        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")
        parser.pretty_print_envvars(envvar_filter=["TEST_PATH2"], filtered_keys_only=True)
        envvar_expect = os.pathsep.join(["/foo", "/bar", "/bar/baz", "/bar", "/bif"])
        envvar_actual = os.environ["TEST_PATH2"]
        self.assertEqual(envvar_expect, envvar_actual)
        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")
        parser.pretty_print_envvars(envvar_filter=["TEST_PATH3"], filtered_keys_only=True)
        envvar_expect = os.pathsep.join(["/foo", "/bar", "/bar", "/bif"])
        envvar_actual = os.environ["TEST_PATH3"]
        self.assertEqual(envvar_expect, envvar_actual)
        print("-----[ TEST END ]------------------------------------------")

        print("OK")
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

        filename_out_truth = os.path.sep.join([self.unit_test_path,"_apply_configuration_truth.sh"])
        filename_out_test  = os.path.sep.join([self.unit_test_path,"___apply_configuration_test.sh"])
        include_header = True
        interpreter  = "bash"
        rval_expect  = 0
        rval_actual  = parser.write_actions_to_file(filename_out_test, include_header, interpreter)

        self.assertEqual(rval_expect, rval_actual)
        self.assertTrue(filecmp.cmp(filename_out_truth, filename_out_test))

        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")

        filename_out_truth = os.path.sep.join([self.unit_test_path,"_apply_configuration_nohdr_truth.sh"])
        filename_out_test  = os.path.sep.join([self.unit_test_path,"___apply_configuration_nohdr_test.sh"])
        include_header = False
        interpreter  = "bash"
        rval_expect  = 0
        rval_actual  = parser.write_actions_to_file(filename_out_test, include_header, interpreter)

        self.assertEqual(rval_expect, rval_actual)
        self.assertTrue(filecmp.cmp(filename_out_truth, filename_out_test))

        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")

        filename_out = "___apply_configuration_nowrite_01.sh"
        include_header = True
        interpreter  = "undefined interpreter"
        rval_expect  = 0
        with self.assertRaises(ValueError):
            rval_actual  = parser.write_actions_to_file(filename_out, include_header, interpreter)
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

        filename_out_truth = os.path.sep.join([self.unit_test_path,"_apply_configuration_truth.py"])
        filename_out_test  = os.path.sep.join([self.unit_test_path,"___apply_configuration_test.py"])
        include_header = True
        interpreter  = "python"
        rval_expect  = 0

        rval_actual  = parser.write_actions_to_file(filename_out_test, include_header, interpreter)

        self.assertEqual(rval_expect, rval_actual)
        self.assertTrue(filecmp.cmp(filename_out_truth, filename_out_test))


        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")

        filename_out_truth = os.path.sep.join([self.unit_test_path,"_apply_configuration_nohdr_truth.py"])
        filename_out_test  = os.path.sep.join([self.unit_test_path,"___apply_configuration_nohdr_test.py"])
        include_header = False
        interpreter  = "python"
        rval_expect  = 0

        rval_actual  = parser.write_actions_to_file(filename_out_test, include_header, interpreter)

        self.assertEqual(rval_expect, rval_actual)
        self.assertTrue(filecmp.cmp(filename_out_truth, filename_out_test))

        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")

        filename_out = "___apply_configuration_nowrite_01.py"
        include_header = True
        interpreter  = "undefined interpreter"
        rval_expect  = 0

        with self.assertRaises(ValueError):
            rval_actual  = parser.write_actions_to_file(filename_out, include_header, interpreter)
            self.assertEqual(rval_expect, rval_actual)

        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")

        filename_out = "___apply_configuration_nowrite_02.py"
        include_header = True
        interpreter  = "undefined interpreter"
        rval_expect  = 1

        parser.exception_control_level = 2

        rval_actual  = parser.write_actions_to_file(filename_out, include_header, interpreter)
        self.assertEqual(rval_expect, rval_actual)

        print("-----[ TEST END ]------------------------------------------")
        print("OK")
        return


    def test_SetEnvironment_freefunc_envvar_assign(self):
        """
        Test the free-function ``envvar_assign``
        """
        print("\n")
        print("-----[ TEST BEGIN ]----------------------------------------")

        with self.assertRaises(TypeError):
            envvar_assign(None, "BAR")

        with self.assertRaises(TypeError):
            envvar_assign("FOO", None)

        with self.assertRaises(TypeError):
            envvar_assign("FOO", "BAR", None)

        envvar_assign("FOO", "", True)
        self.assertEqual("", os.environ["FOO"])
        del os.environ["FOO"]

        with self.assertRaises(ValueError):
            envvar_assign("FOO", "", False)

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
