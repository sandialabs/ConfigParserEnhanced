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

from configparserenhanced.TypedProperty import typed_property

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



class TypedPropertyTest(TestCase):
    """
    Main test driver for TypedProperty testing
    """

    def setUp(self):
        print("")
        return 0

    def test_TypedProperty_typed_propertry_with_default(self):
        """
        Test a typed_property with a default
        """

        class TestClass(object):
            data = typed_property("data", expected_type=int, default=None)

        obj = TestClass()

        # First time read the default is set to None
        value = obj.data
        self.assertIsNone(value)

        # Assign an integer (expected_type)
        obj.data = 100
        value = obj.data
        self.assertEqual(100, value)

        # Assign an invalid value (None) which should fail.
        with self.assertRaises(TypeError):
            obj.data = None

        print("OK")
        return 0

    def test_TypedProperty_req_assign_before_use(self):
        """
        Test typed property ``req_assign_before_use`` properly triggers
        an ``UnboundLocalError`` exception (use before assign.)
        """

        class TestClass(object):
            data = typed_property("data", expected_type=int, default=None, req_assign_before_use=True)

        obj = TestClass()

        # First time read the default is set to None
        with self.assertRaises(UnboundLocalError):
            obj.data

        print("OK")
        return 0

    def test_TypedProperty_wrong_type(self):
        """
        Test the sanity check that a validator must be callable.
        """

        class TestClass(object):
            data = typed_property("data", expected_type=int, default=None)

        obj = TestClass()

        with self.assertRaises(TypeError):
            obj.data = 99.8

        print("OK")
        return 0

    def test_TypedProperty_validator(self):
        """
        Test the sanity check that a validator must be callable.
        """

        def validate_int_geq_100(value):
            if value < 100:
                return 0     # Falsy means fail.
            return 1         # Truthy means success.

        class TestClass(object):
            data = typed_property("data", expected_type=int, default=None, validator=validate_int_geq_100)

        obj = TestClass()
        obj.data = 100

        with self.assertRaises(ValueError):
            obj.data = 99

        print("OK")
        return 0

    def test_TypedProperty_validator_must_be_callable(self):
        """
        Test the sanity check that a validator must be callable.
        """

        class TestClass(object):
            data = typed_property("data", expected_type=int, default=None, validator="X")

        obj = TestClass()

        with self.assertRaises(TypeError):
            obj.data = 100

        print("OK")
        return 0

    def test_TypedProperty_deleter(self):
        """
        Test a typed_property with a default
        """

        class TestClass(object):
            data = typed_property("data", expected_type=int, default=None)

        obj = TestClass()

        # First time read the default is set to None
        value = obj.data
        self.assertIsNone(value)

        # Assign an integer (expected_type)
        obj.data = 100
        value = obj.data
        self.assertEqual(100, value)

        self.assertEqual(True, hasattr(obj, "_data"))
        self.assertEqual(True, hasattr(obj, "_data_is_set"))

        # test the deleter
        del obj.data

        self.assertEqual(False, hasattr(obj, "_data"))
        self.assertEqual(False, hasattr(obj, "_data_is_set"))

        print("OK")
        return 0

    def test_TypedProperty_transform(self):
        """
        Test a transform
        """

        def transform_int_range_0_5(value):
            value = max(0, value)
            value = min(5, value)
            return value

        class TestClass(object):
            data = typed_property("data", expected_type=int, default=None, transform=transform_int_range_0_5)

        obj = TestClass()

        obj.data = 100
        self.assertTrue(obj.data <= 5)
        self.assertTrue(obj.data >= 0)

        obj.data = -9
        self.assertTrue(obj.data <= 5)
        self.assertTrue(obj.data >= 0)

        print("OK")
        return 0

    def test_TypedProperty_transform_with_internal_type(self):
        """
        Test a transform
        """

        def transform_int_range_0_5(value):
            value = max(0, value)
            value = min(5, value)
            return value

        class TestClass(object):
            data = typed_property(
                "data", expected_type=int, internal_type=int, default=None, transform=transform_int_range_0_5
            )

        obj = TestClass()

        obj.data = 100
        self.assertTrue(obj.data <= 5)
        self.assertTrue(obj.data >= 0)

        obj.data = -9
        self.assertTrue(obj.data <= 5)
        self.assertTrue(obj.data >= 0)

        print("OK")
        return 0

    def test_TypedProperty_transform_is_callable(self):
        """
        Test a transform
        """

        class TestClass(object):
            data = typed_property("data", expected_type=int, default=None, transform=99)

        obj = TestClass()

        with self.assertRaises(TypeError):
            obj.data = 100

        print("OK")
        return 0

    def test_TypedProperty_default(self):
        """
        Test a strict default entry.
        """

        class TestClass(object):
            data = typed_property("data")

        obj1 = TestClass()

        # set to None by default if never set.
        self.assertIsInstance(obj1.data, type(None))

        obj1.data = 1
        self.assertIsInstance(obj1.data, int)

        obj1.data = "a"
        self.assertIsInstance(obj1.data, str)

        with self.assertRaises(TypeError):
            obj1.data = None

        print("OK")
        return 0

    def test_TypedProperty_default_factory(self):
        """
        Test a strict default entry.
        """

        class TestClass(object):
            data = typed_property("data", default_factory=dict)

        obj1 = TestClass()
        print(obj1.data)

        obj2 = TestClass()
        print(obj2.data)

        self.assertIsInstance(obj1.data, dict)
        self.assertIsInstance(obj2.data, dict)

        self.assertNotEqual(id(obj1.data), id(obj2.data))

        return 0

    def test_TypedProperty_default_factory_is_callable(self):
        """
        Test a strict default entry.
        """

        class TestClass(object):
            data = typed_property("data", default_factory={})

        obj1 = TestClass()

        with self.assertRaises(TypeError):
            obj1.data

        return 0



# EOF
