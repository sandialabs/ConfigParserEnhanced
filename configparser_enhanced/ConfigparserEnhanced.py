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


# ===============================
# H E L P E R   F U N C T I O N S
# ===============================



# ===============================
# M A I N   C L A S S
# ===============================

class ConfigparserEnhanced(object):
    """

    Args:
        filename (str): The filename of the .ini file to load.
        section  (str): The section in the .ini file to process
                        for an action list. Default: None

    Attributes:
        config  ()    : The data from the .ini file as loaded by configparser.
        section (str) : The section from the .ini file that is loaded.
        actions (dict): The actions that would be processed when apply() is called.

    """

    def __init__(self, filename, section=None):
        self._inifile     = filename
        self._section     = section
        self._configdata  = None


    @property
    def config(self) -> configparser.ConfigParser:
        """
        This property provides a link to the raw results from using the configparser
        class to parse a .ini file.

        This property is lazy-evaluated and will be processed the first time it is
        accessed.

        Returns:
            ConfigParser object containing the contents of the configuration file
            that is loaded from a .ini file.
        """
        if self._configdata is None:
            self._configdata = configparser.ConfigParser(allow_no_value=True)

            # prevent ConfigParser from lowercasing the keys
            self._configdata.optionxform = str

            try:
                with open(self._inifile, 'r') as ifp:
                    self._configdata.read_file(ifp)
            except IOError as err:
                msg = "+" + "="*78 + "+\n" + \
                      "|   ERROR: Unable to load configuration .ini file\n" + \
                      "|   - Requested file: {}\n".format(self._inifile) + \
                      "|   - CWD: {}\n".format(os.getcwd()) + \
                      "+" + "="*78 + "+\n"
                sys.exit(msg)

        return self._configdata


    @property
    def section(self) -> str:
        """
        Returns the section that the parser portion will parse out.

        Returns:
            String containing the root-level section we'd like to parse.
        """
        return self._section


    @section.setter
    def section(self, value) -> str:
        """
        Provides a setter capability for the section data.

        Args:
            value str: the new value we wish to assign to the section.

        Raises:
            TypeError is raised if the value provided is not a string

        TODO:
            This should _reset_ the parsed data (once it's implemented).
        """
        if not isinstance(value, str):
            raise TypeError("section names must be a string type.")

        self._section = value

        return self._section


    def parse_configuration(self) -> dict:
        """
        """
        data = None

        if self.section == None:
            raise TypeError("ERROR: Parsing requires a section to be set.")

        data = self._parse_configuration_r(self.section, data=data)

        return data


# TODO:
# - We might consider replacing the regex
#   expression from text with a property so derivitive classes could easily
#   override it by changing the property.
#   - related to this, might create some kind of a `normalize_op1()`
#     method, that could be also overridden or something to deal with
#     operand clanup operations?
#   - would a `normalize_op2()` method also be useful for completeness?
# Should work with:
# op1
# op1 op2
# op1 'op2'
# op1 'op 2'
# op1 op2 op3
# op1 'op2' op3
# op-1
# op-1 op2
# op-1 op2 op3
# op-1 'op2'
# op-1 'op2' op3
# op-1 'op 2'
# op-1 op-2
# op_1 op_2
# - Develop new tests
# - Clean up REGEX -- op2 needs some love to be more forgiving.
# - Get to a working state


    def _parse_configuration_r(self, section_name, data=None, processed_sections=None) -> dict:
        """
        """
        current_section = None

        if section_name == None:
            raise TypeError("ERROR: a section name must not be None.")

        print("Processing section: `{}`".format(section_name))

        try:
            current_section = self.config[section_name]
        except KeyError:
            message = "ERROR: No section named `{}` was found in the configuration file.".format(section_name)
            raise KeyError(message)

        # Verify that we actually got a section returned. If not, raise a KeyError.
        if current_section is None:
            raise Exception("ERROR: Unable to load section `{}` for unknown reason.".format(section_name))

        if processed_sections is None:
            processed_sections = {}
        processed_sections[section_name] = True

        # regex key splitter to extract op1 and op2
        regex_key_splitter = re.compile(r"^([a-zA-Z0-9-_]+)( '?([a-zA-Z0-9-_ ]+)'?(?: .*)*)?")

        for sec_k,sec_v in current_section.items():
            sec_k = str(sec_k).strip()
            sec_v = str(sec_v).strip()
            sec_v = sec_v.strip('"')
            print("- Entry: `{}` : `{}`".format(sec_k,sec_v))

            # process the key via Regex to extract op1 and op2
            regex_key_splitter_m = regex_key_splitter.match(sec_k)
            if not regex_key_splitter_m:
                continue

            op1 = str(regex_key_splitter_m.groups()[0]).strip()
            op2 = regex_key_splitter_m.groups()[2]

            # replace chars in op1 with legal chars for legal Python function name chars
            op1 = op1.replace('-','_')

            if op2:
                op2 = str(op2).strip()

            #op_list = sec_k.split()
            #op1 = str(op_list[0]).strip()
            #op2 = None
            #if len(op_list) >= 2:
            #    op2 = str(op_list[1]).strip()
            print("- op1: {}".format(op1))
            print("- op2: {}".format(op2))

            ophandler_f = getattr(self, "_handler_{}".format(op1), None)
            if ophandler_f:
                ophandler_f(section_name, op1, op2, data, processed_sections)

        print("Completed section: `{}`".format(section_name))
        return data


    def _handler_use(self, section_name, op1, op2, data, processed_sections=None):
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
        print("+++ _handler_{}".format(op1))
        if op2 not in processed_sections.keys():
            self._parse_configuration_r(op2, data, processed_sections)
        else:
            print("WARNING: Detected a cycle in section `use` dependencies:\n" + \
                  "         cannot load [{}] from [{}].".format(op1, section_name))

        print("--- _handler_{}".format(op1))
        return 0
