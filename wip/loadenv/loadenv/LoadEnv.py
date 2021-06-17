#!/usr/bin/env python3

import argparse
from configparserenhanced import ConfigParserEnhanced
from determinesystem import DetermineSystem
import getpass
import os
from pathlib import Path
from setenvironment import SetEnvironment
import socket
import sys
import textwrap
import uuid

try:
    from .EnvKeywordParser import EnvKeywordParser
except ImportError:
    from EnvKeywordParser import EnvKeywordParser



class LoadEnv:
    """
    TODO: Insert description here.

    Attributes:
        argv:  The command line arguments passed to ``load_env.sh``.
    """

    def parse_top_level_config_file(self):
        """
        Parse the ``load-env.ini`` file and store the corresponding
        ``configparserenhanceddata`` object as :attr:`load_env_config_data`.

        Raises:
            ValueError: (TODO - FILL THIS IN)
        """
        if self.load_env_config_data is None:
            self.load_env_config_data = ConfigParserEnhanced(
                self.load_env_ini_file
            ).configparserenhanceddata
            if not self.load_env_config_data.has_section("load-env"):
                msg = f"'{self.load_env_ini_file}' must contain a 'load-env' section."
                raise ValueError(self.get_formatted_msg(msg))
            for key in ["supported-systems", "supported-envs", "environment-specs"]:
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
        return


    def parse_supported_systems_file(self):
        """
        Parse the ``supported-systems.ini`` file and store the corresponding
        ``configparserenhanceddata`` object as :attr:`supported_systems_data`.
        """
        if self.supported_systems_data is None:
            self.supported_systems_data = ConfigParserEnhanced(
                self.args.supported_systems_file
                ).configparserenhanceddata
        return


    def __init__(self,
                 argv,
                load_env_ini_file=(Path(os.path.realpath(__file__)).parent / "load-env.ini")
                # load_env_ini_file set here for testing purposes. It is not meant to
                # be changed by the user.
                ):
        if not isinstance(argv, list):
            raise TypeError("LoadEnv must be instantiated with a list of command line arguments.")
        self.argv = argv
        self.load_env_ini_file = load_env_ini_file
        self.load_env_config_data = None
        self.parse_top_level_config_file()
        self.supported_systems_data = None
        self.parse_supported_systems_file()
        self.env_keyword_parser = None
        self.set_environment = None


    @property
    def build_name(self):
        return self.args.build_name


    @build_name.setter
    def build_name(self, new_build_name):
        # Clear any data generated from the old build_name
        if hasattr(self, "_system_name"):
            delattr(self, "_system_name")
        if hasattr(self, "_parsed_env_name"):
            delattr(self, "_parsed_env_name")
        self.env_keyword_parser = None

        self.args.build_name = new_build_name
        return self.args.build_name


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
        return


    def list_envs(self):
        """
        List the environments available on the current machine.

        Raises:
            SystemExit:  With the message displaying the available environments
            from which to choose.
        """
        if self.env_keyword_parser is None:
            self.load_env_keyword_parser()

        sys.exit(self.env_keyword_parser.get_msg_showing_supported_environments(
                    "Please select one of the following.",
                    kind="INFO"
                    )
                )
        return


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
            self.set_environment = SetEnvironment(filename=self.args.environment_specs_file)
        return


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
        return


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

        files = [self.tmp_load_matching_env_file]
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
            with open(f, "a") as F:
                F.write(f"export LOADED_ENV_NAME={self.parsed_env_name}")

        return files[-1]


    @property
    def tmp_load_matching_env_file(self):
        """
        Returns:
            Path:  The path to the temporary `load_matching_env.sh` file that
            gets written in the `/tmp` directory.
        """
        if not hasattr(self, "_tmp_load_matching_env_file"):
            unique_str = uuid.uuid4().hex[:8]
            user = getpass.getuser()
            self._tmp_load_matching_env_file = Path(
                f"/tmp/{user}/load_matching_env_{unique_str}.sh"
                ).resolve()

        return self._tmp_load_matching_env_file


    def get_formatted_msg(self, msg, kind="ERROR", extras=""):
        """
        This helper method handles multiline messages, rendering them like::

            +=================================================================+
            |   {kind}:  Unable to find alias or environment name for system
            |            'machine-type-1' in keyword string 'bad_kw_str'.
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

        examples = textwrap.dedent("""\
            Basic Usage:

                $ source load-env.sh [options] [build_name]

                This will place you in a sub-shell with the desired environment loaded.

            Force Load an Environment:

                If you find that you are on a platform that is unknown to LoadEnv
                but you know that it has all the proper modules and packages installed
                that match an existing environment you can force-load a configuration
                with the `--force` option. For example, to force-load the clang-10
                environment for a RHEL7 system that has the SEMS environment modules
                installed, you would enter:

                $ source load-env.sh --force rhel7_sems-clang-10.0.0-openmpi-1.10.1-openmp

                In this case the fully-qualified environment name is formatted as:
                <system_type>_<full_environment_name>

            Identify available environments for a given platform:

                If you are on a system that matches one of the known system types
                but its hostname is not identified in the `supported-envs.ini` file,
                you can find out what environments are supported through the `--force`
                option:

                $ source load-env.sh --force <system_type>

                where <system_type> is one of the section headers in `supported-envs.ini`,
                such as "rhel7".
        """)
        examples = "[ Examples ]".center(79, "-") + "\n\n" + examples

        parser = argparse.ArgumentParser(
            description=description,
            epilog=examples,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            usage="LoadEnv.py [options] [build_name]"
        )

        parser.add_argument("build_name",
                            nargs="?",
                            default="",
                            help="The "
                            "keyword string for which you wish to load the environment.")

        parser.add_argument("--ci-mode",
                            action="store_true",
                            default=False,
                            help="Causes load-env.sh to source the environment to "
                            "your current shell rather than putting you in an "
                            "interactive subshell with the loaded environment.")

        parser.add_argument("-l", "--list-envs",
                            action="store_true",
                            default=False,
                            help="List the environments "
                            "available on your current machine.")

        parser.add_argument("-o", "--output",
                            action="store",
                            default=None,
                            type=lambda p: Path(p).resolve(),
                            help="Output a "
                            "bash script that when sourced will give you an "
                            "environment identical to the one loaded when "
                            "using this tool.")

        parser.add_argument("-f", "--force",
                            action="store_true",
                            default=False,
                            help="Forces load_env to use the "
                            "system name specified in the build_name rather "
                            "than the system name matched via the hostname "
                            "and the supported-systems.ini file.")

        config_files = parser.add_argument_group("configuration file overrides")

        config_files.add_argument("--supported-systems",
                                  dest="supported_systems_file",
                                  action="store",
                                  default=None,
                                  type=lambda p: Path(p).resolve(),
                                  help="Path to ``supported-systems.ini``.  "
                                  "Overrides loading the file specified in "
                                  "``load-env.ini``.")

        config_files.add_argument("--supported-envs",
                                  default=None,
                                  dest="supported_envs_file",
                                  action="store",
                                  type=lambda p: Path(p).resolve(),
                                  help="Path to ``supported-envs.ini``.  "
                                  "Overrides loading the file specified in "
                                  "``load-env.ini``.")

        config_files.add_argument("--environment-specs",
                                  dest="environment_specs_file",
                                  action="store",
                                  default=None,
                                  type=lambda p: Path(p).resolve(),
                                  help="Path to ``environment-specs.ini``.  "
                                  "Overrides loading the file specified in "
                                  "``load-env.ini``.")

        return parser



# ============================
#   M A I N
# ============================


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

    cwd = Path.cwd().resolve()
    with open(cwd/".load_matching_env_loc", "w") as F:
        F.write(str(le.tmp_load_matching_env_file))
    if le.args.ci_mode:
        (cwd/".ci_mode").touch()



if __name__ == "__main__":
    main(sys.argv[1:])
