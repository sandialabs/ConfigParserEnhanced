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
    messages based on a debug level. Generally, the higher the debug_level
    the more _verbose_ / _detailed_ the messages will be.

    Note:
        Normal operation of codes will have a debug_level of 0.

        debug_level (int):

    Todo:
        This should be moved to its own class file / project so it can be
        reused for other components of our framework.
    """

    @property
    def debug_level(self) -> int:
        """int: Sets the debugging level we'll be using for an instance
            of the class. This can be any integer > 0. If a negative number is
            assigned 0. *Default = 0*
        """
        if not hasattr(self, '_debug_level'):
            self._debug_level = 0
        return self._debug_level


    @debug_level.setter
    def debug_level(self, value):
        self._debug_level = max(int(value), 0)
        return self._debug_level


    def debug_message(self, debug_level, message, end="\n", useprefix=True):
        """Optionally prints a message based on the debug_level setting.

        A simple wrapper to ``print()`` which optionally prints out a message
        based on the current ``debug_level``. If ``debug_level`` is > 0 then an
        annotation is prepended to the message that indicates what level of
        debugging triggers this message.

        If ``debug_level`` is > 0, we will also force a stdout flush once the
        command has completed.

        Args:
            debug_level (int): Sets the debug-level requirement of this message.
                If ``self.debug_level`` is <= ``debug_level`` then this message will
                be printed. If this paramter is 0 then we do not prepend the debug
                level annotation to the message so that it will appear the same as
                a basic ``print()`` message.
            message (str): This is the message that will be printed.
            end (str): This allows us to override the line-ending. *Default = "\n"*.
            useprefix (bool): If enabled and ``debug_level`` is > 0 then a prefix
                of ``[D-{debug_level}] `` will be prepended to the message when
                printed. *Default = True*.

        Returns:
            None
        """
        if self.debug_level >= debug_level:
            if debug_level > 0:
                prefix = ""
                if useprefix:
                    prefix = "[D-{}] ".format(debug_level)
                message = "{}{}".format(prefix, message)
            print(message, end=end)
            if debug_level > 0:
                sys.stdout.flush()
        return

