#!/usr/bin/env python
# -*- coding: utf-8; mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
"""
from __future__ import print_function

import sys
sys.dont_write_bytecode = True

import os
sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

from configparser_enhanced import ExceptionControl



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

class ExceptionControlTest(TestCase):
    """
    Main test driver for the SetEnvironment class
    """
    def setUp(self):
        print("")



    def test_ExceptionControl_property_exception_control_level(self):
        """
        Test reading and setting the property `exception_control_level`
        """
        class testme(ExceptionControl):
            def __init__(self):
                pass
                return

        inst_testme = testme()

        # Test default value (2)

        # Test value -1 (bad value should default to 0)
        inst_testme.exception_control_level = -1
        self.assertEqual(inst_testme.exception_control_level, 0)

        # Test value 0
        inst_testme.exception_control_level =  0
        self.assertEqual(inst_testme.exception_control_level, 0)

        # Test value 1
        inst_testme.exception_control_level =  1
        self.assertEqual(inst_testme.exception_control_level, 1)

        # Test value 2
        inst_testme.exception_control_level =  2
        self.assertEqual(inst_testme.exception_control_level, 2)

        # Test value 3
        inst_testme.exception_control_level =  3
        self.assertEqual(inst_testme.exception_control_level, 3)

        # Test value 4
        inst_testme.exception_control_level =  4
        self.assertEqual(inst_testme.exception_control_level, 4)

        # Test value 5
        inst_testme.exception_control_level =  5
        self.assertEqual(inst_testme.exception_control_level, 5)

        # Test value 6 (bad value should default to 5)
        inst_testme.exception_control_level =  6
        self.assertEqual(inst_testme.exception_control_level, 5)

        print("OK")



    def test_ExceptionControl_method_exception_control_event(self):

        class testme(ExceptionControl):
            def __init__(self):
                pass
                return

            def event_warning(self):
                inst_testme.exception_control_event("WARNING", ValueError, message="message text")

            def event_minor(self):
                inst_testme.exception_control_event("MINOR", ValueError, message="message text")

            def event_serious(self):
                inst_testme.exception_control_event("SERIOUS", ValueError, message="message text")

            def event_critical(self):
                inst_testme.exception_control_event("CRITICAL", ValueError, message="message text")

            def event_warning_nomsg(self):
                inst_testme.exception_control_event("WARNING", ValueError, message="message text")

            def event_minor_nomsg(self):
                inst_testme.exception_control_event("MINOR", ValueError, message="message text")

            def event_serious_nomsg(self):
                inst_testme.exception_control_event("SERIOUS", ValueError, message="message text")

            def event_critical_nomsg(self):
                inst_testme.exception_control_event("CRITICAL", ValueError, message="message text")



        inst_testme = testme()

        # Default exception_control_level == 2
        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_warning()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_minor()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_serious()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())

        with self.assertRaises(ValueError):
            inst_testme.event_critical()


        # Set exception_control_level = 0 (Silent Running)
        inst_testme.exception_control_level = 0
        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_warning()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_minor()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_serious()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_critical()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())


        # Set exception_control_level = 1 (Warnings for all, do not raise exceptions.)
        inst_testme.exception_control_level = 1
        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_warning()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_minor()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_serious()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_critical()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())


        # Set exception_control_level = 2 (raise CRITICAL)
        inst_testme.exception_control_level = 2
        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_warning()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_minor()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_serious()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())


        # Set exception_control_level = 3 (raise CRITICAL, SERIOUS)
        inst_testme.exception_control_level = 3
        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_warning()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_minor()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())

        with self.assertRaises(ValueError):
            inst_testme.event_serious()

        with self.assertRaises(ValueError):
            inst_testme.event_critical()


        # Set exception_control_level = 4 (raise CRITICAL, SERIOUS, MINOR)
        inst_testme.exception_control_level = 4
        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_warning()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())

        with self.assertRaises(ValueError):
            inst_testme.event_minor()

        with self.assertRaises(ValueError):
            inst_testme.event_serious()

        with self.assertRaises(ValueError):
            inst_testme.event_critical()


        # Set exception_control_level = 5 (raise ALL)
        inst_testme.exception_control_level = 5
        with self.assertRaises(ValueError):
            inst_testme.event_warning()

        with self.assertRaises(ValueError):
            inst_testme.event_minor()

        with self.assertRaises(ValueError):
            inst_testme.event_serious()

        with self.assertRaises(ValueError):
            inst_testme.event_critical()


        print("OK")


    def test_ExceptionControl_method_exception_control_event(self):

        class testme(ExceptionControl):
            def __init__(self):
                pass
                return

            def event_warning(self):
                inst_testme.exception_control_event("WARNING", ValueError, message="message text")

            def event_minor(self):
                inst_testme.exception_control_event("MINOR", ValueError, message="message text")

            def event_serious(self):
                inst_testme.exception_control_event("SERIOUS", ValueError, message="message text")

            def event_critical(self):
                inst_testme.exception_control_event("CRITICAL", ValueError, message="message text")

            def event_warning_nomsg(self):
                inst_testme.exception_control_event("WARNING", ValueError, message="message text")

            def event_minor_nomsg(self):
                inst_testme.exception_control_event("MINOR", ValueError, message="message text")

            def event_serious_nomsg(self):
                inst_testme.exception_control_event("SERIOUS", ValueError, message="message text")

            def event_critical_nomsg(self):
                inst_testme.exception_control_event("CRITICAL", ValueError, message="message text")



        inst_testme = testme()

        # Default exception_control_level == 2
        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_warning()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_minor()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_serious()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())

        with self.assertRaises(ValueError):
            inst_testme.event_critical()


        # Set exception_control_level = 0 (Silent Running)
        inst_testme.exception_control_level = 0
        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_warning()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_minor()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_serious()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_critical()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())


        # Set exception_control_level = 1 (Warnings for all, do not raise exceptions.)
        inst_testme.exception_control_level = 1
        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_warning()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_minor()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_serious()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_critical()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())


        # Set exception_control_level = 2 (raise CRITICAL)
        inst_testme.exception_control_level = 2
        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_warning()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_minor()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_serious()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())


        # Set exception_control_level = 3 (raise CRITICAL, SERIOUS)
        inst_testme.exception_control_level = 3
        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_warning()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_minor()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())

        with self.assertRaises(ValueError):
            inst_testme.event_serious()

        with self.assertRaises(ValueError):
            inst_testme.event_critical()


        # Set exception_control_level = 4 (raise CRITICAL, SERIOUS, MINOR)
        inst_testme.exception_control_level = 4
        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.event_warning()
            print(fake_out.getvalue())
            self.assertIn("EXCEPTION SKIPPED:", fake_out.getvalue())

        with self.assertRaises(ValueError):
            inst_testme.event_minor()

        with self.assertRaises(ValueError):
            inst_testme.event_serious()

        with self.assertRaises(ValueError):
            inst_testme.event_critical()


        # Set exception_control_level = 5 (raise ALL)
        inst_testme.exception_control_level = 5
        with self.assertRaises(ValueError):
            inst_testme.event_warning()

        with self.assertRaises(ValueError):
            inst_testme.event_minor()

        with self.assertRaises(ValueError):
            inst_testme.event_serious()

        with self.assertRaises(ValueError):
            inst_testme.event_critical()


        print("OK")



# EOF



