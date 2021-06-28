#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
.. Google Docstrings Ref:
    https://gist.github.com/dsaiztc/9b4c15c6dfef08a957c1
"""
from __future__ import print_function

import sys

# ===========================================================
#   H E L P E R   F U N C T I O N S   A N D   C L A S S E S
# ===========================================================

# ===============================
#   M A I N   C L A S S
# ===============================



class Debuggable(object):
    """Adds some debugging capabilities to subclasses.

    A helper class that implements some helpers for things like conditional
    messages based on a debug level. Generally, the higher the ``debug_level``
    the more *verbose*/*detailed* the messages will be.

    Note:
        Normal operation of codes will have a ``debug_level`` of 0, which would
        not print out extra debugging information.
    """

    @property
    def debug_level(self) -> int:
        """The debug level of the class.

        The ``debug_level`` is used by various functions to control the level
        of detail provided during an execution.  Values should be positive
        and range from 0 to *intmax*, where the higher the value the more
        *detailed* the information is.

        Returns:
            int: The ``debug_level`` setting. If none has been set, the default
            of 0 is used.
        """
        if not hasattr(self, '_debug_level'):
            self._debug_level = 0
        return self._debug_level

    @debug_level.setter
    def debug_level(self, value):
        self._debug_level = max(int(value), 0)
        return self._debug_level

    def debug_message(self, debug_level, message, end="\n", useprefix=True):
        """Optionally prints a message based on the ``debug_level`` setting.

        A simple wrapper to ``print()`` which optionally prints out a message
        based on the current ``debug_level``. If ``debug_level > 0``, then an
        annotation is prepended to the message that indicates what level of
        debugging triggers this message.

        If ``debug_level > 0``, we will also force a stdout flush once the
        command has completed.

        Args:
            debug_level (int): Sets the debug level requirement of this message.
                If ``self.debug_level <= debug_level``, then this message will
                be printed. If this paramter is 0 then we do not prepend the debug
                level annotation to the message so that it will appear the same as
                a basic ``print()`` message.
            message (str): This is the message that will be printed.
            end (str): This allows us to override the line-ending.
            useprefix (bool): If enabled and ``debug_level > 0``, then a prefix
                of ``[D-{debug_level}]`` will be prepended to the message to
                indicate the ``debug_level`` that triggers this message.
        """
        if self.debug_level >= debug_level:
            if debug_level > 0:
                prefix = ""
                if useprefix:
                    prefix = f"[D-{debug_level}] "
                message = f"{prefix}{message}"

            print(message, end=end)

            if debug_level > 0:
                sys.stdout.flush()
        return
