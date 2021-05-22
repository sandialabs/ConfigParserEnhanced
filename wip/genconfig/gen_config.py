#!/usr/bin/env python3

"""
TODO:

    * Increase test coverage.

"""

import argparse
from configparserenhanced import ConfigParserEnhanced
import os
from pathlib import Path
from setprogramoptions import SetProgramOptions
from src.config_keyword_parser import ConfigKeywordParser
import sys
import textwrap
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
            if not self.gen_config_config_data.has_section("gen-config"):
                raise ValueError(self.get_formatted_msg(
                    f"'{self.gen_config_ini_file}' must contain a 'gen-config'"
                    " section."
                ))
            # for key in ["supported-systems", "supported-envs",
            #             "environment-specs"]:
            for key in ["supported-config-flags", "config-specs"]:
                if not self.gen_config_config_data.has_option("gen-config", key):
                    raise ValueError(self.get_formatted_msg(
                        f"'{self.gen_config_ini_file}' must contain the "
                        "following in the 'gen-config' section:",
                        extras=f"  {key} : /path/to/{key}.ini"
                    ))
                value = self.gen_config_config_data["gen-config"][key]
                if value == "" or value is None:
                    raise ValueError(self.get_formatted_msg(
                        f"The path specified for '{key}' in "
                        f"'{self.gen_config_ini_file}' must be non-empty, e.g.:",
                        extras=f"  {key} : /path/to/{key}.ini"
                    ))
                else:
                    if not Path(value).is_absolute():
                        self.gen_config_config_data["gen-config"][key] = str(
                            self.gen_config_ini_file.parent / value
                        )

    def __init__(self, argv):
        if not isinstance(argv, list):
            raise TypeError("GenConfig must be instantiated with a list of "
                            "command line arguments.")
        self.argv = argv
        self.gen_config_ini_file = (Path(os.path.realpath(__file__)).parent /
                                    "src/gen-config.ini")
        self.gen_config_config_data = None
        self.parse_top_level_config_file()
        self.config_keyword_parser = None
        self.set_program_options = None

    def gen_config_keyword_parser(self):
        """
        Instantiate an :class:`ConfigKeywordParser` object with this object's
        :attr:`build_name` and ``supported-config-flags.ini``.
        Save the resulting object as :attr:`config_keyword_parser`.
        """
        if self.config_keyword_parser is None:
            self.config_keyword_parser = ConfigKeywordParser(
                self.args.build_name,
                self.args.supported_config_flags_file
            )

    def list_config_flags(self):
        """
        List the available config flags form ``supported-config-flags.ini``.

        Raises:
            SystemExit:  With the message displaying the available config flags
            from which to choose.
        """
        if self.config_keyword_parser is None:
            self.gen_config_keyword_parser()
        sys.exit(
            self.config_keyword_parser.get_msg_showing_supported_flags(
                "Please select one of the following.",
                kind="INFO"
            )
        )

    @property
    def parsed_options(self):
        """
        The selected config flag options name parsed from the
        :attr:`build_name` via the :class:`ConfigKeywordParser`.
        """
        if not hasattr(self, "_parsed_options"):
            if self.config_keyword_parser is None:
                self.gen_config_keyword_parser()
            self._parsed_options = self.config_keyword_parser.selected_options
        return self._parsed_options

    def load_set_program_options(self):
        """
        Instantiate a :class:`SetProgramOptions` object with this object's
        ``config-specs.ini``.  Save the resulting object as
        :attr:`set_program_options`.
        """
        if self.set_program_options is None:
            self.set_program_options = SetProgramOptions(
                filename=self.args.config_specs_file
            )

    @property
    def options_string(self):
        if not hasattr(self, "_options_string"):
            if self.set_program_options is None:
                self.load_set_program_options()
            # TODO: Insert code here to work through :attr:`parsed_options`. Not
            # sure if this will be a dict of flags/options for key/value pairs or
            # one parsed string that's passed to SetProgramOptions. That will
            # depend on design decisions made in project-management#25.
            options_list = self.set_program_options.gen_option_list(
                self.parsed_options  # Placeholder
            )
            self._options_string = " \\\n    ".join(options_list)

        return self._options_string

    def write_cmake_fragment(self):
        # TODO: Update this docstring. And this method, haha.
        """
        Returns:
            Path:  The path to the cmake fragment that was written, either the
            default or whatever the user requested with ``--output``.
        """
        if self.set_program_options is None:
            self.load_set_program_options()
        file = Path("cmake.fragment")  # I'm very unfamiliar with how these
        #                                things are named.
        if self.args.output:
            file = self.args.output

        if file.exists():
            file.unlink()
        file.parent.mkdir(parents=True, exist_ok=True)
        # self.set_program_options.write_actions_to_file(
        #     file,
        #     self.parsed_env_name,
        #     include_header=True,
        #     interpreter="bash"
        # )
        return files

    def get_formatted_msg(self, msg, kind="ERROR", extras=""):
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
        parser.add_argument("-o", "--output", action="store", default=None,
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
        # NOTE: Not sure if we need this here in GenConfig since this is
        # already in LoadEnv.
        # config_files.add_argument("--supported-systems",
        #                           dest="supported_systems_file",
        #                           action="store", default=None,
        #                           type=lambda p: Path(p).resolve(),
        #                           help="Path to ``supported-systems.ini``.  "
        #                           "Overmachine-name-1s loading the file specified in "
        #                           "``gen-config.ini``.")
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

        return parser


def main(argv):
    """
    DOCSTRING
    """
    gc = GenConfig(argv)
    if gc.args.list_config_flags:
        gc.list_config_flags()
    print(gc.options_string)


if __name__ == "__main__":
    main(sys.argv[1:])
