#!/usr/bin/env python3

import argparse
from configparserenhanced import ConfigParserEnhanced
import os
from pathlib import Path
import textwrap
from setenvironment import SetEnvironment
from src.env_keyword_parser import EnvKeywordParser
import sys


class LoadEnv:
    """
    Insert description here.

    Attributes:
        argv:  The command line arguments passed to ``load_env.sh``.
    """

    def __init__(
        self, build_name="", load_env_ini="load_env.ini",
        supported_systems_file=None, supported_envs_file=None,
        environment_specs_file=None, output=None, argv=None
    ):
        self._build_name = build_name
        self._load_env_ini_file = load_env_ini
        self._supported_systems_file = supported_systems_file
        self._supported_envs_file = supported_envs_file
        self._environment_specs_file = environment_specs_file
        self._output = output
        self.argv = argv

    @property
    def system_name(self):
        # Very much a placeholder. Will update.
        self._system_name = os.environ.get("SNLSYSTEM", None)
        return self._system_name

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
        If ``self.argv is None``, then this property also returns ``None``.

        Returns:
            argparse.Namespace:  The parsed arguments, or ``None`` if
            ``self.argv is None``.
        """
        if self.argv is None:
            return None

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


def main(argv):
    le = LoadEnv(argv=argv)
    le.write_load_matching_env()


if __name__ == "__main__":
    main(sys.argv[1:])
