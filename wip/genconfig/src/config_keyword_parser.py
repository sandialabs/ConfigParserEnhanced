from src.keyword_parser import KeywordParser


class ConfigKeywordParser(KeywordParser):
    """
    ###########################################################################
    ####################### This needs to be updated ##########################
    ###########################################################################
    This class accepts a configuration file containing supported environments
    on various machines in the following format::

        [machine-type-5]
        intel-18.0.5-mpich-7.7.6:   # Environment name 1
            intel-18    # Alias 1 for ^^^
            intel       # Alias 2 for ^^^
            default-env # ...
        intel-19.0.4-mpich-7.7.6:   # Environment name 2
            intel-19

        [machine-name-2]
        use machine-type-5  # As if contents of machine-type-5 are copy-pasted here

        [sys-3]
        ...

    Usage::

        ekp = EnvKeywordParser("intel-18", "machine-type-5", "supported_envs.ini")
        qualified_env_name = ekp.qualified_env_name
    ###########################################################################
    ###########################################################################

    Parameters:
        build_name (str):  Keyword string to parse configuration flag/option
            pairs from.
        supported_config_flags_filename (str, Path):  The name of the file to
            load the supported environment configuration from.
    """

    def __init__(self, build_name, supported_config_flags_filename):
        self.config_filename = supported_config_flags_filename
        self.build_name = build_name

        self.flag_names = [_ for _ in self.config["DEFAULT"].keys()]

    @property
    def selected_options(self):
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
        if not hasattr(self, "_selected_options"):
            build_name_options = self.build_name.lower().split("_")
            selected_options = {}

            for flag_name in self.flag_names:
                options = self.get_values_for_section_key("DEFAULT", flag_name)
                options = [_.lower() for _ in options]

                options_in_build_name = [_ for _ in options
                                         if _ in build_name_options]
                if len(options_in_build_name) > 1:
                    raise ValueError(self.get_msg_for_list(
                        f"Multiple options for '{flag_name}' found in build "
                        "name:", options_in_build_name
                    ))
                elif len(options_in_build_name) == 0:
                    selected_options[flag_name] = options[0]
                else:
                    selected_options[flag_name] = options_in_build_name[0]

            self._selected_options = selected_options

        return self._selected_options

# TODO: This can be generalized for both EnvKeywordParser and
#       ConfigKeywordParser. Add swapping of 'Environments', 'Aliases', and the
#       .ini file to see for details
    def get_msg_showing_supported_flags(self, msg, kind="ERROR"):
        """
        Similar to :func:`get_msg_for_list`, except it's a bit more specific.
        Produces an error message like::

            +=================================================================+
            |   {kind}:  {msg}
            |
            |   - Supported Flags Are:
            |     - use-mpi
            |       * Options:
            |         - mpi (default)
            |         - no-mpi
            |     - node-type
            |       * Options:
            |         - serial (default)
            |         - openmp
            |     ...
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
        extras = "\n- Supported Flags Are:\n"
        for flag_name in self.flag_names:
            extras += f"  - {flag_name}\n"
            options_for_flag = self.get_values_for_section_key("DEFAULT",
                                                               flag_name)
            extras += ("    * Options:\n" if len(options_for_flag) > 0 else "")
            for idx, o in enumerate(options_for_flag):
                default = " (default)" if idx == 0 else ""
                extras += (f"      - {o}{default}\n")
        extras += f"\nSee {self.config_filename} for details."
        msg = self.get_formatted_msg(msg, kind=kind, extras=extras)
        return msg
