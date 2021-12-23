#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
Example application that uses ConfigParserEnhanced
"""
from __future__ import print_function # python 2 -> 3 compatiblity

from configparserenhanced import ConfigParserEnhanced



def test_configparserEnhanced(filename="config.ini"):
    print(f"Using filename: `{filename}`\n")

    parser = ConfigParserEnhanced(filename=filename)

    # Additional ConfigParserEnhanced flags:
    #parser.debug_level = 5
    #parser.exception_control_level = 4
    #parser.exception_control_compact_warnings = True
    #parser.exception_control_silent_warnings  = False

    section_name = "SECTION-B"

    parser.parse_section(section_name)

    print(f"Section data for `{section_name}`:")
    section = parser.configparserenhanceddata[section_name]
    print(f"{section}")

    print("")
    print("Section List:")
    for section_name in parser.configparserenhanceddata.sections():
        print(f"- {section_name}")

    print("")
    print("Section Details:")
    for section_name, options in parser.configparserenhanceddata.items():
        print(f"[{section_name}]")
        for key, value in options.items():
            print(f"{key} : {value}")
        print("")

    # Write out a 'collapsed' version of the .ini file
    with open("_example-01-parsed.ini", "w") as ofp:
        parser.write(ofp)
    return 0



if __name__ == "__main__":
    test_configparserEnhanced(filename="example-01.ini")
    print("Done.")
