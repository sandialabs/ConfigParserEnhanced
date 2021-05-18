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

from ..HandlerParameters import HandlerParameters

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



class HandlerParametersTest(TestCase):

    def setup(self):
        pass                                                                                        # pragma: no cover


    def test_HandlerParameters_property_section_root(self):
        """
        Validate the property `section_root`
        """
        hp = HandlerParameters()

        # Check default value for property `section_root`
        expected = None
        self.assertEqual(hp.section_root, None,
                         "default `section_root` should be: {}".format(expected))

        # Verify the type checking on the setter
        # - Setter only allows string types to be assigned.
        with self.assertRaises(TypeError):
            hp.section_root = None


    def test_HandlerParameters_property_raw_option(self):
        """
        Validate the property `raw_option`
        """
        hp = HandlerParameters()

        # Validate default value
        expected = tuple([None, None])
        self.assertEqual(hp.raw_option, expected,
                         "default `raw_option` should be: {}".format(expected))

        # Validate assignment checks.
        # 1. Validate type-check (must be a tuple)
        with self.assertRaises(TypeError):
            hp.raw_option = None

        # 2. Validate tuple must be of length=2
        with self.assertRaises(ValueError):
            hp.raw_option = tuple()
        with self.assertRaises(ValueError):
            hp.raw_option = tuple([1])
        with self.assertRaises(ValueError):
            hp.raw_option = tuple([1,2,3])

        # 3. Validate a proper assignment
        rval = hp.raw_option = expected
        self.assertEqual(expected, hp.raw_option)
        self.assertEqual(rval, hp.raw_option)
        return 0


    def test_HandlerParameters_property_data_shared(self):
        """
        Validate the property `data_shared`
        """
        hp = HandlerParameters()

        expected_default = {}

        # Check the default value. Should be an empty dict.
        self.assertDictEqual(hp.data_shared, expected_default,
                             "Default `data_shared` should be: {}".format(expected_default))

        # Validate assignment check(s).
        with self.assertRaises(TypeError):
            hp.data_shared = None

        with self.assertRaises(TypeError):
            hp.data_shared = 1

        with self.assertRaises(TypeError):
            hp.data_shared = "str"

        expected_new = {"data_shared_test": True}
        hp.data_shared = expected_new
        self.assertDictEqual(hp.data_shared, expected_new)
        return 0


    def test_HandlerParameters_property_data_internal(self):
        """
        Validate the property `data_internal`
        """
        hp = HandlerParameters()

        expected_default = {}

        # Check the default value. Should be an empty dict.
        self.assertDictEqual(hp.data_internal, expected_default,
                             "Default `data_internal` should be: {}".format(expected_default))

        # Validate assignment check(s).
        with self.assertRaises(TypeError):
            hp.data_internal = None

        with self.assertRaises(TypeError):
            hp.data_internal = 1

        with self.assertRaises(TypeError):
            hp.data_internal = "str"

        expected_new = {"data_internal_test": True}
        hp.data_internal = expected_new
        self.assertDictEqual(hp.data_internal, expected_new)
        return 0


    def test_HandlerParameters_property_value(self):
        """
        Validate the property ``value``
        """
        hp = HandlerParameters()

        # Check default value for property `value`
        expected = ""
        self.assertEqual(hp.value, expected,
                         "default `value` should be: ''".format(expected))

        # Verify the type checking on the setter
        # - Setter only allows string or None types to be assigned.
        with self.assertRaises(TypeError):
            hp.value = 123.456

        expected = "TEST"
        hp.value = expected
        self.assertEqual(expected, hp.value, "value should be `{}`".format(expected))

        expected = None
        hp.value = expected
        self.assertEqual(expected, hp.value, "value should be `{}`".format(expected))

        return 0


    def test_HandlerParameters_property_handler_name(self):
        """
        Validate the property ``handler_name``
        """
        hp = HandlerParameters()

        # Check default value for property `handler_name`
        expected = ""
        self.assertEqual(hp.handler_name, expected,
                         "default `handler_name` should be: ''".format(expected))

        # Verify the type checking on the setter
        # - Setter only allows string types to be assigned.
        with self.assertRaises(TypeError):
            hp.handler_name = None
        return 0


    def test_HandlerParameters_property_op(self):
        """
        Validate the property ``op``
        """
        hp = HandlerParameters()

        # Test 1
        expected = ""
        self.assertEqual(hp.op, expected, "default `op` should be: '{}'".format(expected))

        # Verify the type checking on the setter
        # - Setter only allows string types to be assigned.
        with self.assertRaises(TypeError):
            hp.op = None

        return 0


    def test_HandlerParameters_property_params(self):
        """
        Validate the property ``params``
        """
        hp = HandlerParameters()

        # Test 1
        expected = []
        self.assertListEqual(hp.params, expected, "default `params` should be: '{}'".format(expected))

        # Test 2
        # Verify the type checking on the setter
        # - Setter only allows string types to be assigned.
        with self.assertRaises(TypeError):
            hp.params = None

        # Test 3
        input_list = [1,2,3]
        hp.params = input_list
        self.assertListEqual(input_list, hp.params)

        # Test 4
        hp.params = tuple(input_list)
        self.assertListEqual(input_list, list(hp.params))

        return 0


# EOF
