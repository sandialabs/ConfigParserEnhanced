#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
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
