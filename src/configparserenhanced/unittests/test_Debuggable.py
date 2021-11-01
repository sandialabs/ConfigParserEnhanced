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

from configparserenhanced import Debuggable

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



class DebuggableTest(TestCase):
    """
    Main test driver for the SetEnvironment class
    """

    def setUp(self):
        print("")
        return

    def test_Debuggable_property_debug_level(self):
        """
        Test reading and setting the property `debug_level`
        """

        class testme(Debuggable):

            def __init__(self):
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
        return 0

    def test_Debuggable_method_debug_message(self):

        class testme(Debuggable):

            def __init__(self):
                pass
                return

        inst_testme = testme()

        message = "This is a test message!"

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.debug_message(0, message, end="\n")
            self.assertEqual(fake_out.getvalue(), message + "\n")

        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.debug_message(1, message, end="\n")
            self.assertEqual(fake_out.getvalue(), "")

        inst_testme.debug_level = 3
        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.debug_message(3, message, end="\n")
            self.assertEqual(fake_out.getvalue(), "[D-3] " + message + "\n")

        inst_testme.debug_level = 2
        with patch('sys.stdout', new=StringIO()) as fake_out:
            inst_testme.debug_message(0, "A", end="", useprefix=False)
            inst_testme.debug_message(1, "B", end="", useprefix=False)
            inst_testme.debug_message(2, "C", end="", useprefix=False)
            inst_testme.debug_message(3, "D", end="", useprefix=False)
            inst_testme.debug_message(4, "E", end="", useprefix=False)
            self.assertEqual(fake_out.getvalue(), "ABC")

        print("OK")
        return 0



# EOF
