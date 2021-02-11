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
        Validate the parameter `section_root`
        """
        hp = HandlerParameters()

        # Check default value for property `section_root`
        expected = None
        self.assertEqual(hp.section_root, None,
                         "default `section_root` should be: {}".format(expected))


    def test_HandlerParameters_property_raw_option(self):
        """
        Validate the parameter `raw_option`
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


    def test_HandlerParameters_property_op_params(self):
        """
        Validate the parameter `op_params`
        """
        hp = HandlerParameters()

        # Validate default value
        expected = tuple([None, None])
        self.assertEqual(hp.op_params, expected,
                         "default `op_params` should be: {}".format(expected))

        # Validate assignment checks.
        # 1. Validate type-check (must be a tuple)
        with self.assertRaises(TypeError):
            hp.op_params = None

        # 2. Validate tuple must be of length=2
        with self.assertRaises(ValueError):
            hp.op_params = tuple()
        with self.assertRaises(ValueError):
            hp.op_params = tuple([1])
        with self.assertRaises(ValueError):
            hp.op_params = tuple([1,2,3])

        # 3. Validate a proper assignment
        rval = hp.op_params = expected
        self.assertEqual(expected, hp.op_params)
        self.assertEqual(rval, hp.op_params)


    def test_HandlerParameters_property_data_shared(self):
        """
        Validate the parameter `data_shared`
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


    def test_HandlerParameters_property_data_internal(self):
        """
        Validate the parameter `data_internal`
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


# EOF
