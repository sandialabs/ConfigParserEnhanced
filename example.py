#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
test app for ConfigparserEnhanced (will be deleted later, probably).
"""
from __future__ import print_function  # python 2 -> 3 compatiblity

import os

from configparser_enhanced import ConfigparserEnhanced



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



def test_configparserEnhanced(filename="config.ini"):

    section_name = "SECTION A"

    print("filename    : {}".format(filename))
    print("section name: {}".format(section_name))

    parser = ConfigparserEnhanced(filename=filename, section=section_name)

    confdata = parser.config

    parser.section = "SECTION-A+"
    parser.section = "SECTION C+"
    data = parser.parse_configuration()


    return confdata




def main():
    """
    main app
    """
    fname_ini = "config_test_configparserenhanced.ini"
    fpath_ini = find_config_ini(filename=fname_ini)


    test_configparserEnhanced(filename=fpath_ini)


if __name__ == "__main__":
    main()
    print("Done.")


