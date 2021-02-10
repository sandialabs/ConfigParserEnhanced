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

from configparserenhanced import Debuggable



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

class DebuggableTest(TestCase):
    """
    Main test driver for the SetEnvironment class
    """
    def setUp(self):
        print("")



    def test_Debuggable_property_debug_level(self):
        """
        Test reading and setting the property `debug_level`
        """
        class testme(Debuggable):
            def __init__(self):
                pass
                return

        inst_testme = testme()

        self.assertEqual(0, inst_testme.debug_level)

        inst_testme.debug_level = 1
        self.assertEqual(1, inst_testme.debug_level)

        inst_testme.debug_level = 5
        self.assertEqual(5, inst_testme.debug_level)

        inst_testme.debug_level = 100
        self.assertEqual(100, inst_testme.debug_level)

        inst_testme.debug_level = 0
        self.assertEqual(0, inst_testme.debug_level)

        inst_testme.debug_level = -1
        self.assertEqual(0, inst_testme.debug_level)

        print("OK")


    def test_Debuggable_method_debug_message(self):

        class testme(Debuggable):
            def __init__(self):
                pass
                return

        inst_testme = testme()

        message = "This is a test message!"

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.debug_message(0, message, end="\n")
            self.assertEqual(fake_out.getvalue(), message + "\n")

        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.debug_message(1, message, end="\n")
            self.assertEqual(fake_out.getvalue(), "")

        inst_testme.debug_level = 3
        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.debug_message(3, message, end="\n")
            self.assertEqual(fake_out.getvalue(), "[D-3] "+message+"\n")

        inst_testme.debug_level = 2
        with patch('sys.stdout', new = StringIO()) as fake_out:
            inst_testme.debug_message(0, "A", end="", useprefix=False)
            inst_testme.debug_message(1, "B", end="", useprefix=False)
            inst_testme.debug_message(2, "C", end="", useprefix=False)
            inst_testme.debug_message(3, "D", end="", useprefix=False)
            inst_testme.debug_message(4, "E", end="", useprefix=False)
            self.assertEqual(fake_out.getvalue(), "ABC")

        print("OK")





# EOF
