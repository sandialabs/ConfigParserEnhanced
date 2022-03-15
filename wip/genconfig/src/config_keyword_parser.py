from keywordparser import KeywordParser
import re
import sys


class ConfigKeywordParser(KeywordParser):
    """
    This class accepts a configuration file containing supported configuration
    flags and corresponding options in the following format:

    .. code-block:: ini

        # Example
        # -------
        # supported-config-flags.ini
        #
        # For full documentation on formatting, see
        # GenConfig/ini_files/supported-config-flags.ini
        #

        [configure-flags]
        use-mpi:  SELECT_ONE
            mpi # the first option is the default if neither is specified in the build name
            no-mpi
        node-type:  SELECT_ONE
            serial
            openmp
        package-enables:  SELECT_MANY
            no-package-enables   # by default, don't turn anything on
            empire
            sparc  # flags can support more than just two options
            muelu  # e.g., a common configuration used by the MueLu team
            jmgate # e.g., just my personal configuration, not intended to be used by others
        # etc.

    Usage:

    .. code-block:: python

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
        self.delim = "_"

        self.flag_names = [_ for _ in self.config["configure-flags"].keys()]

    @property
    def selected_options_str(self):
        """
        Takes the :attr:`selected_options` dictionary and parses options to
        form a string for use in :class:`GenConfig`. The order in which options
        are added to this string is the order in which they appear in
        ``supported-config-flags.ini``. For example, given the example configuration
        file in the class documentation:

        .. code-block:: python

            >>> ckp = ConfigKeywordParser("mpi_serial_sparc_empire", config_file)
            >>> ckp.selected_options
            {'use-mpi': 'mpi', 'node-type': 'serial'}
            >>> ckp.selected_options_str
            "_mpi_serial_empire_sparc"

        """
        if not hasattr(self, "_selected_options_str"):
            selected_options_str = ""
            for flag in self.selected_options.keys():
                if type(self.selected_options[flag]) == list:
                    for option in self.selected_options[flag]:
                        selected_options_str += f"_{option}"
                else:
                    selected_options_str += f"_{self.selected_options[flag]}"

            self._selected_options_str = selected_options_str

        return self._selected_options_str

    @property
    def selected_options(self):
        """
        This property gives easy access to the output of
        :func:`parse_selected_options`.
        """
        if not hasattr(self, "_selected_options"):
            self.__parse_selected_options()

        return self._selected_options

    def __parse_selected_options(self):
        """
        Parses the :attr:`build_name` into a dictionary containing the
        supported flags as keys and the corresponding selected options as
        values.
        The way this happens is:

            * Split the :attr:`build_name` by the delimiter ``_``.
            * For each supported flag name in the ``supported-config-flags.ini``:

                * Find the options for this flag that exist in the
                  :attr:`build_name`.
                * If more than one option is found in the :attr:`build_name`
                  and the flag type is ``SELECT_ONE``, raise an exception.
                * If no option is found in the :attr:`build_name`, use the
                  default value (first option) from the `.ini` file.
                * If one option is found, use that.
                * If the flag type is ``SELECT_MANY``, aggregate the options
                  present in the build name into a list; the order of the list
                  is the order in which the options appear in the `.ini` file.

        Returns:
            dict:  A `dict` containing key/value pairs of flags and selected
            options, as found in the :attr:`build_name`.
        """
        self.assert_options_are_unique_across_all_flags()
        self.assert_all_build_name_options_are_valid()

        build_name_options = self.build_name.split(self.delim)
        selected_options = {}

        for flag_name in self.flag_names:
            options, flag_type = self.get_options_and_flag_type_for_flag(flag_name)
            options_in_build_name = [_ for _ in options
                                     if _ in build_name_options]

            if (flag_type == "SELECT_ONE"
                    and len(options_in_build_name) > 1):
                raise ValueError(self.get_msg_for_list(
                    "Multiple options found in build name for SELECT_ONE "
                    f"flag '{flag_name}':",
                    options_in_build_name
                ))
            elif (flag_type == "SELECT_MANY"
                    and len(options_in_build_name) > 1):
                selected_options[flag_name] = options_in_build_name
            elif len(options_in_build_name) == 0:
                # Select default option if none in build name
                selected_options[flag_name] = options[0]
            else:  # len(options_in_build_name) == 1 case
                selected_options[flag_name] = options_in_build_name[0]


        self._selected_options = selected_options

    def assert_all_build_name_options_are_valid(self):
        """
        Helper method to assert all options in a build name are valid.
        """
        build_name_options = self.build_name.split(self.delim)

        valid_options = self.get_options_list_for_all_flags()
        invalid_options = [_ for _ in build_name_options
                           if _ not in valid_options and _ != ""]

        if len(invalid_options) > 0:
            err_msg = ("\n\nThe build name contains the following invalid "
                       "options:\n")

            for opt in invalid_options:
                err_msg += f"\n  - {opt}"

            err_msg += ("\n\nValid options can be found in "
                        f"'{self.config_filename}'.")

            raise ValueError(err_msg)

    def get_options_and_flag_type_for_flag(self, flag_name):
        """
        A thin wrapper around :func:`get_values_for_section_key` that applies
        special rules to ensure flags specify their type (``SELECT_ONE`` or
        ``SELECT_MANY``) as the first option.

        Returns:
            tuple:  A tuple containing the list of options and flag type,
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
                        f"  '{str(self.config_filename)}'.")
            ))

        return options, flag_type

    def assert_options_are_unique_across_all_flags(self):
        """
        Ensures options are unique across all flags. So, an exception would be
        raised for the following ``supported-config-flags.ini``:

        .. code-block:: ini

            [configure-flags]
            use-mpi:
                yes
                no
            use-asan:
                yes  # Duplicate of 'yes' in 'use-mpi'!
                no   # Same here
        """
        options_list = self.get_options_list_for_all_flags()
        duplicates = [_ for _ in set(options_list)
                      if options_list.count(_) > 1]
        try:
            assert duplicates == []
        except AssertionError:
            these = "these" if len(duplicates) > 1 else "this"
            it = "it" if len(duplicates) > 1 else "they"
            s = "s" if len(duplicates) > 1 else ""
            msg = self.get_msg_for_list(
                "The following options appear for multiple flags in\n"
                f"'{str(self.config_filename)}':",
                duplicates, extras=f"Please change {these} to be unique "
                f"for each flag\nin which {it} appear{s}."
            )
            sys.exit(msg)

    def get_options_list_for_all_flags(self):
        """
        Get an list of all options for all flags in
        ``supported-config-flags.ini``. This is uses to check for uniqueness in
        :func:`assert_options_are_unique_across_all_flags`.

        Returns:
            list:  A list containing all options for all flags.
        """
        if not hasattr(self, "_options_list"):
            options_list = []
            for flag_name in self.flag_names:
                options, flag_type = self.get_options_and_flag_type_for_flag(
                    flag_name
                )
                options_list += options

            self._options_list = options_list

        return self._options_list

    @property
    def build_name(self):
        """
        This property provides a convenient way to reset any generated
        information if one were to change the :attr:`build_name`. This enables
        the same :class:`ConfigKeywordParser` object to be used to parse
        multiple build names. For example:

        .. code-block:: python

            >>> ckp = ConfigKeywordParser(build_name_1, config_file)
            >>> selected_options_1 = ckp.selected_options
            >>> ckp.build_name = build_name_2  # Resets the `selected_options` property
            >>> selected_options_2 = ckp.selected_options

        Returns:
            str:  The build name given in the class initializer.
        """
        return self._build_name

    @build_name.setter
    def build_name(self, new_build_name):
        # Clear any data generated from the old build_name
        if hasattr(self, "_selected_options_str"):
            delattr(self, "_selected_options_str")
        if hasattr(self, "_selected_options"):
            delattr(self, "_selected_options")

        self._build_name = new_build_name

    def get_msg_showing_supported_flags(self, msg, kind="ERROR"):
        """
        Similar to :func:`get_msg_for_list`, except it's a bit more specific.
        Produces an error message like:

        .. highlight:: none
        .. code-block::

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

        extras += f"\nSee {str(self.config_filename)} for details."
        msg = self.get_formatted_msg(msg, kind=kind, extras=extras)
        return msg
