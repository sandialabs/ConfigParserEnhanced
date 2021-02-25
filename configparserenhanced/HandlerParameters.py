#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
Todo:                            # Do this sometime.
    Fill in file-level docstring #
    Clean up docstrings          #
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
    """Contains the set of parameters that we pass to *handlers*.
    """
    def __init__(self):
        pass

    @property
    def section_root(self) -> str:
        """Name of the *root* section in section parsing.

        This contains the *root* section when recursively parsing
        sections in a ``.ini`` file by :class:`~configparserenhanced.ConfigParserEnhanced`.

        Returns:
            str: A string containing the *root* section name.

        Raises:
            TypeError: If the setter fails to convert the assigned value
                to a string object.
        """
        if not hasattr(self, '_section_root'):
            self._section_root = None
        return self._section_root

    @section_root.setter
    def section_root(self, value) -> str:
        if not isinstance(value, (str)):
            raise TypeError("String conversion failed for {}".format(value))
        self._section_root = value
        return self._section_root

    @property
    def raw_option(self) -> tuple:
        """Raw copy of the ``key: value`` pair from current option.

        This contains a copy of the ``key: value`` pair for the current
        option without editing as a *tuple*.

        Returns:
            tuple: A tuple containing the ``key`` and ``value``
            pairs from the current *option* being processed.

        Raises:
            TypeError: If the value isn't a tuple.
            ValueError: If the value is a tuple with length other than 2.
        """
        if not hasattr(self, '_raw_option'):
            self._raw_option = (None, None)
        return self._raw_option

    @raw_option.setter
    def raw_option(self, value) -> tuple:
        if not isinstance(value, tuple):
            raise TypeError("raw_option must be a tuple.")
        if len(value) != 2:
            raise ValueError("raw_option must have 2 entries.")
        self._raw_option = value
        return self._raw_option

    @property
    def op_params(self) -> tuple: # What's the difference between this and raw_params?
        """
        Operation parameters for this handler. This must be a tuple of length 2.

        Returns:
            tuple: A tuple ``(op1, op2)`` containing the operations extracted from
            the current operation.

        Raises:
            TypeError: If the value isn't a tuple.
            ValueError: If the value is a tuple with length other than 2.
        """
        if not hasattr(self, '_op_params'):
            self._op_params = (None, None)
        return self._op_params

    @op_params.setter
    def op_params(self, value) -> tuple:
        if not isinstance(value, tuple):
            raise TypeError("op_params must be a tuple.")
        if len(value) != 2:
            raise ValueError("op_params must have 2 entries.")
        self._op_params = value
        return self._op_params

    @property
    def value(self) -> str:
        """The value vield of an option.

        This is the *value* field from a given option from a ``.ini``
        file of the form: ``key: value``.

        If there was no value provided, then this should return an
        empty string.

        Returns:
            str: Typically this returns a string, but it can also return ``None``
            when encountering an option from a ``.ini`` file that does not have a separator
            character (i.e., ``key`` instead of ``key:`` or ``key=``).
        """
        if not hasattr(self, '_value'):
            self._value = ""
        return self._value

    @value.setter
    def value(self, value):
        if not isinstance(value, (str, type(None))):
            raise TypeError("Value must be a `str` type.")
        self._value = value
        return self._value

    @property
    def data_shared(self) -> dict:
        """Shared workspace data for handlers.

        This entry should be considered persistent across handlers
        when parsing is run and will contain data and information that
        gets added by the various handlers.

        Returns:
            dict: A dictionary containing the *shared* workspace sent to the handlers in
            :class:`~configparserenhanced.ConfigParserEnhanced`.

        Raises:
            TypeError: If the type is not a ``dict`` during assignment.
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
        """Internal data structure for recursive section parsing.

        This property is used internally by the section parser in
        :meth:`~.ConfigParserEnhanced.parse_configuration` to store
        useful state information as the parser operates.

        Information such as *previously visited sections* during
        recursion is used to prevent infinite loops if there are
        cycles present in the ``use <section>`` entries.

        Returns:
            dict: A dictionary containing the internal state information for the parser.

        Raises:
            TypeError: If assignment is attempted by a value
                that is not a ``dict`` type.
        """
        if not hasattr(self, '_data_internal'):
            self._data_internal = {}
        return self._data_internal

    @data_internal.setter
    def data_internal(self, value) -> dict:
        if not isinstance(value, (dict)):
            raise TypeError("data_internal must be a dict type.")
        self._data_internal = value
        return self._data_internal

    @property
    def handler_name(self) -> str:
        """The handler name for a given operation.

        Returns:
            str: The value from the field.
        """
        if not hasattr(self, '_handler_name'):
            self._handler_name = ""
        return self._handler_name

    @handler_name.setter
    def handler_name(self, handler_name):
        if not isinstance(handler_name, (str)):
            raise TypeError("handler_name must be a str type.")
        self._handler_name = handler_name
        return self._handler_name
