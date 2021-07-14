#!/usr/bin/env python3

# All imports must be base python or trilinos-consolidation modules only.
import argparse
from configparserenhanced import ConfigParserEnhanced
from contextlib import redirect_stdout
import getpass
import io
from keywordparser import FormattedMsg
from LoadEnv.load_env import LoadEnv
import os
from pathlib import Path
import re
from setprogramoptions import SetProgramOptionsCMake
from src.config_keyword_parser import ConfigKeywordParser
import sys
import textwrap
from typing import List
import uuid


class GenConfig(FormattedMsg):
    """
    Insert description here.

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
        if not hasattr(self, "_generated_config_flags_str"):
            if self.set_program_options is None:
                self.load_set_program_options()
            if not self.has_been_validated:
                self.validate_config_specs_ini()

            options_list = self.set_program_options.gen_option_list(
                self.complete_config, "bash"
            )
            self._generated_config_flags_str = " \\\n    ".join(options_list)

        return self._generated_config_flags_str

    def write_cmake_fragment(self):
        """
        Returns:
            Path:  The path to the cmake fragment that was written, either the
            default or whatever the user requested with ``--cmake-fragment``.
        """
        if not hasattr(self, "_cmake_fragment_file"):
            if self.set_program_options is None:
                self.load_set_program_options()
            if not self.has_been_validated:
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

            print(f"* Cmake fragment file written to: {str(file)}")

        return self._cmake_fragment_file

    def list_config_flags(self):
        """
        List the available config flags form ``supported-config-flags.ini``.

        Raises:
            SystemExit:  With the message displaying the available config flags
            from which to choose.
        """
        if self.config_keyword_parser is None:
            self.load_config_keyword_parser()
        sys.exit(
            self.config_keyword_parser.get_msg_showing_supported_flags(
                "Please select one of the following.",
                kind="INFO"
            )
        )

    @property
    def complete_config(self):
        """
        The selected config flag options name parsed from the
        :attr:`build_name` via the :class:`ConfigKeywordParser`.
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

        invalid_sections = []
        for section_name in config_specs.keys():
            if section_name.upper() == section_name:
                continue  # This is just a supporting section

            le.build_name = section_name
            ckp.build_name = section_name
            try:
                selected_options_str = ckp.selected_options_str
            except ValueError as e:
                raise ValueError(self.get_formatted_msg(
                    "When validating sections in\n"
                    f"`{self.args.config_specs_file.name}`,\n"
                    "the following error was encountered:\n"
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

        self.load_env.build_name = self.args.build_name
        self.load_env.args.force = self.args.force
        self.config_keyword_parser.build_name = self.args.build_name
        self.has_been_validated = True

    def load_config_keyword_parser(self):
        """
        Instantiate an :class:`ConfigKeywordParser` object with this object's
        :attr:`build_name` and ``supported-config-flags.ini``.
        Save the resulting object as :attr:`config_keyword_parser`.
        """
        if self.config_keyword_parser is None:
            self.config_keyword_parser = ConfigKeywordParser(
                self.args.build_name,
                self.args.supported_config_flags_file,
            )

    def load_set_program_options(self):
        """
        Instantiate a :class:`SetProgramOptions` object with this object's
        ``config-specs.ini``.  Save the resulting object as
        :attr:`set_program_options`.
        """
        if self.set_program_options is None:
            self.set_program_options = SetProgramOptionsCMake(
                filename=self.args.config_specs_file
            )

    def load_load_env(self):
        """
        Instantiate a :class:`LoadEnv` object with this object's configuration
        files. Save the resulting object as :attr:`load_env`.
        """
        if self.load_env is None:
            self.load_env = LoadEnv(argv=self.load_env_args)

    @property
    def load_env_args(self):
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
        Parse the ``gen-config.ini`` file and store the corresponding
        ``configparserenhanceddata`` object as :attr:`gen_config_config_data`.
        """
        if self._gen_config_config_data is None:
            self._gen_config_config_data = ConfigParserEnhanced(
                self.gen_config_ini_file
            ).configparserenhanceddata

        self.validate_gen_config_config_data()
        return self._gen_config_config_data

    def validate_gen_config_config_data(self):
        if self._gen_config_config_data is None:
            return

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
                if not Path(value).is_absolute():
                    self._gen_config_config_data[section][key] = str(
                        self.gen_config_ini_file.parent / value
                    )

            if not Path(self._gen_config_config_data[section][key]).exists():
                raise ValueError(self.get_formatted_msg(
                    f"The file specified for '{key}' in "
                    f"'{str(self.gen_config_ini_file)}' does not exist:",
                    extras=f"  {key} : "
                    f"{self._gen_config_config_data[section][key]}.ini"
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

            Run CMake Using Configure Flags from GenConfig::

                source /path/to/gen-config.sh \\
                    <build-name> \\
                    /path/to/src

            Save CMake Fragment File to Use with CMake::

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

        parser.add_argument("build_name", nargs="?", default="", help="The "
                            "keyword string for which you wish to generate the"
                            " configuration flags.")
        parser.add_argument("-l", "--list-config-flags", action="store_true",
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
        parser.add_argument("--save-load-env-args", action="store",
                            default=None, type=lambda p: Path(p).resolve(),
                            help="Based on the command line arguments passed to "
                            "GenConfig, write the corresponding command line "
                            "arguments for LoadEnv to a specified file.")

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

        return parser


def main(argv):
    """
    DOCSTRING
    """
    gc = GenConfig(argv)
    if gc.args.list_config_flags:
        gc.list_config_flags()
    elif gc.args.save_load_env_args is not None:
        with open(gc.args.save_load_env_args, "w") as F:
            F.write(" ".join(gc.load_env_args))
    elif gc.args.cmake_fragment is not None:
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

        unique_str = uuid.uuid4().hex[: 8]
        bash_cmake_args_file_loc = Path(
            f"/tmp/{user}/bash_cmake_args_from_gen_config_{unique_str}"
        ).resolve()
        with open(bash_cmake_args_file_loc, "w") as F:
            F.write(gc.generated_config_flags_str)

        # Location to the unique file ^^. Used in gen-config.sh.
        with open(f"/tmp/{user}/.bash_cmake_args_loc", "w") as F:
            F.write(str(bash_cmake_args_file_loc))


if __name__ == "__main__":
    main(sys.argv[1:])
