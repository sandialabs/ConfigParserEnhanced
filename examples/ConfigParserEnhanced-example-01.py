#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
Example app for ConfigParserEnhanced.
"""
from __future__ import print_function # python 2 -> 3 compatiblity

import os
from pprint import pprint
import sys

try:
    # Try and load `configparserenhanced` from Python's site-packages.
    print("Load `configparserenhanced`: ", end="")
    from configparserenhanced import ConfigParserEnhanced
    print("OK (site-packages)\n")
except ModuleNotFoundError:
    # If we didn't find it in site-packages, we might be in a clone
    # of the source, so let's see if we can locate it in ../src
    try:
        sys.path.append(os.path.realpath("../src"))
        from configparserenhanced import ConfigParserEnhanced
        print("OK (src)\n")
    except ModuleNotFoundError as exc:
        # Still can't find it? Time to exit.
        print("FAILED\n")
        raise exc



def find_config_ini(filename="config.ini", rootpath="."):
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
    for dirpath, dirnames, filename_list in os.walk(rootpath):
        if filename in filename_list:
            output = os.path.join(dirpath, filename)
            break
    if output is None:
        raise FileNotFoundError("Unable to find {} in {}".format(filename, os.getcwd()))
    return output



def print_section_data(parser, section_name):
    """
    Get and print a section from the ``configparserenhanceddata``.

    Args:
        section_name (str): The name of the section to be printed.
    """
    print("Section data for `{}`:".format(section_name))
    section = parser.configparserenhanceddata[section_name]
    print("{}".format(section))
    return 0



def test_configparserEnhanced(filename="config.ini"):
    print("Using filename: `{}`\n".format(filename))

    parser = ConfigParserEnhanced(filename=filename)
    #parser.debug_level = 5
    #parser.exception_control_level = 4
    #parser.exception_control_compact_warnings = True
    #parser.exception_control_silent_warnings  = False

    section_name = "SECTION-B"

    parser.parse_section(section_name)

    print_section_data(parser, section_name)

    print("")
    print("Section List:")
    for section_name in parser.configparserenhanceddata.sections():
        print("- {}".format(section_name))

    print("")
    print("Section Details:")
    for section_name, options in parser.configparserenhanceddata.items():
        print("[{}]".format(section_name))
        max_keylen = 0
        for key in options.keys():
            max_keylen = max(max_keylen, len(key))
        for option, value in options.items():
            print("{} : {}".format(option.ljust(max_keylen, ' '), value))
        print("")

    # Write out a 'collapsed' version of the .ini file
    with open("_example-01-parsed.ini", "w") as ofp:
        parser.write(ofp)
    return 0



def main():
    """
    main app
    """
    fname_ini = "example-01.ini"
    fpath_ini = find_config_ini(filename=fname_ini)

    test_configparserEnhanced(filename=fpath_ini)



if __name__ == "__main__":
    main()
    print("Done.")
