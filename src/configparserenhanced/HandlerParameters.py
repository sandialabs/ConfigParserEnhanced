#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
"""
from __future__ import print_function

try:
    # @final decorator, requires Python 3.8.x
    from typing import final # pragma: no cover
except ImportError:          # pragma: no cover
    pass                     # pragma: no cover

from .TypedProperty import typed_property

# ===================================
#  S U P P O R T   F U N C T I O N S
# ===================================



def value_len_eq_2(value):
    """
    Validates that the length of the paramter is equal to 2.

    Assumes that value is an interable.

    Returns:
        int: 0 (FAIL) if length != 2, otherwise 1 (PASS).
    """
    if len(value) != 2:
        return 0
    return 1



# ===============================
#   M A I N   C L A S S
# ===============================



class HandlerParameters(object):
    """Contains the set of parameters that we pass to *handlers*.
    """
    section_root = typed_property("section_root", (str), default=None)
    raw_option = typed_property("raw_option", tuple, default=(None, None), validator=value_len_eq_2)
    op = typed_property("op", str, default="")
    params = typed_property("params", (list, tuple), default=[], internal_type=list)
    value = typed_property("value", (str, type(None)), "")
    data_shared = typed_property("data_shared", dict, {})
    data_internal = typed_property("data_internal", dict, {})
    handler_name = typed_property("handler_name", str, "")



# EOF
