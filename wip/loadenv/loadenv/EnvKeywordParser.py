import re
from keywordparser import KeywordParser
import os
import sys



class EnvKeywordParser(KeywordParser):
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
        self.config_filename = supported_envs_filename
        self.build_name = build_name
        self.system_name = system_name
        self.delim = "_"

        env_names = [_ for _ in self.config[self.system_name].keys()]
        self.env_names = sorted(env_names, key=len, reverse=True)
        self.aliases = sorted(self.get_aliases(), key=len, reverse=True)


    @property
    def qualified_env_name(self):
        """
        Parses the :attr:`build_name` and returns the fully qualified
        environment name that is listed as supported for the current
        :attr:`system_name` in the file :attr:`config_filename`.
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
                   :func:`get_key_for_section_value`.

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
                env_name_in_build_name = (
                    False
                    if re.search(f"(?:^|{self.delim}){name}(?:$|{self.delim})", self.build_name) is
                    None else True
                    )

                if env_name_in_build_name:
                    matched_env_name = name
                    print(f"Matched environment name '{name}' in build name '{self.build_name}'.")
                    break

            if matched_env_name is None:
                matched_alias = None
                for alias in self.aliases:
                    alias_in_build_name = (
                        False if
                        re.search(f"(?:^|{self.delim}){alias}(?:$|{self.delim})",
                                  self.build_name) is None else True
                        )

                    if alias_in_build_name:
                        matched_alias = alias
                        break

                if matched_alias is None:
                    msg = self.get_msg_showing_supported_environments(
                        "Unable to find alias or environment name for system "
                        f"'{self.system_name}' in\nbuild name '{self.build_name}'."
                        )
                    sys.exit(msg)

                matched_env_name = self.get_key_for_section_value(self.system_name, matched_alias)
                print(
                    f"NOTICE:  Matched alias '{matched_alias}' in build "
                    f"name '{self.build_name}' to environment name '{matched_env_name}'."
                    )

            self._qualified_env_name = f"{self.system_name}{self.delim}{matched_env_name}"

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
        aliases = []
        for env_name in self.config[self.system_name].keys():
            aliases += self.get_values_for_section_key(self.system_name, env_name)

        self.assert_alias_list_values_are_unique(aliases)
        self.assert_aliases_not_equal_to_env_names(aliases)

        return aliases


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

        Raises:
            SystemExit: TODO - explain what condition trips this.
        """
        duplicates = [_ for _ in set(alias_list) if alias_list.count(_) > 1]
        try:
            assert duplicates == []
        except AssertionError:
            msg = self.get_msg_for_list(
                f"Aliases for '{self.system_name}' contains duplicates:", duplicates
                )
            sys.exit(msg)
        return


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
                f"Alias found for '{self.system_name}' that matches an environment name:",
                duplicates,
                )
            sys.exit(msg)
        return


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
            |   See {self.config_filename} for details.
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
        for env_name in sorted(self.env_names):
            extras += f"  - {env_name}\n"
            aliases_for_env = sorted(self.get_values_for_section_key(self.system_name, env_name))
            extras += "    * Aliases:\n" if len(aliases_for_env) > 0 else ""
            for a in aliases_for_env:
                extras += f"      - {a}\n"

        config_filename_rel = os.path.relpath(self.config_filename, ".")

        extras += f"\nSee `{config_filename_rel}` for details on the available environments.\n"
        extras += "\n"
        extras += "To force-load an environment see the guidance in the `--help` output.\n"
        extras += "\n"

        msg = self.get_formatted_msg(msg, kind=kind, extras=extras)
        return msg
