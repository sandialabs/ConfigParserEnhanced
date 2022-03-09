#!/usr/bin/env python3

# All imports must be base python or trilinos-consolidation modules only.
import argparse
from contextlib import redirect_stdout
import getpass
import io
import os
from pathlib import Path
import sys
import textwrap
from typing import List
import uuid

try:
    from configparserenhanced import ConfigParserEnhanced
    from keywordparser import FormattedMsg
    from LoadEnv.load_env import LoadEnv
    from setprogramoptions import SetProgramOptionsCMake
    from src.config_keyword_parser import ConfigKeywordParser
except ImportError:                         # pragma: no cover
    cwd = Path.cwd()                        # pragma: no cover
    gen_config_dir = Path(__file__).parent  # pragma: no cover
    raise ImportError(                      # pragma: no cover
        "Unable to import Python module dependencies. To fix this, please run:\n\n" +
        (f"    $ cd {gen_config_dir}\n" if cwd != gen_config_dir else "") +
        "    $ ./install_reqs\n" +
        ("    $ cd -\n\n" if cwd != gen_config_dir else "\n") +
        "and try again."
    )


class GenConfig(FormattedMsg):
    """
    :class:`GenConfig` is a utility to convert a build name into a set of
    configuration flags or CMake fragment file to be used with CMake. This is
    accomplished using :class:`ConfigKeywordParser` and two configuration
    files:

    1. ``supported-config-flags.ini``: Lists the flags and corresponding
    options supported for parsing within :class:`ConfigKeywordParser`.

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

    2. ``config-specs.ini``: Contains CMake options to use for corresponding
    configurations parsed from :class:`LoadEnv` and
    :class:`ConfigKeywordParser`.

    .. code-block:: ini

        # Example
        # -------
        # config-specs.ini
        #
        # For full documentation on formatting, see
        # GenConfig/ini_files/config-specs.ini
        #

        # Supporting sections are all-caps
        [machine-type-5]
        # Insert machine-type-5 CMake configuration here

        [machine-type-5_MPI|YES]
        # Insert machine-type-5/MPI-enabled CMake configuration here

        # Complete configurations are mixed case
        [machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_mpi_serial_no-package-enables]
        use machine-type-5
        use machine-type-5_MPI|YES
        # Insert CMake configuration, for example:
        opt-set-cmake-var KokkosKernels_sparse_serial_MPI_1_DISABLE BOOL : ON


    Attributes:
        argv:  The command line arguments passed to ``gen_config.py``.
    """

    def __init__(
        self, argv:List[str],
        gen_config_ini_file=(Path(os.path.realpath(__file__)).parent /
                             "src/gen-config.ini"),
        # gen_config_ini_file set here for testing purposes. It is not meant to
        # be changed by the user.
    ):
        if not isinstance(argv, list):
            raise TypeError("GenConfig must be instantiated with a list of "
                            "command line arguments.")

        self.argv = argv
        # final_argv = []
        # for arg in argv:
        #     final_argv += arg.split(" ")
        # self.argv = final_argv
        self.gen_config_ini_file = Path(gen_config_ini_file)
        self._gen_config_config_data = None
        self.config_keyword_parser = None
        self.set_program_options = None
        self.load_env = None
        self.has_been_validated = False

    @property
    def generated_config_flags_str(self):
        """
        String representing the CMake configuration flags specified in
        ``config-specs.ini`` parsed for use in ``bash``. For example, say
        ``config-specs.ini`` contained the following:

        .. code-block:: ini

            [build-name-here]
            opt-set-cmake-var KokkosKernels_sparse_serial_MPI_1_DISABLE BOOL : ON
            opt-set-cmake-var TeuchosCore_show_stack_DISABLE            BOOL : ON

        The output of this property would be::

            >>> gen_config.generated_config_flags_str
            -DKokkosKernels_sparse_serial_MPI_1_DISABLE:BOOL=ON \\
                -DTeuchosCore_show_stack_DISABLE:BOOL=ON

        This could be used with CMake in bash:

        .. code-block:: bash

            $ cmake $(<output-from-generated_config_flags_str>)
            # Which turns into:
            $ cmake -DKokkosKernels_sparse_serial_MPI_1_DISABLE:BOOL=ON \\
                  -DTeuchosCore_show_stack_DISABLE:BOOL=ON
        """
        if not hasattr(self, "_generated_config_flags_str"):
            # These should be set already via validate_config_specs_ini,
            # which comes before this in main(). Don't include in branch
            # coverage, as it's just a safety check.
            if self.set_program_options is None:             # pragma: no cover
                self.load_set_program_options()
            if not self.has_been_validated:                  # pragma: no cover
                self.validate_config_specs_ini()

            options_list = self.set_program_options.gen_option_list(
                self.complete_config, "bash"
            )
            self._generated_config_flags_str = " \\\n    ".join(options_list)

        return self._generated_config_flags_str

    def write_cmake_fragment(self):
        """
        Writes the generated config flags to a CMake fragment file, where the
        path is specified using the ``--cmake-fragment`` flag.

        Returns:
            Path:  The path to the CMake fragment file.
        """
        if not hasattr(self, "_cmake_fragment_file"):
            # These should be set already via validate_config_specs_ini,
            # which comes before this in main(). Don't include in branch
            # coverage, as it's just a safety check.
            if self.set_program_options is None:             # pragma: no cover
                self.load_set_program_options()
            if not self.has_been_validated:                  # pragma: no cover
                self.validate_config_specs_ini()

            cmake_options_list = self.set_program_options.gen_option_list(
                self.complete_config, "cmake_fragment"
            )

            file = self.args.cmake_fragment
            if file.exists():
                if not self.args.yes:
                    response = input(
                        "\n**WARNING** A cmake fragment file containing configuration "
                        "data already exists\nat the location you specified "
                        f"({self.args.cmake_fragment}).\n"
                        "* Would you like to overwrite this file? [y/n] "
                    )
                    while response.lower()[0] not in ["y", "n"]:
                        response = input(
                            "  * Input not recognized. Please enter [y/n]: "
                        )

                    if response.lower()[0] == "n":
                        print("* CMake fragment file not written.")
                        sys.exit(1)

                file.unlink()

            file.parent.mkdir(parents=True, exist_ok=True)

            with open(file, "w") as F:
                F.write("\n".join(cmake_options_list))
            self._cmake_fragment_file = file

            print(f"* CMake fragment file written to: {str(file)}\n")

        return self._cmake_fragment_file

    def list_config_flags(self):
        """
        List the available config flags from ``supported-config-flags.ini``.
        The message will be in the following format:

        .. highlight:: none
        .. code-block::

            +==============================================================================+
            |   INFO:  Please select options from the following.
            |
            |   - Supported Flags Are:
            |     - build-type
            |       * Options (SELECT_ONE):
            |         - debug (default)
            |         - release
            |         - release-debug
            |     - lib-type
            |       * Options (SELECT_ONE):
            |         - static (default)
            |         - shared
            |     - kokkos-arch
            |       * Options (SELECT_MANY):
            |         - no-kokkos-arch (default)
            |         - KNC
            |         - KNL
            |         - SNB
            |         - HSW
            |         - BDW
            |         - SKX
            |         ...
            |
            |   See /path/to/GenConfig/ini_files/supported-config-flags.ini for details.
            +==============================================================================+

        Raises:
            SystemExit:  With the message displaying the available config flags
                from which to choose.
        """
        # This should be defined already via validate_config_specs_ini, which
        # comes before this in main(). Don't include in branch coverage, as
        # it's just a safety check.
        if self.config_keyword_parser is None:               # pragma: no cover
            self.load_config_keyword_parser()

        print(self.config_keyword_parser.get_msg_showing_supported_flags(
            "Please select options from the following.",
            kind="INFO"))
        sys.exit(0)

    def list_configs(self):
        """
        List the available complete configuration names from
        ``config-specs.ini``. The message will be in the following format:

        .. highlight:: none
        .. code-block::

            +==============================================================================+
            |   INFO:  Please select one of the following complete configurations from
            |           /path/to/GenConfig/ini_files/config-specs.ini
            |
            |     - rhel7_cee-cuda-10.1.243-gnu-7.2.0-openmpi-4.0.3_release_shared_Volta70_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-package-enables
            |     - rhel7_cee-cuda-10.1.243-gnu-7.2.0-openmpi-4.0.3_release_static_Volta70_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-package-enables
            |     - rhel7_cee-cuda-10.1.243-gnu-7.2.0-openmpi-4.0.3_release_static_Volta70_no-asan_no-complex_no-fpic_no-mpi_no-pt_no-rdc_no-package-enables
            |     - rhel7_cee-cuda-10.1.243-gnu-7.2.0-openmpi-4.0.3_debug_shared_Volta70_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-package-enables
            |     ...
            |
            +==============================================================================+

        Raises:
            SystemExit:  With the message displaying the available complete
                configs from which to choose.
        """
        if self.load_env is None:
            self.load_load_env()

        sys_name = self.load_env.system_name

        config_specs = ConfigParserEnhanced(
            self.args.config_specs_file
        ).configparserenhanceddata
        complete_configs = [_ for _ in config_specs.sections()
                            if _.startswith(sys_name)]

        print(self.get_msg_for_list(
            "Please select one of the following complete configurations from\n"
            f"{str(self.args.config_specs_file)}\n\n", complete_configs,
            kind="INFO", extras="\n"))
        sys.exit(0)

    @property
    def complete_config(self):
        """
        A string that includes:

            1. The matched environment name from ``LoadEnv``.
            2. The selected config flag options parsed from the
               :attr:`build_name` via the :class:`ConfigKeywordParser`.


        An example of this could be:

        .. code-block:: python

              machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_debug_static
            # ^_______________________________________^ ^__________^
            #  full environment name from LoadEnv        config flag options str from ConfigKeywordParser
        """
        if not hasattr(self, "_complete_config"):
            if self.config_keyword_parser is None:
                self.load_config_keyword_parser()
            if self.load_env is None:
                self.load_load_env()
            self._complete_config = (
                f"{self.load_env.parsed_env_name}"
                f"{self.config_keyword_parser.selected_options_str}"
            )

            print(f"Matched complete configuration '{self._complete_config}'"
                  f"\n  for build name '{self.args.build_name}'.")

        return self._complete_config

    def validate_config_specs_ini(self):
        """
        Runs validation methods to ensure ``config-specs.ini`` has properly
        formatted section names and properly handled operations. For more
        information on these, see
        :func:`validate_config_specs_ini_section_names` and
        :func:`validate_config_specs_ini_operations`.
        """
        self.validate_config_specs_ini_section_names()
        self.validate_config_specs_ini_operations()
        self.has_been_validated = True

    def validate_config_specs_ini_section_names(self):
        """
        Validates each section in ``config-specs.ini`` to ensure the format is
        correct.

        Note:

            ALL-CAPS sections in ``config-specs.ini`` are skipped in validation
            checks, as they are assumed to be supporting sections:

            .. code-block:: ini

                [ALL-CAPS-SECTION]
                # contents here

                [section-to-be-validated]
                use ALL-CAPS-SECTION

        The correct format is:

        .. highlight:: none
        .. code-block::

            <LoadEnv.parsed_env_name><ConfigKeywordParser.selected_options_str>

        For example:

        .. code-block:: python

              rhel7_cee-cuda-10.1.243-gnu-7.2.0-openmpi-4.0.3_release_shared_Volta70_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-package-enables
            # ^_____________________________________________^^____________________________________________________________________________________^
            #           LoadEnv.parsed_env_name               ConfigKeywordParser.selected_options_str
        """
        if self.config_keyword_parser is None:
            self.load_config_keyword_parser()
        if self.load_env is None:
            self.load_load_env()

        ckp = self.config_keyword_parser
        le = self.load_env
        le.args.force = True
        config_specs = ConfigParserEnhanced(
            self.args.config_specs_file
        ).configparserenhanceddata
        supported_systems = [x for x in le.supported_systems_data]

        invalid_sections = []
        sections_with_invalid_systems = []
        for section_name in config_specs.keys():
            if section_name.upper() == section_name:
                continue  # This is just a supporting section

            le.build_name = section_name

            try:
                ckp.set_build_name_system_name(section_name, le.system_name)
            except SystemExit as e:                                     # pragma: no cover
                sections_with_invalid_systems.append(section_name)
                continue

            try:
                selected_options_str = ckp.selected_options_str
            except ValueError as e:                                     # pragma: no cover
                # Don't require coverage of this, as this block of code only
                # exists to give context to any potential ValueErrors in
                # ConfigKeywordParser.
                raise ValueError(self.get_formatted_msg(
                    "When validating sections in\n"
                    f"`{self.args.config_specs_file.name}`,\n"
                    "the following error was encountered for the section name\n"
                    "`{section_name}`:\n"
                    f"{str(e)}"
                ))

            # Silences the LoadEnv diagnostic messages for all the section name
            # matching (i.e. "Matched environment name ...")
            with redirect_stdout(io.StringIO()):
                formatted_section_name = (
                    f"{le.parsed_env_name}{selected_options_str}"
                )
            if formatted_section_name != section_name:
                invalid_sections.append((section_name, formatted_section_name))

        if len(invalid_sections) > 0:
            err_msg = (
                "The following section(s) in your config-specs.ini file\n"
                "should be formatted in the following manner to include "
                "only valid\noptions and to match the order of supported "
                "flags/options in\n"
                f"'{self.args.supported_config_flags_file.name}':\n\n"
                "-  {current_section_name}\n-> {formatted_section_name}\n\n"
            )
            for section_name, formatted_section_name in invalid_sections:
                err_msg += f"-  {section_name}\n-> {formatted_section_name}\n\n"

            raise ValueError(self.get_formatted_msg(
                err_msg, extras=("Please correct these sections in "
                                 f"'{self.args.config_specs_file.name}'.")
            ))

        if len(sections_with_invalid_systems) > 0:
            err_msg = (
                "The following section(s) in your config-specs.ini file\n"
                "do not match any systems listed in\n"
                f"'{le.args.supported_systems_file.name}':\n\n"
            )
            for section_name in sections_with_invalid_systems:
                err_msg += f"-  {section_name}\n"

            raise ValueError(self.get_formatted_msg(
                err_msg, extras=("Please update "
                                 f"'{le.args.supported_systems_file.name}'.")
            ))

        self.load_env.build_name = self.args.build_name
        self.load_env.args.force = self.args.force
        self.config_keyword_parser.set_build_name_system_name(self.args.build_name,
                                                              self.load_env.system_name)

    def validate_config_specs_ini_operations(self):
        """
        Uses the :class:`ConfigParserEnhanced` method
        :func:`assert_file_all_sections_handled` to make sure all operations
        within the ``config-specs.ini`` file have corresponding handlers to be
        processed with :class:`SetProgramOptionsCMake`.
        """
        if self.set_program_options is None:
            self.load_set_program_options()

        # Raise an exception if the .ini file has any unhandled entries
        # Note: If `set_program_options.exception_control_level` is
        #       2 or less then `ValueError` will not be raised but
        #       rather `set_program_options` will return a nonzero value.
        self.set_program_options.assert_file_all_sections_handled()

    def load_config_keyword_parser(self):
        """
        Instantiate a :class:`ConfigKeywordParser` object with this object's
        :attr:`build_name` and ``supported-config-flags.ini``.
        Save the resulting object to ``self.config_keyword_parser``.
        """
        if self.load_env is None:
            self.load_load_env()

        self.config_keyword_parser = ConfigKeywordParser(
            self.args.build_name,
            self.load_env.system_name,
            self.args.supported_config_flags_file,
        )

    def load_set_program_options(self):
        """
        Instantiate a :class:`SetProgramOptions` object with this object's
        ``config-specs.ini``.  Save the resulting object to
        ``self.set_program_options``.
        """
        self.set_program_options = SetProgramOptionsCMake(
            filename=self.args.config_specs_file
        )
        self.set_program_options.exception_control_level = 4

    def load_load_env(self):
        """
        Instantiate a :class:`LoadEnv` object with this object's configuration
        files. Save the resulting object to ``self.load_env``.
        """
        self.load_env = LoadEnv(argv=self.load_env_args)

    @property
    def load_env_args(self):
        """
        Given the :attr:`argv` passed to this :class:`GenConfig` object, return
        just the ``argv`` that applies to :class:`LoadEnv`.
        """
        argv = [
            "--supported-systems", str(self.args.supported_systems_file),
            "--supported-envs", str(self.args.supported_envs_file),
            "--environment-specs", str(self.args.environment_specs_file),
        ]
        argv += ["--force"] if self.args.force else []
        argv += ["--ci-mode"] if self.args.ci_mode else []
        argv += [self.args.build_name]

        return argv

    @property
    def gen_config_config_data(self):
        """
        Parsed data from the ``gen-config.ini`` file.
        """
        if self._gen_config_config_data is None:
            self._gen_config_config_data = ConfigParserEnhanced(
                self.gen_config_ini_file
            ).configparserenhanceddata

        self.__validate_gen_config_config_data()
        return self._gen_config_config_data

    def __validate_gen_config_config_data(self):
        """
        Reads ``gen-config.ini`` and runs some validation:

            * Ensure the file has the sections ``gen-config`` and ``load-env``.
            * Ensure each section has key-value pairs for the required files.
            * Ensure the specified files exist.
        """
        for section in ["gen-config", "load-env"]:
            if not self._gen_config_config_data.has_section(section):
                raise ValueError(self.get_formatted_msg(
                    f"'{str(self.gen_config_ini_file)}' must contain a "
                    f"'{section}' section."
                ))

        # Check paths specified in gen-config.ini
        section_keys = [
            ("gen-config", "supported-config-flags"),
            ("gen-config", "config-specs"),
            ("load-env", "supported-systems"),
            ("load-env", "supported-envs"),
            ("load-env", "environment-specs"),
        ]
        for section, key in section_keys:
            if not self._gen_config_config_data.has_option(section, key):
                raise ValueError(self.get_formatted_msg(
                    f"'{str(self.gen_config_ini_file)}' must contain the "
                    f"following in the '{section}' section:",
                    extras=f"  {key} : /path/to/{key}.ini"
                ))
            value = self._gen_config_config_data[section][key]
            if value == "" or value is None:
                raise ValueError(self.get_formatted_msg(
                    f"The path specified for '{key}' in "
                    f"'{str(self.gen_config_ini_file)}' must be non-empty, e.g.:",
                    extras=f"  {key} : /path/to/{key}.ini"
                ))
            else:
                if not Path(self._gen_config_config_data[section][key]).exists() and not Path(value).is_absolute():
                    self._gen_config_config_data[section][key] = str(
                        self.gen_config_ini_file.parent / value
                    )

            if not Path(self._gen_config_config_data[section][key]).exists():
                raise ValueError(self.get_formatted_msg(
                    f"The file specified for '{key}' in "
                    f"'{str(self.gen_config_ini_file)}' does not exist:",
                    extras=f"  {key} : "
                    f"{self._gen_config_config_data[section][key]}"
                ))

    @property
    def args(self):
        """
        The parsed command line arguments to the script.

        Returns:
            argparse.Namespace:  The parsed arguments.
        """
        if not hasattr(self, "_args"):
            args = self.__parser().parse_args(self.argv)
            gen_config = self.gen_config_config_data["gen-config"]
            if args.supported_config_flags_file is None:
                args.supported_config_flags_file = Path(
                     gen_config["supported-config-flags"]
                ).resolve()
            if args.config_specs_file is None:
                args.config_specs_file = Path(
                    gen_config["config-specs"]
                ).resolve()

            load_env = self.gen_config_config_data["load-env"]
            if args.supported_systems_file is None:
                args.supported_systems_file = Path(
                    load_env["supported-systems"]
                ).resolve()
            if args.supported_envs_file is None:
                args.supported_envs_file = Path(
                    load_env["supported-envs"]
                ).resolve()
            if args.environment_specs_file is None:
                args.environment_specs_file = Path(
                    load_env["environment-specs"]
                ).resolve()

            self._args = args

        return self._args

    def __parser(self):
        """
        Returns:
            argparse.ArgumentParser:  The parser bject with properly configured
            argument options.  This is to be used in conjunction with
            :attr:`args`.
        """
        description = "[ Generate Configuration Utility ]".center(79, "-")
        description += textwrap.dedent(
            """\n\n
            This tool allows you to generate cmake configuration flags by
            passing it a string containing keywords to call out particular
            configuration flag options.
            """
        ).ljust(79)

        examples = """
            NOTE:  In each of the following examples, GenConfig first runs
                   LoadEnv to load the correct environment.

            Run CMake Using Configure Flags from GenConfig:

                source /path/to/gen-config.sh \\
                    <build-name> \\
                    /path/to/src

                NOTE:  /path/to/src must always be specified as the last command
                       line argument UNLESS the --cmake-fragment flag is used.

            Save CMake Fragment File to Use with CMake:

                source /path/to/gen-config.sh \\
                    --cmake-fragment foo.cmake \\
                    <build-name>

                cmake -C foo.cmake /path/to/src
        """
        examples = textwrap.dedent(examples)
        examples = "[ Examples ]".center(79, "-") + "\n\n" + examples

        parser = argparse.ArgumentParser(
            description=description,
            epilog=examples,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        #################### User-facing arguments ####################
        parser.add_argument("build_name", nargs="?", default="", help="The "
                            "keyword string for which you wish to generate the"
                            " configuration flags.")
        parser.add_argument("--list-configs", action="store_true",
                            default=False, help="List the available "
                            "configurations for this system.")
        parser.add_argument("--list-config-flags", action="store_true",
                            default=False, help="List the available "
                            "configuration flags and options.")
        parser.add_argument("--cmake-fragment", action="store", default=None,
                            type=lambda p: Path(p).resolve(), help="Output a "
                            "cmake fragment that will give you an identical "
                            "set of configuration flags as when using this "
                            "tool.")
        parser.add_argument("-f", "--force", action="store_true",
                            default=False, help="Forces gen_config to use the "
                            "system name specified in the build_name rather "
                            "than the system name matched via the hostname "
                            "and the supported-systems.ini file "
                            "(see LoadEnv).")
        parser.add_argument("-y", "--yes", action="store_true",
                            default=False, help="Automatically say yes to any "
                            "yes/no prompts.")
        parser.add_argument(
            "--ci-mode", action="store_true",
            default=False,
            help="Causes gen-config.sh to modify your current shell rather "
                 "than putting you in a interactive subshell.")

        config_files = parser.add_argument_group(
            "configuration file overmachine-name-1s"
        )
        config_files.add_argument("--supported-config-flags", default=None,
                                  dest="supported_config_flags_file",
                                  action="store",
                                  type=lambda p: Path(p).resolve(),
                                  help="Path to ``supported-config-flags.ini``"
                                  ".  Overmachine-name-1s loading the file specified in "
                                  "``gen-config.ini``.")
        config_files.add_argument("--config-specs",
                                  dest="config_specs_file",
                                  action="store", default=None,
                                  type=lambda p: Path(p).resolve(),
                                  help="Path to ``config-specs.ini``.  "
                                  "Overmachine-name-1s loading the file specified in "
                                  "``gen-config.ini``.")
        config_files.add_argument("--supported-systems",
                                  dest="supported_systems_file",
                                  action="store", default=None,
                                  type=lambda p: Path(p).resolve(),
                                  help="Path to ``supported-systems.ini``.  "
                                  "Overmachine-name-1s loading the file specified in "
                                  "``gen-config.ini``.")
        config_files.add_argument("--supported-envs", default=None,
                                  dest="supported_envs_file", action="store",
                                  type=lambda p: Path(p).resolve(),
                                  help="Path to ``supported-envs.ini``.  "
                                  "Overmachine-name-1s loading the file specified in "
                                  "``gen-config.ini``.")
        config_files.add_argument("--environment-specs",
                                  dest="environment_specs_file",
                                  action="store", default=None,
                                  type=lambda p: Path(p).resolve(),
                                  help="Path to ``environment-specs.ini``.  "
                                  "Overmachine-name-1s loading the file specified in "
                                  "``gen-config.ini``.")

        ########## Suppressed arguments intended for gen-config.sh ##########
        parser.add_argument("--output-load-env-args-only", action="store_true",
                            default=False, help=argparse.SUPPRESS)
                            # help="Based on the command line arguments passed to "
                            # "GenConfig, write the corresponding command line "
                            # "arguments for LoadEnv to stdout. This "
                            # "is a helper flag to be used by gen-config.sh, not "
                            # "intended to be used by the user.")

        parser.add_argument("--bash-cmake-args-location",
                            action="store",
                            default=None,
                            type=lambda p: Path(p).resolve(),
                            help=argparse.SUPPRESS)
                            # help="Path to load-matching-env file in /tmp/$USER/")

        return parser


def main(argv):
    """
    DOCSTRING
    """
    gc = GenConfig(argv)

    # To support gen-config.sh, we must conditionally output the load-env.sh args
    # and exit early
    if gc.args.output_load_env_args_only:
        print(" ".join(gc.load_env_args))
        sys.exit(0)

    gc.validate_config_specs_ini()
    if gc.args.list_config_flags:
        gc.list_config_flags()
    if gc.args.list_configs:
        gc.list_configs()

    # Handle generation of configure output
    if gc.args.cmake_fragment is not None:
        gc.write_cmake_fragment()
    else:  # Output bash cmake args to be used by gen-config.sh...
        #
        # * gen_config.py saves generated cmake args to, i.e.,
        #     /tmp/$USER/bash_cmake_args_from_gen_config_82dk2h
        #
        # * gen_config.py saves this location to /tmp/$USER/.bash_cmake_args_file_loc
        #
        # * gen-config.sh reads and uses the cmake args in the following manner:
        #
        #       # gen-config.sh
        #       bash_cmake_args_file=$(cat /tmp/$USER/.bash_cmake_args_file_loc)
        #       cmake $(cat $bash_cmake_args_file) /path/to/src
        #
        user = getpass.getuser()
        Path(f"/tmp/{user}").mkdir(parents=True, exist_ok=True)

        if gc.args.bash_cmake_args_location is not None:
            with open(gc.args.bash_cmake_args_location, "w") as F:
                F.write(gc.generated_config_flags_str)



if __name__ == "__main__":  # pragma: no cover
    main(sys.argv[1:])      # pragma: no cover
