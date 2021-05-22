#!/usr/bin/env python3

"""
TODO:

    * Increase test coverage.

"""

import argparse
from configparserenhanced import ConfigParserEnhanced
from determinesystem import DetermineSystem
import os
from pathlib import Path
from setenvironment import SetEnvironment
from src.env_keyword_parser import EnvKeywordParser
from src.load_env_common import LoadEnvCommon
import socket
import sys
import textwrap


class LoadEnv(LoadEnvCommon):
    """
    Insert description here.

    Attributes:
        argv:  The command line arguments passed to ``load_env.sh``.
    """

    def parse_top_level_config_file(self):
        """
        Parse the ``load-env.ini`` file and store the corresponding
        ``configparserenhanceddata`` object as :attr:`load_env_config_data`.
        """
        if self.load_env_config_data is None:
            self.load_env_config_data = ConfigParserEnhanced(
                self.load_env_ini_file
            ).configparserenhanceddata
            if not self.load_env_config_data.has_section("load-env"):
                raise ValueError(self.get_formatted_msg(
                    f"'{self.load_env_ini_file}' must contain a 'load-env' "
                    "section."
                ))
            for key in ["supported-systems", "supported-envs",
                        "environment-specs"]:
                if not self.load_env_config_data.has_option("load-env", key):
                    raise ValueError(self.get_formatted_msg(
                        f"'{self.load_env_ini_file}' must contain the "
                        "following in the 'load-env' section:",
                        extras=f"  {key} : /path/to/{key}.ini"
                    ))
                value = self.load_env_config_data["load-env"][key]
                if value == "" or value is None:
                    raise ValueError(self.get_formatted_msg(
                        f"The path specified for '{key}' in "
                        f"'{self.load_env_ini_file}' must be non-empty, e.g.:",
                        extras=f"  {key} : /path/to/{key}.ini"
                    ))
                else:
                    if not Path(value).is_absolute():
                        self.load_env_config_data["load-env"][key] = str(
                            self.load_env_ini_file.parent / value
                        )

    def parse_supported_systems_file(self):
        """
        Parse the ``supported-systems.ini`` file and store the corresponding
        ``configparserenhanceddata`` object as :attr:`supported_systems_data`.
        """
        if self.supported_systems_data is None:
            self.supported_systems_data = ConfigParserEnhanced(
                self.args.supported_systems_file
            ).configparserenhanceddata

    def __init__(self, argv):
        if not isinstance(argv, list):
            raise TypeError("LoadEnv must be instantiated with a list of "
                            "command line arguments.")
        self.argv = argv
        self.load_env_ini_file = (Path(os.path.realpath(__file__)).parent /
                                  "src/load-env.ini")
        self.load_env_config_data = None
        self.parse_top_level_config_file()
        self.supported_systems_data = None
        self.parse_supported_systems_file()
        self.env_keyword_parser = None
        self.set_environment = None

    @property
    def system_name(self):
        """
        The name of the system from which the tool will select an environment.
        """
        if not hasattr(self, "_system_name"):
            ds = DetermineSystem(self.args.build_name,
                                 self.args.supported_systems_file,
                                 force_build_name=self.args.force)
            self._system_name = ds.system_name

        return self._system_name

    def load_env_keyword_parser(self):
        """
        Instantiate an :class:`EnvKeywordParser` object with this object's
        :attr:`build_name`, :attr:`system_name`, and ``supported-envs.ini``.
        Save the resulting object as :attr:`env_keyword_parser`.
        """
        if self.env_keyword_parser is None:
            self.env_keyword_parser = EnvKeywordParser(
                self.args.build_name,
                self.system_name,
                self.args.supported_envs_file
            )

    def list_envs(self):
        """
        List the environments available on the current machine.

        Raises:
            SystemExit:  With the message displaying the available environments
            from which to choose.
        """
        if self.env_keyword_parser is None:
            self.load_env_keyword_parser()
        sys.exit(
            self.env_keyword_parser.get_msg_showing_supported_environments(
                "Please select one of the following.",
                kind="INFO"
            )
        )

    @property
    def parsed_env_name(self):
        """
        The environent name parsed from the :attr:`build_name` via the
        :class:`EnvKeywordParser`.
        """
        if not hasattr(self, "_parsed_env_name"):
            if self.env_keyword_parser is None:
                self.load_env_keyword_parser()
            self._parsed_env_name = self.env_keyword_parser.qualified_env_name
        return self._parsed_env_name

    def load_set_environment(self):
        """
        Instantiate a :class:`SetEnvironment` object with this object's
        ``environment-specs.ini``.  Save the resulting object as
        :attr:`set_environment`.
        """
        if self.set_environment is None:
            self.set_environment = SetEnvironment(
                filename=self.args.environment_specs_file
            )

    def apply_env(self):
        """
        Apply the selected environment to ensure it works on the given machine.
        """
        if self.set_environment is None:
            self.load_set_environment()
        rval = self.set_environment.apply(self.parsed_env_name)
        if rval != 0:
            raise RuntimeError(self.get_formatted_msg(
                "Something unexpected went wrong in applying the "
                f"environment.  Ensure that the '{self.parsed_env_name}' "
                "environment is fully supported on the "
                f"'{socket.gethostname()}' host."
            ))

    def write_load_matching_env(self):
        """
        Write a bash script that when sourced will give you the same
        environment loaded by this tool.

        Returns:
            Path:  The path to the script that was written, either the default
            (which always gets written to), or whatever the user requested with
            ``--output``.
        """
        if self.set_environment is None:
            self.load_set_environment()
        files = [Path("/tmp/load_matching_env.sh").resolve()]
        if self.args.output:
            files += [self.args.output]
        for f in files:
            if f.exists():
                f.unlink()
            f.parent.mkdir(parents=True, exist_ok=True)
            self.set_environment.write_actions_to_file(
                f,
                self.parsed_env_name,
                include_header=True,
                interpreter="bash"
            )
        return files[-1]

    @property
    def args(self):
        """
        The parsed command line arguments to the script.

        Returns:
            argparse.Namespace:  The parsed arguments.
        """
        if not hasattr(self, "_args"):
            args = self.__parser().parse_args(self.argv)
            if args.supported_systems_file is None:
                args.supported_systems_file = Path(
                    self.load_env_config_data["load-env"]["supported-systems"]
                ).resolve()
            if args.supported_envs_file is None:
                args.supported_envs_file = Path(
                    self.load_env_config_data["load-env"]["supported-envs"]
                ).resolve()
            if args.environment_specs_file is None:
                args.environment_specs_file = Path(
                    self.load_env_config_data["load-env"]["environment-specs"]
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
        description = "[ Load Environment Utility ]".center(79, "-")
        description += ("\n\nThis tool allows you to load environments "
                        "supported on your system by passing\nit a string "
                        "containing keywords to call out a particular "
                        "environment name or\nalias.")

        examples = """
            Basic Usage::

                source load-env.sh <build-name>
        """
        examples = textwrap.dedent(examples)
        examples = "[ Examples ]".center(79, "-") + "\n\n" + examples

        parser = argparse.ArgumentParser(
            description=description,
            epilog=examples,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        parser.add_argument("build_name", nargs="?", default="", help="The "
                            "keyword string for which you wish to load the "
                            "environment.")
        parser.add_argument("-l", "--list-envs", action="store_true",
                            default=False, help="List the environments "
                            "available on your current machine.")
        parser.add_argument("-o", "--output", action="store", default=None,
                            type=lambda p: Path(p).resolve(), help="Output a "
                            "bash script that when sourced will give you an "
                            "environment identical to the one loaded when "
                            "using this tool.")
        parser.add_argument("-f", "--force", action="store_true",
                            default=False, help="Forces load_env to use the "
                            "system name specified in the build_name rather "
                            "than the system name matched via the hostname "
                            "and the supported-systems.ini file.")
        
        config_files = parser.add_argument_group(
            "configuration file overrides"
        )
        config_files.add_argument("--supported-systems",
                                  dest="supported_systems_file",
                                  action="store", default=None,
                                  type=lambda p: Path(p).resolve(),
                                  help="Path to ``supported-systems.ini``.  "
                                  "Overrides loading the file specified in "
                                  "``load_env.ini``.")
        config_files.add_argument("--supported-envs", default=None,
                                  dest="supported_envs_file", action="store",
                                  type=lambda p: Path(p).resolve(),
                                  help="Path to ``supported-envs.ini``.  "
                                  "Overrides loading the file specified in "
                                  "``load_env.ini``.")
        config_files.add_argument("--environment-specs",
                                  dest="environment_specs_file",
                                  action="store", default=None,
                                  type=lambda p: Path(p).resolve(),
                                  help="Path to ``environment-specs.ini``.  "
                                  "Overrides loading the file specified in "
                                  "``load_env.ini``.")

        return parser


def main(argv):
    """
    DOCSTRING
    """
    le = LoadEnv(argv)
    if le.args.list_envs:
        le.list_envs()
    le.apply_env()
    print(f"Environment '{le.parsed_env_name}' validated.")
    le.write_load_matching_env()


if __name__ == "__main__":
    main(sys.argv[1:])
