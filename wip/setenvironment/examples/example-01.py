#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
Example app for SetEnvironment
"""
from __future__ import print_function # python 2 -> 3 compatiblity

import os
from pprint import pprint

import setenvironment



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
        raise FileNotFoundError("Unable to find {} in {}".format(filename, os.getcwd())) # pragma: no cover
    return output



def parse_section(parser, section):
    data = parser.configparserenhanceddata[section]

    print("\nAction Data")
    print("===========")
    pprint(parser.actions[section], width=120)

    # Print the loginfo from the last search
    print("\nLogInfo")
    print("=======")
    handler_list = [
        (d['type'], d['name']) for d in parser._loginfo if d['type'] in ['handler-entry', 'handler-exit']
    ]
    pprint(handler_list, width=120)

    assert len(parser.actions[section]) > 0

    return data



def test_setenvironment(filename="config.ini"):
    print("filename    : {}".format(filename))
    print("")

    parser = setenvironment.SetEnvironment(filename=filename)
    parser.debug_level = 5
    parser.exception_control_level = 4

    # pre-parse all sections
    parser.parse_all_sections()

    section_name = "CONFIG_A+" # ENVVARS + USE
                               #section_name = "CONFIG_B+"      # MODULES + USE
                               #section_name = "CONFIG_A"       # ENVVARS ONLY
                               #section_name = "CONFIG_B"       # MODULES ONLY

    parse_section(parser, section_name)

    print("")
    parser.pretty_print_actions(section_name)

    parser.apply(section_name)

    envvar_filter = ["TEST_SETENVIRONMENT_", "TEST_ENVVAR_", "FOO", "BAR", "BAZ"]

    parser.pretty_print_envvars(envvar_filter, True)

    for interp, ext in [("bash", "sh"), ("python", "py")]:
        filename = "___set_environment.{}".format(ext)
        parser.write_actions_to_file(filename, section_name, interpreter=interp)

    return



def main():
    """
    main app
    """
    fname_ini = "example-01.ini"
    fpath_ini = find_config_ini(filename=fname_ini)

    test_setenvironment(filename=fpath_ini)



if __name__ == "__main__":
    main()
    print("Done.")
