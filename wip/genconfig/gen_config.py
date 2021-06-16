#!/usr/bin/env python3

import argparse
from configparserenhanced import ConfigParserEnhanced
from contextlib import redirect_stdout
import io
from loadenv import LoadEnv
import os
from pathlib import Path
import re
from setprogramoptions import SetProgramOptionsCMake
from src.config_keyword_parser import ConfigKeywordParser
import sys
import textwrap
from typing import List
# TODO: Probably will need to import LoadEnv from somewhere here


class GenConfig:
    """
    Insert description here.

    Attributes:
        argv:  The command line arguments passed to ``gen_config.py``.
    """

    def parse_top_level_config_file(self):
        """
        Parse the ``gen-config.ini`` file and store the corresponding
        ``configparserenhanceddata`` object as :attr:`gen_config_config_data`.
        """
        if self.gen_config_config_data is None:
            self.gen_config_config_data = ConfigParserEnhanced(
                self.gen_config_ini_file
            ).configparserenhanceddata

            for section in ["gen-config", "load-env"]:
                if not self.gen_config_config_data.has_section(section):
                    raise ValueError(self.get_formatted_msg(
                        f"'{self.gen_config_ini_file}' must contain a "
                        f"'{section}' section."
                    ))

            section_keys = [
                ("gen-config", "supported-config-flags"),
                ("gen-config", "config-specs"),
                ("load-env", "supported-systems"),
                ("load-env", "supported-envs"),
                ("load-env", "environment-specs"),
            ]
            for section, key in section_keys:
                if not self.gen_config_config_data.has_option(section, key):
                    raise ValueError(self.get_formatted_msg(
                        f"'{self.gen_config_ini_file}' must contain the "
                        f"following in the '{section}' section:",
                        extras=f"  {key} : /path/to/{key}.ini"
                    ))
                value = self.gen_config_config_data[section][key]
                if value == "" or value is None:
                    raise ValueError(self.get_formatted_msg(
                        f"The path specified for '{key}' in "
                        f"'{self.gen_config_ini_file}' must be non-empty, e.g.:",
                        extras=f"  {key} : /path/to/{key}.ini"
                    ))
                else:
                    if not Path(value).is_absolute():
                        self.gen_config_config_data[section][key] = str(
                            self.gen_config_ini_file.parent / value
                        )

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
        self.gen_config_ini_file = Path(gen_config_ini_file)
        self.gen_config_config_data = None
        self.parse_top_level_config_file()
        self.config_keyword_parser = None
        self.set_program_options = None
        self.load_env = None
        self.has_been_validated = False

    def validate_config_specs_ini(self):
        if self.config_keyword_parser is None:
            self.load_config_keyword_parser()
        if self.load_env is None:
            self.load_load_env()

        ckp = self.config_keyword_parser
        le = self.load_env
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
            argv = [
                "--supported-systems", str(self.args.supported_systems_file),
                "--supported-envs", str(self.args.supported_envs_file),
                "--environment-specs", str(self.args.environment_specs_file),
            ]
            argv += ["--force"] if self.args.force else []
            argv += [self.args.build_name]
            self.load_env = LoadEnv(argv=argv)

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
        # TODO: Update this docstring.
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
                file.unlink()
            file.parent.mkdir(parents=True, exist_ok=True)

            with open(file, "w") as F:
                F.write("\n".join(cmake_options_list))

            self._cmake_fragment_file = file

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

    def get_formatted_msg(self, msg:str, kind:str="ERROR",
                          extras:str="") -> str:
        """
        This helper method handles multiline messages, rendering them like::

            +=================================================================+
            |   {kind}:  Unable to find alias or environment name for system
            |            'machine-type-5' in keyword string 'bad_kw_str'.
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
            else:
                msg += f"|           {line}\n"
        for extra in extras.splitlines():
            msg += f"|   {extra}\n"
        msg = "\n+" + "="*78 + "+\n" + msg + "+" + "="*78 + "+\n"
        msg = re.sub(r"\s+\n", "\n", msg)  # Remove trailing machine-name-4space

        return msg

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
            Basic Usage::

                python3 gen_config.py <build-name>
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
                            "(see LoadEnv).")  # NOTE: Should this be changed?

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
    if gc.args.cmake_fragment is not None:
        gc.write_cmake_fragment()
    else:
        print(gc.generated_config_flags_str, file=sys.stderr, end="")


if __name__ == "__main__":
    main(sys.argv[1:])
