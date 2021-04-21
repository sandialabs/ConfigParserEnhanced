#!/usr/bin/env python3

from configparserenhanced import ConfigParserEnhanced
import re
import socket
import sys
import textwrap


class DetermineSystem:
    """
    This small utility determines the system name from a
    ``supported_systems.ini`` file, the ``hostname``, and potentially the
    ``build_name``.

    Parameters:
        build_name (str):  The build name for the environment or configuration.
        supported_systems_file (Path-like):  The path to
            ``supported_systems.ini``.
        force_build_name (bool):  If ``True``, use the system name determined
            by the ``build_name`` rather than that determined by the
            ``hostname``.
    """

    def __init__(self, build_name, supported_systems_file,
                 force_build_name=False):
        self.build_name = build_name
        self.supported_systems_file = supported_systems_file
        self.supported_systems_data = None
        self.parse_supported_systems_file()
        self.force_build_name = force_build_name

    @property
    def system_name(self):
        """
        The name of the system from which the tool will select an environment.
        """
        if not hasattr(self, "_system_name"):
            self.determine_system()
            """
            When pulling this system determination piece out into its own
            utility, here's what I'm guessing this'll look like after the fact:

            ds = DetermineSystem(self.args.supported_systems_file)
            self._system_name = ds.system_name

            We'll need to move determine_system() and
            parse_supported_systems_file() and any associated data over to
            DetermineSystem.
            """
        return self._system_name

    def determine_system(self):
        """
        Determine which system from ``supported-envs.ini`` to use, either by
        grabbing what's specified in the :attr:`build_name`, or by using the
        hostname and ``supported-systems.ini``.  Store the result as
        :attr:`system_name`.
        """
        if not hasattr(self, "_system_name"):
            hostname = socket.gethostname()
            sys_name_from_hostname = self.get_sys_name_from_hostname(hostname)
            self._system_name = sys_name_from_hostname
            if self._system_name is not None:
                print(f"Using system '{self._system_name}' based on matching "
                      f"hostname '{hostname}'.")
            sys_name_from_build_name = self.get_sys_name_from_build_name()
            if (sys_name_from_hostname is None and
                    sys_name_from_build_name is None):
                msg = self.get_formatted_msg(textwrap.fill(
                    f"Unable to find valid system name in the build name or "
                    f"for the hostname '{hostname}' in "
                    f"'{self.supported_systems_file}'.",
                    width=68,
                    break_on_hyphens=False,
                    break_long_words=False
                ))
                sys.exit(msg)

            # Use the system name in build_name if sys_name_from_hostname is
            # None.
            if sys_name_from_build_name is not None:
                self._system_name = sys_name_from_build_name
                print(("Setting" if sys_name_from_hostname is None else
                       "Overriding") +
                      f" system to '{self._system_name}' based on "
                      f"specification in build name '{self.build_name}'.")
                if (sys_name_from_hostname is not None
                        and sys_name_from_hostname != self._system_name
                        and self.force_build_name is False):
                    msg = self.get_formatted_msg(textwrap.fill(
                        f"Hostname '{hostname}' matched to system "
                        f"'{sys_name_from_hostname}' in "
                        f"'{self.supported_systems_file}', but you "
                        f"specified '{self._system_name}' in the build name.  "
                        "If you want to force the use of "
                        f"'{self._system_name}', add the --force flag.",
                        width=68
                    ))
                    sys.exit(msg)

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
        sys_names = [s for s in self.supported_systems_data.sections()
                     if s != "DEFAULT"]
        sys_name_from_hostname = None
        for sys_name in sys_names:
            # Strip the keys of comments:
            #
            #   Don't match anything following whitespace and a '#'.
            #                                  |
            #   Match anything that's not      |
            #        a '#' or whitespace.      |
            #                      vvvvv    vvvvvvvv
            keys = [re.findall(r"([^#^\s]*)(?:\s*#.*)?", key)[0]
                    for key in self.supported_systems_data[sys_name].keys()]

            # Keys are treated as REGEXes.
            matches = []
            for key in keys:
                matches += re.findall(key, hostname)
            if len(matches) > 0:
                sys_name_from_hostname = sys_name
                break
        return sys_name_from_hostname

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
        sys_names = [s for s in self.supported_systems_data.sections()
                     if s != "DEFAULT"]
        sys_name_from_build_names = [_ for _ in sys_names if _ in
                                     self.build_name]
        if len(sys_name_from_build_names) > 1:
            msg = self.get_msg_for_list(
                "Cannot specify more than one system name in the build name\n"
                "You specified", sys_name_from_build_names
            )
            sys.exit(msg)
        elif len(sys_name_from_build_names) == 0:
            sys_name_from_build_name = None
        else:
            sys_name_from_build_name = sys_name_from_build_names[0]
        return sys_name_from_build_name

    def parse_supported_systems_file(self):
        """
        Parse the ``supported-systems.ini`` file and store the corresponding
        ``configparserenhanceddata`` object as :attr:`supported_systems_data`.
        """
        if self.supported_systems_data is None:
            self.supported_systems_data = ConfigParserEnhanced(
                self.supported_systems_file
            ).configparserenhanceddata

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

    def get_msg_for_list(self, msg, item_list, kind="ERROR"):
        """
        Helper function to generate a message using a list. Produces a message
        like the following::

            +=================================================================+
            |   {kind}:  {msg}
            |     - {item_list[0]}
            |     - {item_list[1]}
            |     - ...
            |     - {item_list[n]}
            +=================================================================+

        Parameters:
            msg (str):  The error message to print.  Can be multiline.
            item_list (list):  The list of items to print in the error message.
            kind (str):  The kind of message being generated, e.g., "ERROR",
                "WARNING", "INFO", etc.

        Returns:
            str:  The formatted message.
        """
        extras = ""
        for item in item_list:
            extras += f"  - {item}\n"
        msg = self.get_formatted_msg(msg, kind=kind, extras=extras)
        return msg
