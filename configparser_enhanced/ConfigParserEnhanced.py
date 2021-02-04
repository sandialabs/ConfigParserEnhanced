#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
# TODO: Implement me!
"""
from __future__ import print_function

import configparser
import os
#import pprint
import re
import sys


# ===========================================================
#   H E L P E R   F U N C T I O N S   A N D   C L A S S E S
# ===========================================================



class Debuggable(object):
    """
    A helper class that implements some helpers for things like conditional
    messages based on a debug level. Generally, the higher the debug_level
    the more _verbose_ / _detailed_ the messages will be.

    Note:
        Normal operation of codes will have a debug_level of 0.

    Attributes:
        debug_level (int): sets the debugging level we'll be using for an instance
            of the class. This can be any integer > 0. If a negative number is
            assigned then it will be set to 0. Default: 0

    Todo:
        This should be moved to its own class file / project so it can be
        reused for other components of our framework.
    """

    @property
    def debug_level(self):
        """
        Returns the current 'debug level' of the class. This is used
        to determine whether or not certain messages get printed by
        `debug_message()` etc.
        """
        if not hasattr(self, '_debug_level'):
            self._debug_level = 0
        return self._debug_level


    @debug_level.setter
    def debug_level(self, value):
        """
        Sets the debug level. Negative values will be forced to be 0.
        """
        self._debug_level = max(int(value), 0)
        return self._debug_level


    def debug_message(self, debug_level, message, end="\n"):
        """
        A simple wrapper to `print()` which optionally prints out a message
        based on the current `debug_level`. If `debug_level` is > 0 then an
        annotation is prepended to the message that indicates what level of
        debugging triggers this message.

        If `debug_level` is > 0, we will also force a stdout flush once the
        command has completed.

        Attributes:
            debug_level (int): Sets the debug-level requirement of this message.
                If `self.debug_level` is <= `debug_level` then this message will
                be printed. If this paramter is 0 then we do not prepend the debug
                level annotation to the message so that it will appear the same as
                a basic `print()` message.
            message (str): This is the message that will be printed.
            end (str): This allows us to override the line-ending. Default="\n"

        """
        if self.debug_level >= debug_level:
            if debug_level > 0:
                message = "[D-{}] {}".format(debug_level, message)
            print(message, end=end)
            if debug_level > 0:
                sys.stdout.flush()
        return



# ===============================
#   M A I N   C L A S S
# ===============================

class ConfigParserEnhanced(Debuggable):
    """
    Provides an enhanced version of the `configparser` module which enables some
    extended processing of the information provided in a `.ini` file.

    Args:
        filename (str): The filename of the .ini file to load.
        section  (str): The section in the .ini file to process
                        for an action list. Default: None

    Attributes:
        config  (object): The data from the .ini file as loaded by configparser.
            This will return a `configparser.ConfigParser` object.
        section (str): The section from the .ini file that is loaded.
        actions (dict): The actions that would be processed when apply() is called.

    .. configparser reference:
        https://docs.python.org/3/library/configparser.html
    """
    def __init__(self, filename):
        self.inifilename = filename


    # -----------------------
    #   P R O P E R T I E S
    # -----------------------


    @property
    def inifilename(self):
        if not hasattr(self, '_inifile'):
            raise ValueError("ERROR: The filename has not been specified yet.")
        else:
            return self._inifile


    @inifilename.setter
    def inifilename(self, filename):
        if not isinstance(filename, str):
            raise TypeError("ERROR: .ini filename must be a string type.")

        # if we have already loaded a .ini file, we should reset the data
        # structure. Delete any lazy-created properties, etc.
        if hasattr(self, '_inifile'):
            if hasattr(self, '_configdata'):
                delattr(self, '_configdata')
            if hasattr(self, '_loginfo'):
                delattr(self, '_loginfo')

        self._inifile = filename


    @property
    def config(self) -> configparser.ConfigParser:
        """
        This property provides a link to the raw results from using the configparser
        class to parse a .ini file.

        This property is lazy-evaluated and will be processed the first time it is
        accessed.

        Returns:
            configparser.ConfigParser object containing the contents of the configuration
            file that is loaded from a .ini file.

        .. configparser reference:
            https://docs.python.org/3/library/configparser.html
        """
        if not hasattr(self, '_configdata'):
            self._configdata = configparser.ConfigParser(allow_no_value=True)

            # prevent ConfigParser from lowercasing the keys
            self._configdata.optionxform = str

            try:
                with open(self.inifilename, 'r') as ifp:
                    self._configdata.read_file(ifp)
            except IOError as err:
                msg = "\n" + \
                      "+" + "="*78 + "+\n" + \
                      "|   ERROR: Unable to load configuration .ini file\n" + \
                      "|   - Requested file: `{}`\n".format(self.inifilename) + \
                      "|   - CWD: `{}`\n".format(os.getcwd()) + \
                      "+" + "="*78 + "+\n"
                raise IOError(msg)

        return self._configdata


    @property
    def section(self) -> str:
        """
        The section that the parser portion will parse out.

        Returns:
            String containing the root-level section we'd like to parse.
        """
        if not hasattr(self, '_section'):
            raise ValueError("ERROR: A section has not been set yet.")
        else:
            if not isinstance(self._section, str):
                raise TypeError("An Internal ERROR occurred - `section` should always return a str.")
            return self._section


    @section.setter
    def section(self, value) -> str:
        """
        Provides a setter capability for the section data.

        Args:
            value str: the new value we wish to assign to the section.
                This should be a nonempty string.

        Raises:
            TypeError is raised if the value provided is not a string.
            ValueError is raised if we try to assign an empty string.

        """
        if value == None:
            return None

        if not isinstance(value, str):
            raise TypeError("section names must be a string type.")

        if value == "":
            raise ValueError("section names cannot be empty.")

        # clear out any parser-specific stuff if we change the section out.
        if hasattr(self, '_section'):
            if hasattr(self, '_loginfo'):
                delattr(self, '_loginfo')

        self._section = value
        return self._section


    # --------------------
    #   P A R S E R
    # --------------------


    @property
    def parser_data_init(self):
        """
        Initializer for the data object that gets sent to parser initially.

        Returns:
            dict containing the 'base' configuration that is empty and ready for
            for the parser handlers to populate.
        """
        output = {}
        return output


    @property
    def regex_op_splitter(self) -> str:
        """
        This parameter stores the regex used to match operation lines in the parser.

        We provide this as a property in case a subclass needs to override it.

        Warning: There be dragons here!
        This is only something you should do if you _really_ understand the
        core parser engine. If this is changed significantly, you will likely also
        need to override the following methods too:
        - `get_op1_from_regex_match()`
        - `get_op2_from_regex_match()`
        - `regex_op_matcher()`
        """
        if not hasattr(self, '_regex_op_splitter'):
            # regex op splitter to extract op1 and op2, this is pretty complicated so here's the
            # deets:
            # - The goal is to capture op1 and op2 into groups from a regex match.
            # - op1 will always be captured by group1. We only allow this to be letters,
            #   numbers, dashes, or underscores.
            #   - No spaces are ever allowed for op1 because this will get mapped to a handler method
            #     name of the form `_handler_{op1}()`
            # - op2 is captured by group 2 or 3
            #   - group2 if op2 is single-quoted (i.e., 'op 2' or 'op2' or 'op-2')
            #   - group3 if op2 is not quoted.
            # - op2 is just a string that gets passed down to the handler function so we will
            #   let this include spaces, but if you do include spaces it _must_ be single quoted
            #   otherwise we treat everything after the space as 'extra' stuff.
            #   - This 'extra' stuff is discarded by ConfigParserEnhanced so that it can be used
            #     to differentiate multiple commands in a section from one another that might otherwise
            #     map to the same key. Note, in a normal `configparser` `.ini` file each section is
            #     a list of key:value pairs. The keys must be unique but that can be problematic
            #     if we're implementing a simple parsed language on top of it.
            #     For example, if we're setting envvars and wanted multiple entries for PATH:
            #         envvar-prepend PATH: /something/to/prepend/to/path
            #         envvar-prepend PATH: /another/path/to/prepend
            #     Here, the keys would be invalid for configparser because they're identical.
            #     By allowing 'extra' entries after op2 we can allow a user to make each one unique.
            #     So our example above could be changed to:
            #         envvar-prepend PATH A: /something/to/prepend/to/path
            #         envvar-prepend PATH B: /another/path/to/prepend
            #     In both cases, op1 = 'envvar-prepend' and op2 = 'PATH' but the addition of the
            #     'A' and 'B' will differentiate these keys from the configparser's perspective.
            #  - Note: This comment information should find its way into the docs sometime.
            # regex_string = r"^([\w\d\-_]+)( '([\w\d\-_ ]+)'| ([\w\d\-_]+)(?: .*)*)?"   # (old and busted)
            regex_string = r"^([\w\d\-_]+) ?('([\w\d\-_ ]+)'|([\w\d\-_]+)(?: .*)*)?"
            #                  ^^^^^^^^^^    ^^^^^^^^^^^^^    ^^^^^^^^^^
            #                      \              \                \-- op3 : group 3
            #                       \              \--- op2 : group 2
            #                        \--- op1 : group 1
            self._regex_op_splitter = re.compile(regex_string)

        return self._regex_op_splitter


    def regex_op_matcher(self, text):
        """
        Executes the regex match operation against `regex_op_splitter`.
        This method adds the ability to add in extra checks for sanity
        that can be inserted into the parser. If the results of the match
        fails the extra scrutiny, then return None.

        Args:
            text (str): The string in which we're searching.

        Returns:
            Regex match if one exists and we pass any sanity checks that are
            added to this method.
        """
        m = self.regex_op_splitter.match(text)

        # Sanity checks: Change match to None if we fail
        if m != None:
            if m.groups()[0] != text.split()[0]:
                m = None
        return m


    def get_op1_from_regex_match(self, regex_match) -> str:
        """
        Extracts op1 from the regular expression match groups.

        Args:
            regex_match (object): A `re.match()` object.

        Returns:
            String containing the op1 parameter, formatted properly for use
            as part of a handler name.

        Note:
            op1 must be a string that could be used in a method name since this gets
            used by the parser to call a function of the pattern `_handler_{op1}`
        """
        output = str(regex_match.groups()[0])
        output = output.strip()
        output = output.replace('-','_')
        return output


    def get_op2_from_regex_match(self, regex_match) -> str:
        """
        Extracts op2 from the regular expression match groups.

        Args:
            regex_match (object): A `re.match()` object.

        Returns:
            String containing the op2 parameter or None if one doesn't exist.
        """
        output = None

        # op2 matches group 2 or 3 depending on whether or not there were quotes.
        # (there are 4 groups)
        if regex_match.groups()[2]:
            output = str(regex_match.groups()[2]).strip()
        elif regex_match.groups()[3]:
            output = str(regex_match.groups()[3]).strip()

        return output


    def parse_configuration(self) -> dict:
        """
        Top level parser entry point.

        Args:
            data (dict): An initializer for the `data` object which will be passed down into
                         all handlers within the parser for updates and additions. Default: None
        """
        data = self._parse_configuration_r(self.section)
        return data


    def _parse_configuration_r(self, section_name, data=None, processed_sections=None) -> dict:
        """
        Recursive driver of the parser.
        """
        current_section = None

        if section_name == None:
            raise TypeError("ERROR: a section name must not be None.")

        self.debug_message(0, "Processing section: `{}`".format(section_name))                      # Console Logging
        self._loginfo_add({'type': 'section-entry', 'name': section_name})                          # Logging

        try:
            current_section = self.config[section_name]
        except KeyError:
            message = "ERROR: No section named `{}` was found in the configuration file.".format(section_name)
            raise KeyError(message)

        # Verify that we actually got a section returned. If not, raise a KeyError.
        # (wcm) This might not be reachable given the KeyError check.
        #       At least, I can't figure out how to trigger this manually in testing ;)
        #       It's probably not a bad idea to hang onto it for now, but maybe mark with
        #       a #pragma no cover?
        if current_section is None:
            raise Exception("ERROR: Unable to load section `{}` for unknown reason.".format(section_name))

        if data == None:
            data = self.parser_data_init
            assert isinstance(data, dict)

        if processed_sections == None:
            processed_sections = {}
        processed_sections[section_name] = True

        for sec_k,sec_v in current_section.items():
            sec_k = str(sec_k).strip()
            sec_v = str(sec_v).strip()
            sec_v = sec_v.strip('"')

            self.debug_message(0, "- Entry: `{}` : `{}`".format(sec_k,sec_v))                       # Console
            self._loginfo_add({'type': 'section-key-value', 'key': sec_k, 'value': sec_v})          # Logging

            # process the key via Regex to extract op1 and op2
            regex_op_splitter_m = self.regex_op_matcher(sec_k)

            # Skip entry if we didn't get a match
            if not regex_op_splitter_m:
                continue

            self.debug_message(5, "regex-groups {}".format(regex_op_splitter_m.groups()))
            op1 = self.get_op1_from_regex_match(regex_op_splitter_m)
            op2 = self.get_op2_from_regex_match(regex_op_splitter_m)

            self._loginfo_add({"type": 'section-operands', 'op1': op1, 'op2': op2})                 # Logging
            self.debug_message(0, "- op1: {}".format(op1))                                          # Console
            self.debug_message(0, "- op2: {}".format(op2))                                          # Console

            ophandler_f = getattr(self, "_handler_{}".format(op1), None)
            if ophandler_f:
                ophandler_f(section_name, op1, op2, data, processed_sections, entry=(sec_k,sec_v) )

        self._loginfo_add({'type': 'section-exit', 'name': section_name})                           # Logging
        self.debug_message(0, "Completed section: `{}`".format(section_name))                       # Console
        return data


    # --------------------
    #   H A N D L E R S
    # --------------------


    def _handler_use(self, section_name, op1, op2, data, processed_sections=None, entry=None) -> int:
        """
        This is a handler that will get executed when we detect a `use` operation in
        our parser.

        Args:
            section_name (str): The section name of the current _section_ we're processing.
            op1 (str): The first operation parameter
                       (i.e., `use` if the full key is `use section_name`)
            op2 (str): The second operation parameter
                       (i.e., `section_name` if the full key is `use section_name`)

        Returns:
            integer value: 0 if successful, 1 if there was a problem.

        Raises:
            Nothing
        """
        self._loginfo_add({'type': 'handler-entry', 'name': '_handler_use'})                        # Logging
        self.debug_message(0, "+++ _handler_{}".format(op1))                                        # Console

        if op2 not in processed_sections.keys():
            self._parse_configuration_r(op2, data, processed_sections)
        else:
            self.debug_message(0, "WARNING: Detected a cycle in section `use` dependencies:\n" + \
                                  "         cannot load [{}] from [{}].".format(op1, section_name))

        self._loginfo_add({'type': 'handler-exit', 'name': '_handler_use'})                         # Logging
        self.debug_message(0, "--- _handler_{}".format(op1))                                        # Console
        return 0


    # --------------------
    #   H E L P E R S
    # --------------------


    def _loginfo_add(self, entry) -> None:
        """
        If in debug mode, we can use this to log operations.
        Appends to _loginfo

        Args:
            entry (dict): A dictionary containing log information that we're appending.
                          At minimum it should have: `type: typestring`.

        Returns:
            Nothing
        """
        if not hasattr(self, '_loginfo'):
            self._loginfo = []

        if self.debug_level > 0:
            if not isinstance(entry, dict):
                raise TypeError("entry should be a dictionary type.")
            if 'type' not in entry.keys():
                raise ValueError("entry must have a `type: typestr` entry`")
            self._loginfo.append(entry)
        else:
            pass
        return


    def _loginfo_print(self, pretty=True) -> None:
        """
        This is a helper to pretty-print the loginfo object
        """
        if pretty:
            self.debug_message(1, "Loginfo:")
            for entry in self._loginfo:
                self.debug_message(1, "Entry Type: `{}`".format(entry['type']))
                self.debug_message(1, "--------------" + "-"*len(entry['type']))
                max_key_len = max(map(len, entry))
                for k,v in entry.items():
                    key_len_diff = max_key_len - len(k)
                    self.debug_message(1, "--- `{}`{}: `{}`".format(k,' '*(key_len_diff),v))
                self.debug_message(1, "")
        else:
            print(self._loginfo)

        return

