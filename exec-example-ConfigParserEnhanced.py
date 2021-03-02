#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
Example app for ConfigParserEnhanced.
"""
from __future__ import print_function  # python 2 -> 3 compatiblity

import os
import sys

from configparserenhanced import ConfigParserEnhanced



def find_config_ini(filename="config.ini", rootpath="." ):
    """
    Recursively searches for a particular file among the subdirectory structure.
    If we find it, then we return the full relative path to `pwd` to that file.

    The _first_ match will be returned.

    Args:
        filename (str): The _filename_ of the file we're searching for. Default: 'config.ini'
        rootpath (str): The _root_ path where we will begin our search from. Default: '.'

    Returns:
        String containing the path to the file if it was found. If a matching filename is not
        found then `None` is returned.
    """
    output = None
    for dirpath,dirnames,filename_list in os.walk(rootpath):
        if filename in filename_list:
            output = os.path.join(dirpath, filename)
            break
    if output is None:
        raise FileNotFoundError("Unable to find {} in {}".format(filename, os.getcwd()))  # pragma: no cover
    return output



def print_section(parser, section_name):
    """
    Get and print a section from the ``configparserenhanceddata``.

    Args:
        section_name (str): The name of the section to be printed.
    """
    print("Get {}".format(section_name))
    section = parser.configparserenhanceddata[section_name]
    print(section)
    print("")



def test_configparserEnhanced(filename="config.ini"):


    print("filename    : {}".format(filename))
    print("")

    parser = ConfigParserEnhanced(filename=filename)
    parser.debug_level = 1
    parser.exception_control_level = 4

    section = "SECTION-A+"
    section = "SECTION C+"
    #section = "OPERAND_TEST"

    #
    # Check if 'key 4' is a member of this section in the basic configparserenhanceddata
    # result ()
    #
    option = "key 4"
    print("Is option `{}` in `{}`?".format(option, section))

    if parser.configparserenhanceddata.has_option(section, option):
        value = parser.configparserenhanceddata.get(section, option)
        print("---> [{}][{}] == '{}'".format(section, option, value))
    else:
        print("---> NO")
    print("")

    print_section(parser, "NOVALUE_TEST")
    print_section(parser, "SECTION C+")
    print_section(parser, "SECTION-A")

    print("Loop over items in parser.configparserenhanceddata")
    for section,options in parser.configparserenhanceddata.items():
        print("[{}]".format(section))
        max_keylen=0
        for key in options.keys():
            max_keylen=max(max_keylen, len(key))
        for option,value in options.items():
            print("{} : {}".format(option.ljust(max_keylen, ' '), value))
        print("")
    print("")

    # Print the loginfo from the last search
    print("LOGINFO for the _last_ section processed:")
    parser._loginfo_print(pretty=True)

    return



def experimental(filename="config.ini"):
    """
    A catch-all functionf or experimental stuff we're testing out. This
    gets called before the main 'example' routine.
    """

    # This is a silly test to try out some changes to ECE.
    #if True:
    #    parser = ConfigParserEnhanced(filename=filename)
    #    parser.debug_level = 1
    #    parser.exception_control_level = 4
    #    parser.exception_control_event("WARNING", ValueError, "this is a test\nmesssge!")
    #    sys.exit(0)

    return



def main():
    """
    main app
    """
    fname_ini = "config_test_configparserenhanced.ini"
    fpath_ini = find_config_ini(filename=fname_ini)

    experimental(filename=fpath_ini) # Should this be removed?

    test_configparserEnhanced(filename=fpath_ini)


if __name__ == "__main__":
    main()
    print("Done.")


