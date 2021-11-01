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

from configparserenhanced import ExceptionControl
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



class ExceptionControlTest(TestCase):
    """
    Main test driver for the SetEnvironment class
    """

    def setUp(self):
        print("")
        return

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
        inst_testme.exception_control_level = 0
        self.assertEqual(inst_testme.exception_control_level, 0)

        # Test value 1
        inst_testme.exception_control_level = 1
        self.assertEqual(inst_testme.exception_control_level, 1)

        # Test value 2
        inst_testme.exception_control_level = 2
        self.assertEqual(inst_testme.exception_control_level, 2)

        # Test value 3
        inst_testme.exception_control_level = 3
        self.assertEqual(inst_testme.exception_control_level, 3)

        # Test value 4
        inst_testme.exception_control_level = 4
        self.assertEqual(inst_testme.exception_control_level, 4)

        # Test value 5
        inst_testme.exception_control_level = 5
        self.assertEqual(inst_testme.exception_control_level, 5)

        # Test value 6 (bad value should default to 5)
        inst_testme.exception_control_level = 6
        self.assertEqual(inst_testme.exception_control_level, 5)

        print("OK")
        return 0

    def test_ExceptionControl_method_exception_control_event(self):

        class testme(ExceptionControl):

            def __init__(self):
                pass
                return

            def event_silent(self):
                inst_testme.exception_control_event("SILENT", ValueError, message="message text")

            def event_warning(self):
                inst_testme.exception_control_event("WARNING", ValueError, message="message text")

            def event_minor(self):
                inst_testme.exception_control_event("MINOR", ValueError, message="message text")

            def event_serious(self):
                inst_testme.exception_control_event("SERIOUS", ValueError, message="message text")

            def event_critical(self):
                inst_testme.exception_control_event("CRITICAL", ValueError, message="message text")

            def event_catastrophic(self):
                inst_testme.exception_control_event("CATASTROPHIC", ValueError, message="message text")

        inst_testme = testme()

        exception_skipped_msg_regex_01 = r"!! EXCEPTION SKIPPED"
        exception_skipped_msg_regex_02 = r"Message\s*:"

        # Default exception_control_level == 4
        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_warning()
            print(fake_out.getvalue())
            self.assertIn(exception_skipped_msg_regex_01, fake_out.getvalue())

        with self.assertRaises(ValueError):
            inst_testme.event_minor()

        with self.assertRaises(ValueError):
            inst_testme.event_serious()

        with self.assertRaises(ValueError):
            inst_testme.event_critical()

        with self.assertRaises(ValueError):
            inst_testme.event_critical()

        # Set exception_control_level = 0 (Silent Running)
        inst_testme.exception_control_level = 0
        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_silent()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_warning()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_minor()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_serious()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_critical()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with self.assertRaises(ValueError):
            inst_testme.event_catastrophic()

        # Set exception_control_level = 1 (Warnings for all, do not raise exceptions.)
        inst_testme.exception_control_level = 1
        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_silent()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_warning()
            print(fake_out.getvalue())
            self.assertRegex(fake_out.getvalue(), exception_skipped_msg_regex_01)
            self.assertRegex(fake_out.getvalue(), exception_skipped_msg_regex_02)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_minor()
            print(fake_out.getvalue())
            self.assertRegex(fake_out.getvalue(), exception_skipped_msg_regex_01)
            self.assertRegex(fake_out.getvalue(), exception_skipped_msg_regex_02)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_serious()
            print(fake_out.getvalue())
            self.assertRegex(fake_out.getvalue(), exception_skipped_msg_regex_01)
            self.assertRegex(fake_out.getvalue(), exception_skipped_msg_regex_02)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_critical()
            print(fake_out.getvalue())
            self.assertRegex(fake_out.getvalue(), exception_skipped_msg_regex_01)
            self.assertRegex(fake_out.getvalue(), exception_skipped_msg_regex_02)

        with self.assertRaises(ValueError):
            inst_testme.event_catastrophic()

        # Set exception_control_level = 2 (raise CRITICAL)
        inst_testme.exception_control_level = 2
        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_silent()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_warning()
            print(fake_out.getvalue())
            self.assertRegex(fake_out.getvalue(), exception_skipped_msg_regex_01)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_minor()
            print(fake_out.getvalue())
            self.assertRegex(fake_out.getvalue(), exception_skipped_msg_regex_01)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_serious()
            print(fake_out.getvalue())
            self.assertRegex(fake_out.getvalue(), exception_skipped_msg_regex_01)

        with self.assertRaises(ValueError):
            inst_testme.event_critical()

        # Set exception_control_level = 3 (raise CRITICAL, SERIOUS)
        inst_testme.exception_control_level = 3
        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_silent()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_warning()
            print(fake_out.getvalue())
            self.assertRegex(fake_out.getvalue(), exception_skipped_msg_regex_01)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_minor()
            print(fake_out.getvalue())
            self.assertRegex(fake_out.getvalue(), exception_skipped_msg_regex_01)

        with self.assertRaises(ValueError):
            inst_testme.event_serious()

        with self.assertRaises(ValueError):
            inst_testme.event_critical()

        with self.assertRaises(ValueError):
            inst_testme.event_catastrophic()

        # Set exception_control_level = 4 (raise CRITICAL, SERIOUS, MINOR)
        inst_testme.exception_control_level = 4
        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_silent()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_warning()
            print(fake_out.getvalue())
            self.assertRegex(fake_out.getvalue(), exception_skipped_msg_regex_01)

        with self.assertRaises(ValueError):
            inst_testme.event_minor()

        with self.assertRaises(ValueError):
            inst_testme.event_serious()

        with self.assertRaises(ValueError):
            inst_testme.event_critical()

        with self.assertRaises(ValueError):
            inst_testme.event_catastrophic()

        # Set exception_control_level = 5 (raise ALL)
        inst_testme.exception_control_level = 5
        with self.assertRaises(ValueError):
            inst_testme.event_silent()

        with self.assertRaises(ValueError):
            inst_testme.event_warning()

        with self.assertRaises(ValueError):
            inst_testme.event_minor()

        with self.assertRaises(ValueError):
            inst_testme.event_serious()

        with self.assertRaises(ValueError):
            inst_testme.event_critical()

        with self.assertRaises(ValueError):
            inst_testme.event_catastrophic()

        print("OK")
        return 0

    def test_ExceptionControl_method_exception_control_event_nomsg(self):

        class testme(ExceptionControl):

            def __init__(self):
                return

            def event_silent_nomsg(self):
                inst_testme.exception_control_event("SILENT", ValueError)

            def event_warning_nomsg(self):
                inst_testme.exception_control_event("WARNING", ValueError)

            def event_minor_nomsg(self):
                inst_testme.exception_control_event("MINOR", ValueError)

            def event_serious_nomsg(self):
                inst_testme.exception_control_event("SERIOUS", ValueError)

            def event_critical_nomsg(self):
                inst_testme.exception_control_event("CRITICAL", ValueError)

            def event_catastrophic_nomsg(self):
                inst_testme.exception_control_event("CATASTROPHIC", ValueError)

        inst_testme = testme()

        # Set exception_control_level = 1 (Warnings for all, do not raise exceptions.)
        inst_testme.exception_control_level = 1
        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_silent_nomsg()
            print(fake_out.getvalue())
            self.assertNotIn("Message:", fake_out.getvalue())

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_warning_nomsg()
            print(fake_out.getvalue())
            self.assertNotIn("Message:", fake_out.getvalue())

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_minor_nomsg()
            print(fake_out.getvalue())
            self.assertNotIn("Message:", fake_out.getvalue())

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_serious_nomsg()
            print(fake_out.getvalue())
            self.assertNotIn("Message:", fake_out.getvalue())

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_critical_nomsg()
            print(fake_out.getvalue())
            self.assertNotIn("Message:", fake_out.getvalue())

        with self.assertRaises(ValueError):
            inst_testme.event_catastrophic_nomsg()

        # Set exception_control_level = 5 (raise ALL)
        inst_testme.exception_control_level = 5
        with self.assertRaises(ValueError):
            inst_testme.event_silent_nomsg()

        with self.assertRaises(ValueError):
            inst_testme.event_warning_nomsg()

        with self.assertRaises(ValueError):
            inst_testme.event_minor_nomsg()

        with self.assertRaises(ValueError):
            inst_testme.event_serious_nomsg()

        with self.assertRaises(ValueError):
            inst_testme.event_critical_nomsg()

        with self.assertRaises(ValueError):
            inst_testme.event_catastrophic_nomsg()

        print("OK")
        return 0

    def test_ExceptionControl_method_exception_control_event_badexception(self):

        class testme(ExceptionControl):

            def __init__(self):
                pass
                return

            def event_silent(self):
                inst_testme.exception_control_event("SILENT", int, message="message text")

            def event_warning(self):
                inst_testme.exception_control_event("WARNING", int, message="message text")

            def event_minor(self):
                inst_testme.exception_control_event("MINOR", None, message="message text")

            def event_serious(self):
                inst_testme.exception_control_event("SERIOUS", float, message="message text")

            def event_critical(self):
                inst_testme.exception_control_event("CRITICAL", None, message="message text")

            def event_catastrophic(self):
                inst_testme.exception_control_event("CATASTROPHIC", None, message="message text")

        inst_testme = testme()

        for level in range(6):
            inst_testme.exception_control_level = level
            with self.assertRaises(TypeError):
                inst_testme.event_silent()

            with self.assertRaises(TypeError):
                inst_testme.event_warning()

            with self.assertRaises(TypeError):
                inst_testme.event_minor()

            with self.assertRaises(TypeError):
                inst_testme.event_serious()

            with self.assertRaises(TypeError):
                inst_testme.event_critical()

            with self.assertRaises(TypeError):
                inst_testme.event_catastrophic()

        print("OK")
        return

    def test_ExceptionControl_method_exception_control_event_silent_warnings(self):

        class testme(ExceptionControl):

            def __init__(self):
                pass
                return

            def event_silent(self):
                inst_testme.exception_control_event("SILENT", ValueError, message="message text")

            def event_warning(self):
                inst_testme.exception_control_event("WARNING", ValueError, message="message text")

            def event_minor(self):
                inst_testme.exception_control_event("MINOR", ValueError, message="message text")

            def event_serious(self):
                inst_testme.exception_control_event("SERIOUS", ValueError, message="message text")

            def event_critical(self):
                inst_testme.exception_control_event("CRITICAL", ValueError, message="message text")

            def event_catastrophic(self):
                inst_testme.exception_control_event("CATASTROPHIC", ValueError, message="message text")

        inst_testme = testme()

        # Check that we raise the typeerror if the assignment isn't a bool
        with self.assertRaises(TypeError):
            inst_testme.exception_control_silent_warnings = None

        # Enable warning suppression
        inst_testme.exception_control_silent_warnings = True

        # Default exception_control_level == 4
        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_silent()
            output_expect = ""
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(output_expect, output_actual)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_warning()
            output_expect = ""
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(output_expect, output_actual)

        with self.assertRaises(ValueError):
            inst_testme.event_minor()

        with self.assertRaises(ValueError):
            inst_testme.event_serious()

        with self.assertRaises(ValueError):
            inst_testme.event_critical()

        with self.assertRaises(ValueError):
            inst_testme.event_catastrophic()

        # Set exception_control_level = 0 (Silent Running)
        inst_testme.exception_control_level = 0
        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_silent()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_warning()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_minor()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_serious()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_critical()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with self.assertRaises(ValueError):
            inst_testme.event_catastrophic()

        # Set exception_control_level = 1 (Warnings for all, do not raise exceptions.)
        inst_testme.exception_control_level = 1
        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_silent()
            output_expect = ""
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(output_expect, output_actual)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_warning()
            output_expect = ""
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(output_expect, output_actual)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_minor()
            output_expect = ""
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(output_expect, output_actual)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_serious()
            output_expect = ""
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(output_expect, output_actual)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_critical()
            output_expect = ""
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(output_expect, output_actual)

        with self.assertRaises(ValueError):
            inst_testme.event_catastrophic()

        # Set exception_control_level = 2 (raise CRITICAL)
        inst_testme.exception_control_level = 2
        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_silent()
            output_expect = ""
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(output_expect, output_actual)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_warning()
            output_expect = ""
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(output_expect, output_actual)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_minor()
            output_expect = ""
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(output_expect, output_actual)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_serious()
            output_expect = ""
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(output_expect, output_actual)

        with self.assertRaises(ValueError):
            inst_testme.event_critical()

        with self.assertRaises(ValueError):
            inst_testme.event_catastrophic()

        # Set exception_control_level = 3 (raise CRITICAL, SERIOUS)
        inst_testme.exception_control_level = 3
        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_silent()
            output_expect = ""
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(output_expect, output_actual)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_warning()
            output_expect = ""
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(output_expect, output_actual)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_minor()
            output_expect = ""
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(output_expect, output_actual)

        with self.assertRaises(ValueError):
            inst_testme.event_serious()

        with self.assertRaises(ValueError):
            inst_testme.event_critical()

        with self.assertRaises(ValueError):
            inst_testme.event_catastrophic()

        # Set exception_control_level = 4 (raise CRITICAL, SERIOUS, MINOR)
        inst_testme.exception_control_level = 4
        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_silent()
            output_expect = ""
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(output_expect, output_actual)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_warning()
            output_expect = ""
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(output_expect, output_actual)

        with self.assertRaises(ValueError):
            inst_testme.event_minor()

        with self.assertRaises(ValueError):
            inst_testme.event_serious()

        with self.assertRaises(ValueError):
            inst_testme.event_critical()

        with self.assertRaises(ValueError):
            inst_testme.event_catastrophic()

        # Set exception_control_level = 5 (raise ALL)
        inst_testme.exception_control_level = 5
        with self.assertRaises(ValueError):
            inst_testme.event_silent()

        with self.assertRaises(ValueError):
            inst_testme.event_warning()

        with self.assertRaises(ValueError):
            inst_testme.event_minor()

        with self.assertRaises(ValueError):
            inst_testme.event_serious()

        with self.assertRaises(ValueError):
            inst_testme.event_critical()

        with self.assertRaises(ValueError):
            inst_testme.event_catastrophic()

        print("OK")
        return 0

    def test_ExceptionControl_method_exception_control_event_compact_warnings(self):

        class testme(ExceptionControl):

            def __init__(self):
                pass
                return

            def event_silent(self):
                inst_testme.exception_control_event("SILENT", ValueError, message="message text")

            def event_warning(self):
                inst_testme.exception_control_event("WARNING", ValueError, message="message text")

            def event_minor(self):
                inst_testme.exception_control_event("MINOR", ValueError, message="message text")

            def event_serious(self):
                inst_testme.exception_control_event("SERIOUS", ValueError, message="message text")

            def event_critical(self):
                inst_testme.exception_control_event("CRITICAL", ValueError, message="message text")

            def event_catastrophic(self):
                inst_testme.exception_control_event("CATASTROPHIC", ValueError, message="message text")

        inst_testme = testme()

        # Check that we raise the typeerror if the assignment isn't a bool
        with self.assertRaises(TypeError):
            inst_testme.exception_control_compact_warnings = None

        # Enable warning suppression
        inst_testme.exception_control_compact_warnings = True

        exception_msg_regex_01 = r"!! EXCEPTION SKIPPED \(WARNING : ValueError\)"
        exception_msg_regex_02 = r"!! EXCEPTION SKIPPED \(MINOR : ValueError\)"
        exception_msg_regex_03 = r"!! EXCEPTION SKIPPED \(SERIOUS : ValueError\)"
        exception_msg_regex_04 = r"!! EXCEPTION SKIPPED \(CRITICAL : ValueError\)"

        # Default exception_control_level == 4
        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_warning()
            output_expect = ""
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(1, len(output_actual.splitlines()))
            self.assertRegex(output_actual, exception_msg_regex_01)

        with self.assertRaises(ValueError):
            inst_testme.event_minor()

        with self.assertRaises(ValueError):
            inst_testme.event_serious()

        with self.assertRaises(ValueError):
            inst_testme.event_critical()

        with self.assertRaises(ValueError):
            inst_testme.event_catastrophic()

        # Set exception_control_level = 0 (Silent Running)
        inst_testme.exception_control_level = 0
        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_silent()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_warning()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_minor()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_serious()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_critical()
            print(fake_out.getvalue())
            self.assertEqual("", fake_out.getvalue().rstrip())

        with self.assertRaises(ValueError):
            inst_testme.event_catastrophic()

        # Set exception_control_level = 1 (Warnings for all, do not raise exceptions.)
        inst_testme.exception_control_level = 1
        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_silent()
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(0, len(output_actual.splitlines()))

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_warning()
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(1, len(output_actual.splitlines()))
            self.assertRegex(output_actual, exception_msg_regex_01)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_minor()
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(1, len(output_actual.splitlines()))
            self.assertRegex(output_actual, exception_msg_regex_02)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_serious()
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(1, len(output_actual.splitlines()))
            self.assertRegex(output_actual, exception_msg_regex_03)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_critical()
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(1, len(output_actual.splitlines()))
            self.assertRegex(output_actual, exception_msg_regex_04)

        with self.assertRaises(ValueError):
            inst_testme.event_catastrophic()

        # Set exception_control_level = 2 (raise CRITICAL)
        inst_testme.exception_control_level = 2
        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_silent()
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(0, len(output_actual.splitlines()))

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_warning()
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(1, len(output_actual.splitlines()))
            self.assertRegex(output_actual, exception_msg_regex_01)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_minor()
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(1, len(output_actual.splitlines()))
            self.assertRegex(output_actual, exception_msg_regex_02)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_serious()
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(1, len(output_actual.splitlines()))
            self.assertRegex(output_actual, exception_msg_regex_03)

        with self.assertRaises(ValueError):
            inst_testme.event_critical()

        with self.assertRaises(ValueError):
            inst_testme.event_catastrophic()

        # Set exception_control_level = 3 (raise CRITICAL, SERIOUS)
        inst_testme.exception_control_level = 3
        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_silent()
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(0, len(output_actual.splitlines()))

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_warning()
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(1, len(output_actual.splitlines()))
            self.assertRegex(output_actual, exception_msg_regex_01)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_minor()
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(1, len(output_actual.splitlines()))
            self.assertRegex(output_actual, exception_msg_regex_02)

        with self.assertRaises(ValueError):
            inst_testme.event_serious()

        with self.assertRaises(ValueError):
            inst_testme.event_critical()

        with self.assertRaises(ValueError):
            inst_testme.event_catastrophic()

        # Set exception_control_level = 4 (raise CRITICAL, SERIOUS, MINOR)
        inst_testme.exception_control_level = 4
        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_silent()
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(0, len(output_actual.splitlines()))

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.event_warning()
            output_actual = fake_out.getvalue().strip()
            print(output_actual)
            self.assertEqual(1, len(output_actual.splitlines()))
            self.assertRegex(output_actual, exception_msg_regex_01)

        with self.assertRaises(ValueError):
            inst_testme.event_minor()

        with self.assertRaises(ValueError):
            inst_testme.event_serious()

        with self.assertRaises(ValueError):
            inst_testme.event_critical()

        with self.assertRaises(ValueError):
            inst_testme.event_catastrophic()

        # Set exception_control_level = 5 (raise ALL)
        inst_testme.exception_control_level = 5
        with self.assertRaises(ValueError):
            inst_testme.event_silent()

        with self.assertRaises(ValueError):
            inst_testme.event_warning()

        with self.assertRaises(ValueError):
            inst_testme.event_minor()

        with self.assertRaises(ValueError):
            inst_testme.event_serious()

        with self.assertRaises(ValueError):
            inst_testme.event_critical()

        with self.assertRaises(ValueError):
            inst_testme.event_catastrophic()

        print("OK")
        return 0



# EOF
