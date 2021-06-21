from keywordparser import KeywordParser
import sys


class ConfigKeywordParser(KeywordParser):
    """
    This class accepts a configuration file containing supported configuration
    flags and corresponding options in the following format::

        # supported-config-flags.ini

        [configure-flags]
        use-mpi:
            mpi # the first option is the default if neither is specified in the build name
            no-mpi
        node-type:
            serial
            openmp
        package-enables:
            none   # by default, don't turn anything on
            empire
            sparc  # flags can support more than just two options
            muelu  # e.g., a common configuration used by the MueLu team
            jmgate # e.g., just my personal configuration, not intended to be used by others
        # etc.

    Usage::

        ckp = ConfigKeywordParser("machine-type-5_mpi_serial_empire",
                                  "supported-config-flags.ini")
        selected_options = ckp.selected_options

    Parameters:
        build_name (str):  Keyword string to parse configuration flag/option
            pairs from.
        supported_config_flags_filename (str, Path):  The name of the file to
            load the supported configuration flags and options from.
    """

    def __init__(self, build_name, supported_config_flags_filename):
        self.config_filename = supported_config_flags_filename
        self._build_name = build_name
        self.delimiter = "_"

        self.flag_names = [_ for _ in self.config["configure-flags"].keys()]

    @property
    def build_name(self):
        return self._build_name

    @build_name.setter
    def build_name(self, new_build_name):
        # Clear any data generated from the old build_name
        if hasattr(self, "_complete_config"):
            delattr(self, "_complete_config")
        if hasattr(self, "_selected_options"):
            delattr(self, "_selected_options")
        if hasattr(self, "_flags_selected_by_default"):
            delattr(self, "_flags_selected_by_default")

        self._build_name = new_build_name

    @property
    def complete_config(self):
        if not hasattr(self, "_complete_config"):
            complete_config = ""
            for flag in self.selected_options.keys():
                if type(self.selected_options[flag]) == list:
                    for option in self.selected_options[flag]:
                        complete_config += f"_{option}"
                else:
                    complete_config += f"_{self.selected_options[flag]}"

            self._complete_config = complete_config

        return self._complete_config

    @property
    def selected_options(self):
        if not hasattr(self, "_selected_options"):
            self.parse_selected_options()

        return self._selected_options

    @property
    def flags_selected_by_default(self):
        if not hasattr(self, "_flags_selected_by_default"):
            self.parse_selected_options()

        return self._flags_selected_by_default

    # TODO: UPDATE THIS DOCSTRING
    def parse_selected_options(self):
        """
        Parses the :attr:`build_name` into a dictionary containing the
        supported flags as keys and the corresponding selected options as
        values.
        The way this happens is:

            * Split the :attr:`build_name` by the delimiter `_`.
            * For each supported flag name in the `supported-config-flags.ini`:
                * Find the options for this flag that exist in the
                  :attr:`build_name`.
                * If more than one option is found in the :attr:`build_name`,
                  raise an exception.
                * If no option is found in the :attr:`build_name`, use the
                  default value (first option) from the `.ini` file.
                * If one option is found, use that.

        Returns:
            dict:  A `dict` containing key/value pairs of flags and selected
            options, as found in the :attr:`build_name`.
        """
        if (not hasattr(self, "_selected_options")
                or not hasattr(self, "_flags_selected_by_default")):
            self.assert_options_are_unique_across_all_flags()

            build_name_options = self.build_name.split(self.delimiter)
            selected_options = {}
            flags_selected_by_default = {}

            for flag_name in self.flag_names:
                options, flag_type = self.get_options_and_flag_type_for_flag(flag_name)
                options_in_build_name = [_ for _ in options
                                         if _ in build_name_options]

                if (len(options_in_build_name) > 1
                        and flag_type == "SELECT_ONE"):
                    raise ValueError(self.get_msg_for_list(
                        "Multiple options found in build name for SELECT_ONE "
                        f"flag '{flag_name}':",
                        options_in_build_name
                    ))
                elif (len(options_in_build_name) > 1
                        and flag_type == "SELECT_MANY"):
                    selected_options[flag_name] = options_in_build_name
                    flags_selected_by_default[flag_name] = False
                elif len(options_in_build_name) == 0:
                    selected_options[flag_name] = options[0]
                    flags_selected_by_default[flag_name] = True
                else:
                    selected_options[flag_name] = options_in_build_name[0]
                    flags_selected_by_default[flag_name] = False

            self._selected_options = selected_options
            self._flags_selected_by_default = flags_selected_by_default

    def get_options_and_flag_type_for_flag(self, flag_name):
        """
        A thin wrapper around :func:`get_values_for_section_key` that applies
        special rules to ensure flags specify their type (SELECT_ONE or
        SELECT_MANY) as the first option.

        Returns:
            tuple:  A tuple containing the 1) list of options and 2) flag type,
            respectively.
        """
        options = self.get_values_for_section_key("configure-flags", flag_name)
        flag_type = options[0]
        options = options[1:]

        if flag_type not in ["SELECT_ONE", "SELECT_MANY"]:
            raise ValueError(self.get_formatted_msg(
                f"The options for the '{flag_name}' "
                "flag must begin with either\n'SELECT_ONE' or "
                "'SELECT_MANY'.  For example:",
                extras=(f"\n    {flag_name}:  SELECT_ONE\n"
                        "      option_1\n"
                        "      option_2\n"
                        "\nPlease modify your config file accordingly:\n"
                        f"  '{self.config_filename}'.")
            ))

        return options, flag_type

    def is_default_option(self, option):
        if not hasattr(self, "_default_options"):
            defaults = []
            for flag_name in self.flag_names:
                options, flag_type = self.get_options_and_flag_type_for_flag(
                    flag_name
                )
                defaults.append(options[0])

            self._default_options = defaults

        return option in self._default_options

    def assert_options_are_unique_across_all_flags(self):
        if not hasattr(self, "_options_list"):
            options_list = []
            for flag_name in self.flag_names:
                options, flag_type = self.get_options_and_flag_type_for_flag(
                    flag_name
                )
                options_list += options

            self._options_list = options_list

        duplicates = [_ for _ in set(self._options_list)
                      if self._options_list.count(_) > 1]
        try:
            assert duplicates == []
        except AssertionError:
            these = "these" if len(duplicates) > 1 else "this"
            it = "it" if len(duplicates) > 1 else "they"
            s = "s" if len(duplicates) > 1 else ""
            msg = self.get_msg_for_list(
                "The following options appear for multiple flags in\n"
                f"'{self.config_filename}':",
                duplicates, extras=f"Please change {these} to be unique "
                f"for each flag\nin which {it} appear{s}."
            )
            sys.exit(msg)

    def get_msg_showing_supported_flags(self, msg, kind="ERROR"):
        """
        Similar to :func:`get_msg_for_list`, except it's a bit more specific.
        Produces an error message like::

            +=================================================================+
            |   {kind}:  {msg}
            |     - Supported Flags Are:
            |       - use-mpi
            |         - Options:
            |           - mpi (default)
            |           - no-mpi
            |       - node-type
            |         - Options:
            |           - serial (default)
            |           - openmp
            |   ...
            |   See test_supported_flags_shown_correctly.ini for details.
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
            options, flag_type = self.get_options_and_flag_type_for_flag(flag_name)

            extras += f"  - {flag_name}\n"
            s = "s" if len(options) > 0 else ""
            extras += f"    * Option{s} ({flag_type}):\n"
            for idx, o in enumerate(options):
                default = " (default)" if idx == 0 else ""
                extras += (f"      - {o}{default}\n")

        extras += f"\nSee {self.config_filename} for details."
        msg = self.get_formatted_msg(msg, kind=kind, extras=extras)
        return msg
