from configparserenhanced import ConfigParserEnhanced
import re
from src.load_env_common import LoadEnvCommon
import sys


class EnvKeywordParser(LoadEnvCommon):
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
        build_name (str):  Keyword string to parse environment name from.
        system_name (str):  The name of the system this script is being run
            on.
        supported_envs_filename (str, Path):  The name of the file to load
            the supported environment configuration from.
    """

    def __init__(self, build_name, system_name, supported_envs_filename):
        self._supported_envs = None
        self.supported_envs_filename = supported_envs_filename
        self.build_name = build_name
        self.system_name = system_name
        self.delim = "_"

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
        Parses the :attr:`build_name` and returns the fully qualified
        environment name that is listed as supported for the current
        :attr:`system_name` in the file :attr:`supported_envs_filename`.
        The way this happens is:

            * Gather the list of environment names, sorting them from longest
              to shortest.

                 * March through this list, checking if any of these appear in
                   the :attr:`build_name`.
                 * If an environment name is matched, continue past alias
                   checking.
                 * If not, move on to aliases.

            * Gather the list of aliases, sorting them from longest to
              shortest.

                 * March through this list, checking if any of these appear in
                   the :attr:`build_name`.
                 * Get the environment name with
                   :func:`get_env_name_for_alias`.

            * Run
              :func:`assert_kw_str_versions_for_env_name_components_are_supported`
              to make sure component versions specified in the
              :attr:`build_name` are supported.
            * Run :func:`assert_kw_str_node_type_is_supported` to make sure the
              node type (``serial`` or ``openmp``) specified in the
              :attr:`build_name` is supported on the system.
            * Done

        Returns:
            str:  The fully qualified environment name.
        """
        if not hasattr(self, "_qualified_env_name"):
            matched_env_name = None
            for name in self.env_names:
                env_name_in_build_name = False if re.search(
                    f"(?:^|{self.delim}){name}(?:$|{self.delim})",
                    self.build_name
                ) is None else True

                if env_name_in_build_name:
                    matched_env_name = name
                    print(f"Matched environment name '{name}' in build name "
                          f"'{self.build_name}'.")
                    break

            if matched_env_name is None:
                matched_alias = None
                for alias in self.aliases:
                    alias_in_build_name = False if re.search(
                        f"(?:^|{self.delim}){alias}(?:$|{self.delim})",
                        self.build_name
                    ) is None else True

                    if alias_in_build_name:
                        matched_alias = alias
                        break

                if matched_alias is None:
                    msg = self.get_msg_showing_supported_environments(
                        "Unable to find alias or environment name for system "
                        f"'{self.system_name}' in\nbuild name "
                        f"'{self.build_name}'."
                    )
                    sys.exit(msg)

                matched_env_name = self.get_env_name_for_alias(matched_alias)
                print(f"NOTICE:  Matched alias '{matched_alias}' in build "
                      f"name '{self.build_name}' to environment name "
                      f"'{matched_env_name}'.")

            self._qualified_env_name = (
                f"{self.system_name}{self.delim}{matched_env_name}"
            )

        return self._qualified_env_name

# TODO: Will need to stay, but use get_values_for_section_key from
#       KeywordParser
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
        aliases = [_ for _ in self.supported_envs[self.system_name].values()
                   if _ is not None]
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

# TODO: Will likely need to stay
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
            if a is None or a == "":
                continue

            # The following regex is explained in :func:`get_aliases`.
            uncommented_alias_list = re.findall(
                r"(?:\s*?#.*\n*)*([^#^\n]*)", a
            )
            aliases_for_env = [_.strip().replace("_", "-")
                               for _ in uncommented_alias_list if _ != ""]
            if matched_alias in aliases_for_env:
                matched_index = idx
                break

        if matched_index is None:
            msg = self.get_formatted_msg("Unable to find alias "
                                         f"'{matched_alias}' in aliases "
                                         f"for '{self.system_name}'.\n")
            sys.exit(msg)

        matched_env_name = unsorted_env_names[matched_index]

        return matched_env_name

# TODO: May be covered in KeywordParser
    def get_msg_showing_supported_environments(self, msg, kind="ERROR"):
        """
        Similar to :func:`get_msg_for_list`, except it's a bit more specific.
        Produces an error message like::

            +=================================================================+
            |   {kind}:  {msg}
            |
            |   - Supported Environments for 'machine-type-1':
            |     - intel-18.0.5-mpich-7.7.6
            |       * Aliases:
            |         - intel-18
            |         - intel
            |         - default-env
            |     - intel-19.0.4-mpich-7.7.6
            |       * Aliases:
            |         - intel-19
            |   See {self.supported_envs_filename} for details.
            +=================================================================+

        Parameters:
            msg (str):  The main error message to be displayed.  Can be
                multiline.
            kind (str):  The kind of message being generated, e.g., "ERROR",

                "WARNING", "INFO", etc.

        Returns:
            str:  The formatted message.
        """
        extras = f"\n- Supported Environments for '{self.system_name}':\n"
        for name in sorted(self.env_names):
            extras += f"  - {name}\n"
            aliases_for_env = sorted(
                [a for a in self.aliases
                 if self.get_env_name_for_alias(a) == name]
            )
            extras += ("    * Aliases:\n" if len(aliases_for_env) > 0 else "")
            for a in aliases_for_env:
                extras += (f"      - {a}\n")
        extras += f"\nSee {self.supported_envs_filename} for details."
        msg = self.get_formatted_msg(msg, kind=kind, extras=extras)
        return msg

# TODO: Will likely be needed to check for uniqueness across all aliases for a
#       given system_name
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
            msg = self.get_msg_for_list(
                f"Aliases for '{self.system_name}' contains duplicates:",
                duplicates
            )
            sys.exit(msg)

# TODO: Will likely still be needed after refactor
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

        Raises:
            SystemExit:  If the user requests an unsupported version.
        """
        duplicates = [_ for _ in alias_list if _ in self.env_names]
        try:
            assert duplicates == []
        except AssertionError:
            msg = self.get_msg_for_list(
                f"Alias found for '{self.system_name}' that matches an "
                "environment name:", duplicates
            )
            sys.exit(msg)

# TODO: Covered by KeywordParser
    def assert_aliases_do_not_contain_whitespace(self, alias_list):
        """
        Ensure there are no whitespaces in aliases; that is::

            env-name:
                alias-1 # This is okay.
                alias 2 # This is not.

        Parameters:
            alias_list (str): A list of aliases to check for environemnt names.

        Raises:
            SystemExit:  If the user requests an unsupported version.
        """
        aliases_w_whitespace = [_ for _ in alias_list if " " in _]
        try:
            assert aliases_w_whitespace == []
        except AssertionError:
            es = "es" if len(aliases_w_whitespace) > 1 else ""
            s = "s" if len(aliases_w_whitespace) == 1 else ""
            msg = self.get_msg_for_list(
                f"The following alias{es} contain{s} whitespace:",
                aliases_w_whitespace
            )
            sys.exit(msg)
