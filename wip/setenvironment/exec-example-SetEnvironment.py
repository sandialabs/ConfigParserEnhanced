#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
Example app for SetEnvironment
"""
from __future__ import print_function  # python 2 -> 3 compatiblity

import os
from pprint import pprint

import setenvironment



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



def test_setenvironment(filename="config.ini"):
    print("filename    : {}".format(filename))
    print("")

    parser = setenvironment.SetEnvironment(filename=filename)
    parser.debug_level = 5
    parser.exception_control_level = 4

    parse_section(parser, "CONFIG_A+")     # ENVVARS + USE
    #parse_section(parser, "CONFIG_B+")     # MODULES + USE
    #parse_section(parser, "CONFIG_A")      # ENVVARS ONLY
    #parse_section(parser, "CONFIG_B")      # MODULES ONLY

    print("")
    parser.pretty_print_actions()

    parser.apply()

    envvar_filter=["TEST_SETENVIRONMENT_", "FOO", "BAR", "BAZ"]

    parser.pretty_print_envvars(envvar_filter, True)

    return



def parse_section(parser, section):
    #data = parser.parse_section(section)
    data = parser.configparserenhanceddata[section]

    print("\nAction Data")
    print("===========")
    pprint(parser.actions, width=120)

    # Print the loginfo from the last search
    print("\nLogInfo")
    print("=======")
    #parser._loginfo_print(pretty=True)
    handler_list = [ (d['type'], d['name']) for d in parser._loginfo if d['type'] in ['handler-entry','handler-exit']]
    pprint(handler_list, width=120)

    assert len(parser.actions) > 0

    parser.write_actions_to_file("___set_environment.sh")

    return data



def experimental(filename="config.ini"):

    return



def main():
    """
    main app
    """
    fname_ini = "config_test_setenvironment.ini"
    fpath_ini = find_config_ini(filename=fname_ini)

    experimental(filename=fpath_ini)

    test_setenvironment(filename=fpath_ini)


if __name__ == "__main__":
    main()
    print("Done.")


