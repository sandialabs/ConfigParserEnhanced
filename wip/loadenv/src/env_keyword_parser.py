from configparserenhanced import ConfigParserEnhanced
from pathlib import Path
import re
from src.load_env_common import LoadEnvCommon
import sys
import textwrap


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
        self.build_name = build_name.replace("_", "-")
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
                if name in self.build_name:
                    matched_env_name = name
                    print(f"Matched environment name '{name}' in build name "
                          f"'{self.build_name}'.")
                    break

            if matched_env_name is None:
                matched_alias = None
                for alias in self.aliases:
                    if alias in self.build_name:
                        matched_alias = alias
                        break

                if matched_alias is None:
                    msg = self.get_msg_showing_supported_environments(
                        "Unable to find alias or environment name for system "
                        f"'{self.system_name}' in\nkeyword string "
                        f"'{self.build_name}'."
                    )
                    sys.exit(msg)

                matched_env_name = self.get_env_name_for_alias(matched_alias)
                print(f"Matched alias '{matched_alias}' in build name "
                      f"'{self.build_name}' to environment name "
                      f"'{matched_env_name}'.")

            self.assert_kw_str_versions_for_env_name_components_are_supported(
                matched_env_name
            )
            self.assert_kw_str_node_type_is_supported(matched_env_name)

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
            msg = self.get_formatted_msg("Unable to find alias "
                                         f"'{matched_alias}' in aliases "
                                         f"for '{self.system_name}'.\n")
            sys.exit(msg)

        matched_env_name = unsorted_env_names[matched_index]

        return matched_env_name

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
        for name in self.env_names:
            extras += f"  - {name}\n"
            aliases_for_env = [a for a in self.aliases
                               if self.get_env_name_for_alias(a) == name]
            extras += ("    * Aliases:\n" if len(aliases_for_env) > 0 else "")
            for a in aliases_for_env:
                extras += (f"      - {a}\n")
        extras += f"\nSee {self.supported_envs_filename} for details."
        msg = self.get_formatted_msg(msg, kind=kind, extras=extras)
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
            msg = self.get_msg_for_list(
                f"Aliases for '{self.system_name}' contains duplicates:",
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

    def get_versioned_components_from_str(self, input_str, str_to_check):
        """
        When parsing a :attr:`build_name`, we split on delimiters; however,
        we'd actually like to treat versioned components in the
        :attr:`build_name` as single 'words'.  For instance, we'd like to treat
        ``intel-19.0.4`` as a single word, instead of splitting it into
        ``intel`` and ``19.0.4``.  This routine creates those compound words
        from the naive split.

        Parameters:
            input_str (str): The string you would like to split and create
                versioned components from.
            str_to_check (str): This routine will only keep versioned
                components that are also found in this string.

        Returns:
            list:  A list of strings containing the versioned components.
        """
        matched_components = input_str.split("-")
        regex_list = [f"{mc}[^A-Z^a-z]*" for mc in matched_components]
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
        versioned_components = re.findall(
            f"({'|'.join(regex_list)})(?:-|$)", str_to_check
        )
        return versioned_components

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

        Now consider ``build_name = 'intel-20'``. The usual method for
        matching the environment name would find that `intel` is in the
        :attr:`build_name`, and subsequently match the
        :attr:`qualified_env_name` as ``intel-18.0.5-mpich-7.7.6``. This method
        matches ``intel-20`` in the :attr:`build_name` and checks if it exists
        in any of the supported environment names. Since `intel-20` does not,
        an exception is raised.

        Similarly, consider ``build_name = 'intel-19-mpich-7.2'``. The usual
        method would find that ``intel-19`` is in the :attr:`build_name`, and
        match the :attr:`qualified_env_name` as ``intel-19.0.4-mpich-7.7.6``.
        This method matches both ``intel-19`` and ``mpich-7.2`` in the
        :attr:`build_name` and checks if both exist in any of the supported
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

        If we have ``build_name = 'arm-21.0-openmpi-4.0.2``, this method
        would see that this version combination of ``arm`` and ``openmpi`` is
        not supported and raise an exception.

        Parameters:
            matched_env_name (str):  The matched environment name to check
                component versions for.

        Raises:
            SystemExit:  If the user requests an unsupported version.
        """
        versioned_components = self.get_versioned_components_from_str(
            matched_env_name, self.build_name
        )
        vcs_in_env_names = []
        for env in self.env_names:
            vcs_in_env_names += [all([vc in env for vc in
                                      versioned_components])]
        if not any(vcs_in_env_names):
            msg = ""
            if len(versioned_components) == 1:
                msg = f"'{versioned_components[0]}' is not supported."
            elif len(versioned_components) == 2:
                msg = (f"'{versioned_components[0]}' and "
                       f"'{versioned_components[1]}' are not supported "
                       "together.")
            else:
                for i in range(len(versioned_components) - 1):
                    msg += f"'{versioned_components[i]}', "
                msg += (f"and '{versioned_components[-1]}' are not supported "
                        "together.")
            msg = textwrap.fill(msg)
            sys.exit(self.get_msg_showing_supported_environments(msg))

    def assert_kw_str_node_type_is_supported(self, matched_env_name):
        """
        Ensure the node type (``serial`` or ``openmp``) specified in the
        :attr:`build_name` is actually supported on the system.  For instance,
        if the user specified ``intel-serial``, we don't want to match an alias
        of ``intel`` and map that back to an ``openmp`` environment.

        Parameters:
            matched_env_name (str):  The matched environment name to check for
                the presence of the node type.

        Raises:
            SystemExit:  If the user requests an unsupported node type.
        """
        build_name_vcs = self.get_versioned_components_from_str(
            self.build_name, self.build_name
        )
        matched_env_name_vcs = self.get_versioned_components_from_str(
            matched_env_name, matched_env_name
        )

        if "openmp" in build_name_vcs and "serial" in matched_env_name_vcs:
            sys.exit(self.get_msg_showing_supported_environments(
                "'openmp' was specified in the build name, but only the "
                "'serial'\nnode type is supported for your selected "
                "environment"
            ))
        if "serial" in build_name_vcs and "openmp" in matched_env_name_vcs:
            sys.exit(self.get_msg_showing_supported_environments(
                "'serial' was specified in the build name, but only the "
                "'openmp'\nnode type is supported for your selected "
                "environment"
            ))
        if (any(["cuda" in _ for _ in matched_env_name_vcs]) and
            any([_ in build_name_vcs for _ in ["serial", "openmp"]])):
            sys.exit(self.get_msg_showing_supported_environments(
                "The 'serial' and 'openmp' node types are not applicable to "
                "CUDA\nenvironments"
            ))
