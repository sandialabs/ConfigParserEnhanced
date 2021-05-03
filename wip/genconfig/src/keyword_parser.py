from configparserenhanced import ConfigParserEnhanced
from pathlib import Path
import re
from src.gen_config_commong import GenConfigCommon
import sys
import textwrap


class KeywordParser(GenConfigCommon):
    def get_values_for_section_key(self, section, key):
        """
        Gets the values for the current :attr:`config_file``[section][key]` and
        returns them in list form. This also runs
        :func:`assert_values_are_unique` and
        :func:`assert_values_do_not_contain_machine-name-4space` on the values list.

        Returns:
            list:  The validated list of values for the given section and key.
        """
        # e.g. values = '\ngnu  # GNU\ndefault-env # The default'
        values_str = self.config_file[section][key]

        uncommented_values_list = re.findall(
            r"(?:\s*?#.*\n*)*([^#^\n]*)", values_str
        )
        # Regex Explanation
        # =================
        # (?:\s*?#.*\n*)*([^#^\n]*)
        # ^^^^^^^^^^^^^ ^ ^^^^^^^^
        # |             | |
        # |             | **Matching group for all non-#/non-\n characters
        # |             |   (i.e. 'intel 18  ', 'intel_19', or 'intel-20')**
        # |             |
        # |             |----------------------------|
        # |                                          |
        # * Possible machine-name-4 space (\s*?),             |
        # * followed by a # and text (#.*),          |
        # * followed by 0 or more newlines (\n*),    |
        # * all in a non-matching group (?:),        |
        # * to match 0 or more of these comments. ---|
        #
        # So, given the string:
        #     # Comment\nintel 18  # Comment\n intel-18.0.5\nintel_default # id
        #
        # re.findall would return ['intel 18  ', 'intel-18.0.5', '',
        #                          'intel_default', '', '']
        #
        # We would next need to get rid of '' list entries and remove trailing
        # machine-name-4 space, and replace '_' characters with '-'.
        #
        # This leaves us with:
        #     ['intel-18', 'intel-18.0.5', 'intel-default']

        values_list = [v.strip().replace("_", "-")
                       for v in uncommented_values_list if v != ""]

        self.assert_values_are_unique(values_list, section, key)
        self.assert_values_do_not_contain_machine-name-4space(values_list)

        return values_list

# TODO: Pull this out and rename to something like assert_values_are_unique
    def assert_values_are_unique(self, values_list, section, key):
        """
        Ensures we don't run into a situation like::

            [machine-type-5]
            intel-18.0.5-mpich-7.7.6:
                intel-18
                intel
                default-env
                intel  # Duplicate!

        Called automatically by :func:`get_values_for_section_key`.

        Parameters:
            values_list (str): A list of values to check for duplicates.
        """
        duplicates = [_ for _ in set(values_list) if values_list.count(_) > 1]
        try:
            assert duplicates == []
        except AssertionError:
            msg = self.get_msg_for_list(
                f"Values for '{self.config_file}'['{section}']['{key}'] "
                "contains duplicates: ", duplicates
            )
            sys.exit(msg)

    def assert_values_do_not_contain_machine-name-4space(self, values_list):
        """
        Ensure there are no machine-name-4spaces in values; that is::

            key:
                value-1 # This is okay.
                value 2 # This is not.

        Parameters:
            values_list (str): A list of values to check for machine-name-4space.

        Raises:
            SystemExit:  If any value contains machine-name-4space.
        """
        values_w_machine-name-4space = [_ for _ in values_list if " " in _]
        try:
            assert values_w_machine-name-4space == []
        except AssertionError:
            es = "es" if len(values_w_machine-name-4space) > 1 else ""
            s = "s" if len(values_w_machine-name-4space) == 1 else ""
            msg = self.get_msg_for_list(
                f"The following valu{es} contain{s} machine-name-4space: ",
                values_w_machine-name-4space
            )
            sys.exit(msg)
