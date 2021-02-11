#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
Todo:
    Fill in file-level docstring
    Clean up docstrings
"""
from __future__ import print_function

try:
    # @final decorator, requires Python 3.8.x
    from typing import final                                                      # pragma: no cover
except ImportError:                                                               # pragma: no cover
    pass                                                                          # pragma: no cover



# ===================================
#  S U P P O R T   F U N C T I O N S
# ===================================



# ===============================
#   M A I N   C L A S S
# ===============================


class HandlerParameters(object):
    """
    Contains the set of parameters that we pass to Handlers.
    """
    def __init__(self):
        pass

    @property
    def section_root(self) -> str:
        if not hasattr(self, '_section_root'):
            self._section_root = None
        return self._section_root

    @section_root.setter
    def section_root(self, value) -> str:
        self._section_root = str(value)
        return self._section_root

    @property
    def raw_option(self) -> tuple:
        """
        This contains a copy of the key:value pair for the current
        option without editing as a tuple.
        """
        if not hasattr(self, '_raw_option'):
            self._raw_option = (None, None)
        return self._raw_option

    @raw_option.setter
    def raw_option(self, value) -> tuple:
        if not isinstance(value, tuple):
            raise TypeError("raw_option must be a tuple.")
        if len(value) != 2:
            raise ValueError("raw_option must have 2 entries")
        self._raw_option = value
        return self._raw_option

    @property
    def op_params(self) -> tuple:
        """
        Operation parameters for this handler. This must be a tuple of length 2.
        """
        if not hasattr(self, '_op_params'):
            self._op_params = (None, None)
        return self._op_params

    @op_params.setter
    def op_params(self, value) -> tuple:
        """
        Setter for the params property.
        Must be a tuple of length 2 to properly assign.

        Raises:
            TypeError if the value isn't a tuple.
            ValueError if the value is a tuple len != 2.
        """
        if not isinstance(value, tuple):
            raise TypeError("op_params must be a tuple.")
        if len(value) != 2:
            raise ValueError("op_params must have 2 entries")
        self._op_params = value
        return self._op_params

    @property
    def data_shared(self) -> dict:
        """
        Shared data for handlers. This entry should be considered
        persistent across handlers when parsing is run and will
        contain data and information that
        """
        if not hasattr(self, '_data_shared'):
            self._data_shared = {}
        return self._data_shared

    @data_shared.setter
    def data_shared(self, value) -> dict:
        if not isinstance(value, (dict)):
            raise TypeError("data_shared must be a dict type.")
        self._data_shared = value
        return self._data_shared

    @property
    def data_internal(self) -> dict:
        if not hasattr(self, '_data_internal'):
            self._data_internal = {}
        return self._data_internal

    @data_internal.setter
    def data_internal(self, value) -> dict:
        if not isinstance(value, (dict)):
            raise TypeError("data_internal must be a dict type.")
        self._data_internal = value
        return self._data_internal



