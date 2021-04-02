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
        self, argv, build_name="", load_env_ini="load_env.ini",
        supported_systems_file=None, supported_envs_file=None,
        environment_specs_file=None, output=None,
        force_build_name_sys_name=False
    ):
        if not isinstance(argv, list):
            raise TypeError("LoadEnv must be instantiated with a list of "
                            "command line arguments.")
        self.argv = argv
        self._build_name = build_name
        self._load_env_ini_file = load_env_ini
        self._supported_systems_file = supported_systems_file
        self._supported_envs_file = supported_envs_file
        self._environment_specs_file = environment_specs_file
        self._output = output
        self._force_build_name_sys_name = force_build_name_sys_name

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
                f"'{self.supported_systems_file}'."
            )
            sys.exit(msg)

        # Use system name in build_name if hostname_sys_name is None
        if build_name_sys_name is not None:
            self._system_name = build_name_sys_name
            if (hostname_sys_name is not None
                    and hostname_sys_name != self._system_name
                    and self.force_build_name_sys_name is False):
                msg = self.get_formatted_msg(
                    f"Hostname '{hostname}' matched to system "
                    f"'{hostname_sys_name}'\n in "
                    f"'{self.supported_systems_file}', but you specified "
                    f"'{self._system_name}' in the build name.\nIf you want "
                    f"to force the use of '{self._system_name}', add "
                    "the --force flag."
                )
                sys.exit(msg)

        return self._system_name

    def get_sys_name_from_hostname(self, hostname):
        """
        Helper function to match the given hostname to a system name, as
        defined by the :attr:`supported_systems_file`. If nothing is matched,
        ``None`` is returned.

        Parameters:
            hostname:  The hostname to match a system name to.

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
        Helper function that finds any system name in
        :attr:`supported_systems_file` that exists in the :attr:`build_name`.
        If more than 1 system name is matched, an exception is raised, and if
        no system names are matched, then ``None`` is returned.

        Returns:
            str:  The matched system name in the build name, if it exists. If
            not, return ``None``.
        """
        sys_names = [s for s in self.supported_systems_ini.sections()
                     if s != "DEFAULT"]
        build_name_sys_names = [_ for _ in sys_names if _ in self.build_name]
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
    def force_build_name_sys_name(self):
        """
        If ``True``, load_env is forced to use the configurations
        for the system name specified in the build_name rather than the system
        name matched via the hostname and the supported-systems.ini file. The
        value that exists for this in :attr:`parsed_args` overrides the value
        that is passed through the class initializer.

        Returns:
            bool:  The ``force_build_name_sys_name`` flag.
        """
        if self.parsed_args is not None:
            self._force_build_name_sys_name = (
                self.parsed_args.force_build_name_sys_name
            )

        return self._force_build_name_sys_name

    @property
    def parsed_env_name(self):
        """
        This property instantiates an :class:`EnvKeywordParser` object with
        this object's :attr:`build_name`, :attr:`system_name`, and
        :attr:`supported_envs_file`. From this object, the qualified
        environment name is retrieved and returned.

        Returns:
            str:  The qualified environment name from parsing the
            :attr:`build_name`.
        """
        ekp = EnvKeywordParser(self.build_name, self.system_name,
                               self.supported_envs_file)
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
        se = SetEnvironment(filename=self.environment_specs_file)
        files = [Path("/tmp/load_matching_env.sh").resolve()]
        if self.output:
            files += [self.output]
        for f in files:
            if f.exists():
                f.unlink()
            f.parent.mkdir(parents=True, exist_ok=True)
            se.write_actions_to_file(f, self.parsed_env_name,
                                     include_header=True, interpreter="bash")
        return files[-1]

    @property
    def build_name(self):
        """
        Returns the :attr:`build_name` value passed by the user. Any value
        that exists for this in :attr:`parsed_args` overrides the value that is
        passed through the class initializer.

        Returns:
            str:  The keyword string given by the user.
        """
        if (self.parsed_args is not None and
                self.parsed_args.build_name is not None):
            self._build_name = self.parsed_args.build_name

        if self._build_name == "":
            raise ValueError('Keyword string cannot be "".')

        return self._build_name

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
    def supported_systems_file(self):
        """
        Gives the path to ``supported-systems.ini``. Any value that exists for
        this in :attr:`parsed_args` or that was explicitly passed
        in the class initializer overrides the value that is in
        ``load_env.ini``.

        Returns:
            pathlib.Path:  The path to ``supported-systems.ini``.
        """
        if (self.parsed_args is not None and
                self.parsed_args.supported_systems_file is not None):
            self._supported_systems_file = (
                self.parsed_args.supported_systems_file
            )

        if self._supported_systems_file is None:
            self._supported_systems_file = (
                self.load_env_ini["load-env"]["supported-systems"]
            )

        if self._supported_systems_file == "":
            raise ValueError('Path for supported-systems.ini cannot be "".')

        self._supported_systems_file = Path(self._supported_systems_file)

        return self._supported_systems_file

    @property
    def supported_systems_ini(self):
        """
        Returns:
            configparserenhanced.ConfigParserEnhancedData:  The data from
            ``supported-systems.ini``.
        """
        self._supported_systems = ConfigParserEnhanced(
            self.supported_systems_file
        ).configparserenhanceddata

        return self._supported_systems

    @property
    def supported_envs_file(self):
        """
        Gives the path to ``supported-envs.ini``. Any value that exists for
        this in :attr:`parsed_args` or that was explicitly passed
        in the class initializer overrides the value that is in
        ``load_env.ini``.

        Returns:
            pathlib.Path:  The path to ``supported-envs.ini``.
        """
        if (self.parsed_args is not None and
                self.parsed_args.supported_envs_file is not None):
            self._supported_envs_file = self.parsed_args.supported_envs_file

        if self._supported_envs_file is None:
            self._supported_envs_file = (
                self.load_env_ini["load-env"]["supported-envs"]
            )

        if self._supported_envs_file == "":
            raise ValueError('Path for supported-envs.ini cannot be "".')

        self._supported_envs_file = Path(self._supported_envs_file)

        return self._supported_envs_file

    @property
    def environment_specs_file(self):
        """
        Gives the path to ``environment-specs.ini``. Any value that exists for
        this in :attr:`parsed_args` or that was explicitly passed
        in the class initializer overrides the value that is in
        ``load_env.ini``.

        Returns:
            pathlib.Path:  The path to ``environment-specs.ini``.
        """
        if (self.parsed_args is not None and
                self.parsed_args.environment_specs_file is not None):
            self._environment_specs_file = (
                self.parsed_args.environment_specs_file
            )

        if self._environment_specs_file is None:
            self._environment_specs_file = (
                self.load_env_ini["load-env"]["environment-specs"]
            )

        if self._environment_specs_file == "":
            raise ValueError('Path for environment-specs.ini cannot be "".')

        self._environment_specs_file = Path(self._environment_specs_file)

        return self._environment_specs_file

    @property
    def output(self):
        """
        Gives the path to a file to output a bash script that when sourced will
        give the user the same environment that was loaded by this tool. Any
        value that exists for this in :attr:`parsed_args` overrides the value
        that is passed through the class initializer.

        Returns:
            pathlib.Path, None:  The path to the script, if the user has
            specified it.
        """
        if (self.parsed_args is not None and
                self.parsed_args.output is not None):
            self._output = Path(
                self.parsed_args.output
            ).resolve()
        return self._output

    @property
    def parsed_args(self):
        """
        The result of calling ``parsed_args(self.argv)`` on :func:`__parser`.

        Returns:
            argparse.Namespace:  The parsed arguments.
        """
        return self.__parser().parse_args(self.argv)

    def __parser(self):
        """
        Returns:
            argparse.ArgumentParser:  The parser bject with properly configured
            argument options.  This is to be used in conjunction with
            :attr:`parsed_args`.
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

        parser.add_argument("build_name", help=(
            "The keyword string for which you wish to load the environment."
        ))

        parser.add_argument("-o", "--output",
                            dest="output", action="store",
                            default=None,
                            help="Output a bash script that when sourced will "
                            "give you an environment identical to the one "
                            "loaded when using this tool.")

        parser.add_argument("-f", "--force", dest="force_build_name_sys_name",
                            action="store_true", default=False,
                            help="Forces load_env to use the system name "
                            "specified in the build_name rather than the "
                            "system name matched via the hostname and the "
                            "supported-systems.ini file.")

        config_files = parser.add_argument_group(
            "configuration file overrides"
        )
        config_files.add_argument("--supported-systems",
                                  dest="supported_systems_file",
                                  action="store", default=None,
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
