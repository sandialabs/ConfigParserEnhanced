from configparserenhanced import ConfigParserEnhanced
import re
import sys


class KeywordParser:
    def __init__(self, config_filename):
        self.config_filename = config_filename

    @property
    def config(self):
        """
        Gets the :class:`ConfigParserEnhancedData` object with
        :attr:`config_filename` loaded.

        Returns:
            ConfigParserEnhancedData:  A :class:`ConfigParserEnhancedData`
            object with `config_filename` loaded.
        """
        if hasattr(self, "_config"):
            return self._config

        self._config = ConfigParserEnhanced(
            self.config_filename
        ).configparserenhanceddata

        # Actually parses the sections. Shouldn't be needed in the near future
        # once the ConfigParserEnhanced bug is addressed.
        self.config.items()

        return self._config

    def get_values_for_section_key(self, section, key):
        """
        Gets the values for the current :attr:`config``[section][key]` and
        returns them in list form. This also runs
        :func:`assert_values_are_unique` and
        :func:`assert_values_do_not_contain_whitespace` on the values list.

        Returns:
            list:  The validated list of values for the given section and key.
        """
        # e.g. values = '\ngnu  # GNU\ndefault-env # The default'
        values_str = (self.config[section][key]
                      if self.config[section][key] is not None
                      else "")

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
        # * Possible white space (\s*?),             |
        # * followed by a # and text (#.*),          |
        # * followed by 0 or more newlines (\n*),    |
        # * all in a non-matching group (?:),        |
        # * to match 0 or more of these comments. ---|
        #
        # So, given the string:
        #     # Comment\nintel 18  # Comment\n intel-18.0.5\nintel-default # id
        #
        # re.findall would return ['intel 18  ', 'intel-18.0.5', '',
        #                          'intel-default', '', '']
        #
        # We would next need to get rid of '' list entries and remove trailing
        # white space.
        #
        # This leaves us with:
        #     ['intel-18', 'intel-18.0.5', 'intel-default']

        values_list = [v.strip() for v in uncommented_values_list if v != ""]

        self.assert_values_are_unique(values_list, section, key)
        self.assert_values_do_not_contain_whitespace_or_delimiter(values_list)

        return values_list

    def assert_values_are_unique(self, values_list, section, key):
        """
        Ensures we don't run into a situation like::

            [machine-type-1]
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
                f"Values for '{self.config_filename}'['{section}']['{key}'] "
                "contains duplicates: ", duplicates
            )
            sys.exit(msg)

    def assert_values_do_not_contain_whitespace_or_delimiter(self, values_list):
        """
        Ensure there are no whitespaces in values; that is::

            key:
                value-1 # This is okay.
                value 2 # This is not.

        Parameters:
            values_list (str): A list of values to check for whitespace.

        Raises:
            SystemExit:  If any value contains whitespace.
        """
        values_w_whitespace_or_delim = [_ for _ in values_list
                                        if " " in _ or "_" in _]
        try:
            assert values_w_whitespace_or_delim == []
        except AssertionError:
            es = "es" if len(values_w_whitespace_or_delim) > 1 else "e"
            s = "s" if len(values_w_whitespace_or_delim) == 1 else ""
            msg = self.get_msg_for_list(
                f"The following valu{es} contain{s} whitespace or "
                "the delimiter '_': ",
                values_w_whitespace_or_delim
            )
            sys.exit(msg)

    def get_key_for_section_value(self, section, value):
        """
        Returns the key for which the value corresponds to. For
        example, ``value = intel`` would return
        ``intel-18.0.5-mpich-7.7.6`` for the follwing config::

            [machine-type-1]
            intel-18.0.5-mpich-7.7.6:
                intel-18
                intel
                default-env
            intel-19.0.4-mpich-7.7.6:
                intel-19

        Parameters:
            value (str):  The value to find the key for.

        Returns:
            str:  The key for the given value.
        """

        matched_key = None
        for key in self.config[section].keys():
            values_for_key = self.get_values_for_section_key(section, key)
            if value in values_for_key:
                matched_key = key

        if matched_key is None:
            msg = self.get_formatted_msg("Unable to find value "
                                         f"'{value}' in values "
                                         f"for '{section}'.\n")
            sys.exit(msg)

        return matched_key

    def get_formatted_msg(self, msg, kind="ERROR", extras=""):
        """
        This helper method handles multiline messages, rendering them like::

            +=================================================================+
            |   {kind}:  Unable to find alias or environment name for system
            |            'machine-type-1' in keyword string 'bad_kw_str'.
            |   {extras}
            +=================================================================+

        Parameters:
            msg (str):  The error message, potentially with multiple lines.
            kind (str):  The kind of message being generated, e.g., "ERROR",
                "WARNING", "INFO", etc.
            extras (str):  Any extra text to include after the initial ``msg``.

        Returns:
            str:  The formatted message.
        """
        for idx, line in enumerate(msg.splitlines()):
            if idx == 0:
                msg = f"|   {kind}:  {line}\n"
            elif line != "":
                msg += f"|           {line}\n"
        for extra in extras.splitlines():
            space = "" if extra == "" else "   "
            msg += f"|{space}{extra}\n"
        msg = "\n+" + "="*78 + "+\n" + msg + "+" + "="*78 + "+\n"
        msg = msg.strip()

        return msg

    def get_msg_for_list(self, msg, item_list, kind="ERROR", extras=""):
        """
        Helper function to generate a message using a list. Produces a message
        like the following::

            +=================================================================+
            |   {kind}:  {msg}
            |     - {item_list[0]}
            |     - {item_list[2]}
            |     - ...
            |     - {item_list[n]}
            |   {extras}
            +=================================================================+

        Parameters:
            msg (str):  The error message to print.  Can be multiline.
            item_list (list):  The list of items to print in the error message.
            kind (str):  The kind of message being generated, e.g., "ERROR",
                "WARNING", "INFO", etc.

        Returns:
            str:  The formatted message.
        """
        new_extras = ""
        for item in item_list:
            new_extras += f"  - {item}\n"
        new_extras += extras
        msg = self.get_formatted_msg(msg, kind=kind, extras=new_extras)
        return msg
