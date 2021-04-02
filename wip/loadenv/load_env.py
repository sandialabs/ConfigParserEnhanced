#!/usr/bin/env python3

import argparse
from configparserenhanced import ConfigParserEnhanced
from pathlib import Path
import re
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

    def __init__(
        self, argv, load_env_ini="load_env.ini"
    ):
        if not isinstance(argv, list):
            raise TypeError("LoadEnv must be instantiated with a list of "
                            "command line arguments.")
        self.argv = argv
        self._load_env_ini_file = load_env_ini

    @property
    def system_name(self):
        if hasattr("self", "_system_name"):
            return self._system_name

        hostname = socket.gethostname()
        hostname_sys_name = self.get_sys_name_from_hostname(hostname)
        self._system_name = hostname_sys_name

        build_name_sys_name = self.get_sys_name_from_build_name()

        if hostname_sys_name is None and build_name_sys_name is None:
            msg = self.get_formatted_msg(
                f"Unable to find valid system name in the build name or "
                f"for the hostname '{hostname}'\n in "
                f"'{self.args.supported_systems_file}'."
            )
            sys.exit(msg)

        # Use system name in build_name if hostname_sys_name is None
        if build_name_sys_name is not None:
            self._system_name = build_name_sys_name
            if (hostname_sys_name is not None
                    and hostname_sys_name != self._system_name
                    and self.args.force is False):
                msg = self.get_formatted_msg(
                    f"Hostname '{hostname}' matched to system "
                    f"'{hostname_sys_name}'\n in "
                    f"'{self.args.supported_systems_file}', but you specified "
                    f"'{self._system_name}' in the build name.\nIf you want "
                    f"to force the use of '{self._system_name}', add "
                    "the --force flag."
                )
                sys.exit(msg)

        return self._system_name

    def get_sys_name_from_hostname(self, hostname):
        """
        Helper function to match the given hostname to a system name, as
        defined by the ``supported-systems.ini``.  If nothing is matched,
        ``None`` is returned.

        Parameters:
            hostname (str):  The hostname to match a system name to.

        Returns:
            str:  The matched system name, or ``None`` if nothing is matched.
        """
        sys_names = [s for s in self.supported_systems_ini.sections()
                     if s != "DEFAULT"]
        hostname_sys_name = None
        for sys_name in sys_names:
            # Strip the keys of comments:
            #
            #   Don't match anything following whitespace and a '#'.
            #                                  |
            #   Match anything that's not      |
            #        a '#' or whitespace.      |
            #                      vvvvv    vvvvvvvv
            keys = [re.findall(r"([^#^\s]*)(?:\s*#.*)?", key)[0]
                    for key in self.supported_systems_ini[sys_name].keys()]

            # Keys are treated as REGEXes
            matches = []
            for key in keys:
                matches += re.findall(key, hostname)

            if len(matches) > 0:
                hostname_sys_name = sys_name
                break

        return hostname_sys_name

    def get_sys_name_from_build_name(self):
        """
        Helper function that finds any system name in ``supported-systems.ini``
        that exists in the ``build_name``.  If more than one system name is
        matched, an exception is raised, and if no system names are matched,
        then ``None`` is returned.

        Returns:
            str:  The matched system name in the build name, if it exists. If
            not, return ``None``.
        """
        sys_names = [s for s in self.supported_systems_ini.sections()
                     if s != "DEFAULT"]
        build_name_sys_names = [_ for _ in sys_names if _ in
                                self.args.build_name]
        if len(build_name_sys_names) > 1:
            msg = self.get_msg_for_list(
                "Cannot specify more than one system name in the build name\n"
                "You specified", build_name_sys_names
            )
            sys.exit(msg)
        elif len(build_name_sys_names) == 0:
            build_name_sys_name = None
        else:
            build_name_sys_name = build_name_sys_names[0]

        return build_name_sys_name

    @property
    def parsed_env_name(self):
        """
        This property instantiates an :class:`EnvKeywordParser` object with
        this object's :attr:`build_name`, :attr:`system_name`, and
        ``supported-envs.ini``. From this object, the qualified environment
        name is retrieved and returned.

        Returns:
            str:  The qualified environment name from parsing the
            :attr:`build_name`.
        """
        ekp = EnvKeywordParser(self.args.build_name, self.system_name,
                               self.args.supported_envs_file)
        self._parsed_env_name = ekp.qualified_env_name

        return self._parsed_env_name

    def write_load_matching_env(self):
        """
        Write a bash script that when sourced will give you the same
        environment loaded by this tool.

        Returns:
            Path:  The path to the script that was written, either the default,
            or whatever the user requested with ``--output``.
        """
        se = SetEnvironment(filename=self.args.environment_specs_file)
        files = [Path("/tmp/load_matching_env.sh").resolve()]
        if self.args.output:
            files += [self.args.output]
        for f in files:
            if f.exists():
                f.unlink()
            f.parent.mkdir(parents=True, exist_ok=True)
            se.write_actions_to_file(f, self.parsed_env_name,
                                     include_header=True, interpreter="bash")
        return files[-1]

    @property
    def load_env_ini(self):
        """
        Returns:
            configparserenhanced.ConfigParserEnhancedData:  The data from
            ``load_env.ini``.
        """
        if not hasattr(self, "_load_env_ini"):
            self._load_env_ini = ConfigParserEnhanced(
                self._load_env_ini_file
            ).configparserenhanceddata
        return self._load_env_ini

    @property
    def supported_systems_ini(self):
        """
        Returns:
            configparserenhanced.ConfigParserEnhancedData:  The data from
            ``supported-systems.ini``.
        """
        self._supported_systems = ConfigParserEnhanced(
            self.args.supported_systems_file
        ).configparserenhanceddata
        return self._supported_systems

    @property
    def args(self):
        """
        The parsed command line arguments to the script.

        Returns:
            argparse.Namespace:  The parsed arguments.
        """
        args = self.__parser().parse_args(self.argv)

        if args.supported_systems_file is None:
            args.supported_systems_file = (
                self.load_env_ini["load-env"]["supported-systems"]
            )
        if args.supported_systems_file == "":
            raise ValueError('Path for supported-systems.ini cannot be "".')
        args.supported_systems_file = Path(args.supported_systems_file)

        if args.supported_envs_file is None:
            args.supported_envs_file = (
                self.load_env_ini["load-env"]["supported-envs"]
            )
        if args.supported_envs_file == "":
            raise ValueError('Path for supported-envs.ini cannot be "".')
        args.supported_envs_file = Path(args.supported_envs_file)

        if args.environment_specs_file is None:
            args.environment_specs_file = (
                self.load_env_ini["load-env"]["environment-specs"]
            )
        if args.environment_specs_file == "":
            raise ValueError('Path for environment-specs.ini cannot be "".')
        args.environment_specs_file = Path(args.environment_specs_file)

        return args

    def __parser(self):
        """
        Returns:
            argparse.ArgumentParser:  The parser bject with properly configured
            argument options.  This is to be used in conjunction with
            :attr:`args`.
        """
        if hasattr(self, "_parser"):
            return self._parser

        description = "[ Load Environment Utility ]".center(79, "-")

        examples = """
            Basic Usage::

                load_env.sh build_name-here
        """
        examples = textwrap.dedent(examples)
        examples = "[ Examples ]".center(79, "-") + "\n\n" + examples

        parser = argparse.ArgumentParser(
            description=description,
            epilog=examples,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        parser.add_argument("build_name", help="The keyword string for which "
                            "you wish to load the environment.")

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
                                  help="Path to ``supported-envs.ini``.  "
                                  "Overrides loading the file specified in "
                                  "``load_env.ini``.")
        config_files.add_argument("--environment-specs",
                                  dest="environment_specs_file",
                                  action="store", default=None,
                                  help="Path to ``environment-specs.ini``.  "
                                  "Overrides loading the file specified in "
                                  "``load_env.ini``.")

        return parser


if __name__ == "__main__":
    le = LoadEnv(sys.argv[1:])
    le.write_load_matching_env()
