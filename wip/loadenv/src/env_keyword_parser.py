import re
import sys
from configparserenhanced import ConfigParserEnhanced
from pathlib import Path


class EnvKeywordParser:
    """
    This class accepts a configuration file containing supported environments
    on various machines in the following format::

        [machine-type-1]
        intel-18.0.5-mpich-7.7.6:   # Environment name 1
            intel-18    # Alias 1 for ^^^
            intel       # Alias 2 for ^^^
            default-env # ...
        intel-19.0.4-mpich-7.7.6:   # Environment name 2
            intel-19

        [mutrino]
        use machine-type-1  # As if contents of machine-type-1 are copy-pasted here

        [sys-3]
        ...

    Usage::

        ekp = EnvKeywordParser("intel-18", "machine-type-1", "supported_envs.ini")
        qualified_env_name = ekp.qualified_env_name

    Parameters:
        keyword_str (str):  Keyword string to parse environment name from.
        system_name (str):  The name of the system this script is being run
            on.
        supported_envs_filename (str, Path):  The name of the file to load
            the supported environment configuration from.
    """

    def __init__(self, keyword_str, system_name, supported_envs_filename):
        self._supported_envs = None
        self.supported_envs_filename = supported_envs_filename
        self.keyword_str = keyword_str.replace("_", "-")
        self.system_name = system_name

        env_names = [_ for _ in self.supported_envs[self.system_name].keys()]
        self.env_names = sorted(env_names, key=len, reverse=True)
        self.aliases = sorted(self.get_aliases(), key=len, reverse=True)

    @property
    def supported_envs(self):
        """
        Gets the :class:`ConfigParserEnhancedData` object with
        :attr:`supported_envs_filename` loaded.

        Returns:
            ConfigParserEnhancedData:  A :class:`ConfigParserEnhancedData`
            object with `supported_envs_filename` loaded.
        """
        self._supported_envs = ConfigParserEnhanced(
                self.supported_envs_filename
            ).configparserenhanceddata
        return self._supported_envs

    @property
    def qualified_env_name(self):
        """
        Parses the :attr:`keyword_str` and returns the fully qualified
        environment name that is listed as supported for the current
        :attr:`system_name` in the file :attr:`supported_envs_filename`.
        The way this happens is:

            * Gather the list of environment names, sorting them from longest
              to shortest.

                 * March through this list, checking if any of these appear in the
                   :attr:`keyword_str`.
                 * If an environment name is matched, continue past alias
                   checking.
                 * If not, move on to aliases.

            * Gather the list of aliases, sorting them from longest to
              shortest.

                 * March through this list, checking if any of these appear in the
                   :attr:`keyword_str`.
                 * Get the environment name with :func:`get_env_name_for_alias`.

            * Run
              :func:`assert_kw_str_versions_for_env_name_components_are_supported`
              to make sure component versions specified in the
              :attr:`keyword_str` are supported.
            * Done

        Returns:
            str:  The fully qualified environment name.
        """
        matched_env_name = None
        for name in self.env_names:
            if name in self.keyword_str:
                matched_env_name = name
                break

        if matched_env_name is None:
            matched_alias = None
            for alias in self.aliases:
                if alias in self.keyword_str:
                    matched_alias = alias
                    break

            if matched_alias is None:
                err_msg = self.get_err_msg_showing_supported_environments(
                    "Unable to find alias or environment name for system "
                    f"'{self.system_name}' in\nkeyword string "
                    f"'{self.keyword_str}'"
                )
                sys.exit(err_msg)

            matched_env_name = self.get_env_name_for_alias(matched_alias)

        # i.e. 'intel' could be a match in 'intel-20' even though
        #      'intel-20' is not supported.
        self.assert_kw_str_versions_for_env_name_components_are_supported(
            matched_env_name
        )

        self._qualified_env_name = f"{self.system_name}-{matched_env_name}"

        return self._qualified_env_name

    def get_aliases(self):
        """
        Gets the aliases for the current :attr:`system_name` and returns them
        in list form. This also runs
        :func:`assert_alias_list_values_are_unique` and
        :func:`assert_aliases_not_equal_to_env_names` on the alias list.

        Returns:
            list:  The filtered and validated list of aliases for the current
            :attr:`system_name`.
        """
        # e.g. aliases = ['\ngnu  # GNU\ndefault-env # The default',
        #                 '\ncuda-gnu\ncuda']
        aliases = [_ for _ in self.supported_envs[self.system_name].values()]
        alias_str = "\n".join(aliases)

        uncommented_alias_list = re.findall(
            r"(?:\s*?#.*\n*)*([^#^\n]*)", alias_str
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
        #     # Comment\nintel 18  # Comment\n intel-18.0.5\nintel_default # id
        #
        # re.findall would return ['intel 18  ', 'intel-18.0.5', '',
        #                          'intel_default', '', '']
        #
        # We would next need to get rid of '' list entries and remove trailing
        # white space, and replace '_' characters with '-'.
        #
        # This leaves us with:
        #     ['intel-18', 'intel-18.0.5', 'intel-default']

        alias_list = [a.strip().replace("_", "-")
                      for a in uncommented_alias_list if a != ""]

        self.assert_alias_list_values_are_unique(alias_list)
        self.assert_aliases_not_equal_to_env_names(alias_list)
        self.assert_aliases_do_not_contain_whitespace(alias_list)

        return alias_list

    def get_env_name_for_alias(self, matched_alias):
        """
        Returns the environment name for which the alias specifies. For
        example, ``matched_alias = intel`` would return
        ``intel-18.0.5-mpich-7.7.6`` for the follwing configuration::

            [machine-type-1]
            intel-18.0.5-mpich-7.7.6:
                intel-18
                intel
                default-env
            intel-19.0.4-mpich-7.7.6:
                intel-19

        Parameters:
            matched_alias (str):  The alias to find the environment name for.

        Returns:
            str:  The environment name for the alias.
        """
        unsorted_env_names = [_ for _ in
                              self.supported_envs[self.system_name].keys()]

        unparsed_aliases = [_ for _ in
                            self.supported_envs[self.system_name].values()]

        matched_index = None
        for idx, a in enumerate(unparsed_aliases):
            # Regex explained in :func:`get_aliases`
            uncommented_alias_list = re.findall(
                r"(?:\s*?#.*\n*)*([^#^\n]*)", a
            )
            aliases_for_env = [_.strip().replace("_", "-")
                               for _ in uncommented_alias_list if _ != ""]
            if matched_alias in aliases_for_env:
                matched_index = idx
                break

        if matched_index is None:
            msg = ("\n+" + "="*78 + "+\n"
                   f"|   ERROR:  Unable to find alias '{matched_alias}' in "
                   f"aliases for '{self.system_name}'.\n")
            msg += ("+" + "="*78 + "+\n")
            sys.exit(msg)

        matched_env_name = unsorted_env_names[matched_index]

        return matched_env_name

    def get_err_msg_for_list(self, err_msg, item_list):
        """
        Helper function to generate an error message using a list. Produces a
        message like the following::

            +=================================================================+
            |   ERROR:  {msg}.
            |     - {item_list[0]}
            |     - {item_list[1]}
            |     - ...
            |     - {item_list[n]}
            +=================================================================+

        Parameters:
            err_msg (str):  The error message to print.  Can be multiline.
            item_list (list):  The list of items to print in the error message.

        Returns:
            str:  The formatted error message.
        """
        msg = ("\n+" + "="*78 + "+\n" +
               self.get_formatted_multiline_err_msg(err_msg))
        for item in item_list:
            msg += f"|     - {item}\n"
        msg += ("+" + "="*78 + "+\n")

        return msg

    def get_err_msg_showing_supported_environments(self, err_msg):
        """
        Similar to :func:`get_err_msg_for_list`, except it's a bit more
        specific. Produces an error message like::

            +=================================================================+
            |   ERROR:  {err_msg}.
            |   - Supported Environments for 'machine-type-1':
            |     - intel-18.0.5-mpich-7.7.6
            |       * Aliases:
            |         - intel-18
            |         - intel
            |         - default-env
            |     - intel-19.0.4-mpich-7.7.6
            |       * Aliases:
            |         - intel-19
            +=================================================================+

        Parameters:
            err_msg (str):  The main error message to be displayed.  Can be
            multiline.

        Returns:
            str:  The formatted error message.
        """
        msg = (
            "\n+" + "="*78 + "+\n" +
            self.get_formatted_multiline_err_msg(err_msg) +
            f"|   - Supported Environments for '{self.system_name}':\n"
        )

        for name in self.env_names:
            msg += f"|     - {name}\n"

            aliases_for_env = [a for a in self.aliases
                               if self.get_env_name_for_alias(a) == name]
            msg += ("|       * Aliases:\n" if len(aliases_for_env) > 0 else "")
            for a in aliases_for_env:
                msg += ("|" + " "*9 + f"- {a}\n")

        msg += ("+" + "="*78 + "+\n")

        return msg

    def get_formatted_multiline_err_msg(self, err_msg):
        """
        This helper method handles multiline error messages, rendering them
        like::

            |   ERROR:  Unable to find alias or environment name for system
            |           'machine-type-1' in keyword string 'bad_kw_str'.

        Parameters:
            err_msg (str):  The error message, with potentially multiple lines.

        Returns:
            str:  The formatted error message.
        """
        err_msg_lines = err_msg.split("\n")
        for idx, line in enumerate(err_msg_lines):
            period = "." if idx == len(err_msg_lines)-1 else ""
            if idx == 0:
                msg = f"|   ERROR:  {line}{period}\n"
            else:
                msg += f"|           {line}{period}\n"

        return msg

    def assert_alias_list_values_are_unique(self, alias_list):
        """
        Ensures we don't run into a situation like::

            [machine-type-1]
            intel-18.0.5-mpich-7.7.6:
                intel-18
                intel
                default-env
            intel-19.0.4-mpich-7.7.6:
                intel-19
                intel     # Duplicate of 'intel' in the above section!

        Called automatically by :func:`get_aliases`.

        Parameters:
            alias_list (str): A list of aliases to check for duplicates.
        """
        duplicates = [_ for _ in set(alias_list) if alias_list.count(_) > 1]
        try:
            assert duplicates == []
        except AssertionError:
            msg = self.get_err_msg_for_list(
                f"Aliases for '{self.system_name}' contains duplicates",
                duplicates
            )
            sys.exit(msg)

    def assert_aliases_not_equal_to_env_names(self, alias_list):
        """
        Ensures we don't run into a situation like::

            [machine-type-1]
            intel-18.0.5-mpich-7.7.6:
                intel-18
                intel
                default-env
            intel-19.0.4-mpich-7.7.6:
                intel-19
                intel-18.0.5-mpich-7.7.6  # Same as the other environment name!

        Called automatically by :func:`get_aliases`.

        Parameters:
            alias_list (str): A list of aliases to check for environemnt names.
        """
        duplicates = [_ for _ in alias_list if _ in self.env_names]
        try:
            assert duplicates == []
        except AssertionError:
            msg = self.get_err_msg_for_list(
                f"Alias found for '{self.system_name}' that matches an "
                "environment name", duplicates
            )
            sys.exit(msg)

    def assert_aliases_do_not_contain_whitespace(self, alias_list):
        aliases_w_whitespace = [_ for _ in alias_list if " " in _]
        try:
            assert aliases_w_whitespace == []
        except AssertionError:
            es = "es" if len(aliases_w_whitespace) > 1 else ""
            s = "s" if len(aliases_w_whitespace) == 1 else ""
            msg = self.get_err_msg_for_list(
                f"The following alias{es} contain{s} whitespace",
                aliases_w_whitespace
            )
            sys.exit(msg)

    def assert_kw_str_versions_for_env_name_components_are_supported(
        self, matched_env_name
    ):
        """
        Makes sure that component versions and their combinations are supported
        by the current system. This is best shown by example. Consider the
        following configuration::

            [machine-type-1]
            intel-18.0.5-mpich-7.7.6:
                intel-18
                intel
                default-env
            intel-19.0.4-mpich-7.7.6:
                intel-19

        Now consider ``keyword_str = 'intel-20'``. The usual method for
        matching the environment name would find that `intel` is in the
        :attr:`keyword_str`, and subsequently match the
        :attr:`qualified_env_name` as ``intel-18.0.5-mpich-7.7.6``. This method
        matches ``intel-20`` in the :attr:`keyword_str` and checks if it exists
        in any of the supported environment names. Since `intel-20` does not,
        an exception is raised.

        Similarly, consider ``keyword_str = 'intel-19-mpich-7.2'``. The usual
        method would find that ``intel-19`` is in the :attr:`keyword_str`, and
        match the :attr:`qualified_env_name` as ``intel-19.0.4-mpich-7.7.6``.
        This method matches both ``intel-19`` and ``mpich-7.2`` in the
        :attr:`keyword_str` and checks if both exist in any of the supported
        environment names.  Since ``mpich-7.2`` does not, an exception is
        raised.

        Finally, consider the following configuration::

            [machine-type-4]
                arm-20.0-openmpi-4.0.2:
                    arm-20.0
                    arm
                    default-env
                arm-21.0-openmpi-4.0.3:
                    arm-20.1

        If we have ``keyword_str = 'arm-21.0-openmpi-4.0.2``, this method
        would see that this version combination of ``arm`` and ``openmpi`` is
        not supported and raise an exception.

        Parameters:
            str:  The matched environment name to check component versions for.
        """
        # e.g. `intel-mpich` has two components, each with a version number
        matched_components = matched_env_name.split("-")
        regex_list = [f"{mc}[^A-Z^a-z]*" for mc in matched_components]
        versioned_components = re.findall(
            f"({'|'.join(regex_list)})(?:-|$)", self.keyword_str
        )
        # Regex Explanation
        # =================
        # (intel[^A-Z^a-z']*|mpich[^A-Z^a-z']*)(?:-|$)
        #  ^^^^^^^^^^^^^^^^^^^^^^^             ^^^^^^^
        #  |                |                  |
        #  |                |                  Non-matching group. The previous
        #  |                |                  pattern is followed by either a
        #  |                |                  '-' or end of string '$'.
        #  |                |
        #  |                Or mpich, followed by... -|
        #  |                                          |
        #  intel, followed by 0 or more <-------------|
        #  non-alphabetical characters
        #
        # So, given the string:
        #     intel-20-mpich-7.1.3
        #
        # re.findall would return ['intel-20', 'mpich-7.1.3']

        # Make sure each component version is supported
        for vc in versioned_components:
            try:
                assert [en for en in self.env_names if vc in en] != []
            except AssertionError:
                sys.exit(
                    self.get_err_msg_showing_supported_environments(
                        f"'{vc}' is not a supported version"
                    )
                )

        # Make sure the component versions combination is supported
        versioned_match = "-".join(versioned_components)
        try:
            assert [en for en in self.env_names if versioned_match in en] != []
        except AssertionError:
            sys.exit(self.get_err_msg_showing_supported_environments(
                f"'{versioned_match}' is not a supported version"
            ))
