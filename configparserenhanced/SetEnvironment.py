#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
SetEnvironment module documentation goes here.

Todo:
    Document me!

:Authors:
    William C. McLendon III
:Version: 0.0.1-alpha

"""
from __future__ import print_function

import os
#import re
#import sys

try:
    # @final decorator, requires Python 3.8.x
    from typing import final                                                                        # pragma: no cover
except ImportError:                                                                                 # pragma: no cover
    pass                                                                                            # pragma: no cover

from . import ConfigParserEnhanced


# ===================================
#  S U P P O R T   F U N C T I O N S
# ===================================



# ===============================
#   M A I N   C L A S S
# ===============================



class SetEnvironment(ConfigParserEnhanced):
    """Handle Environment Operations using a .ini based configuration.

    This class adds handling capabilities for setting and updating
    the system environment one would use. Currently this class supports
    two primary kinds of environment operations:

    - **module** operations such as *environment modules* and *lmod*
    - **environment variable** operations.

    .. configparser reference:
        https://docs.python.org/3/library/configparser.html
    .. docstrings style reference:
        https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html
    """
    def __init__(self, filename):
        self.inifilepath = filename


    # -----------------------
    #   P R O P E R T I E S
    # -----------------------


    @property
    def actions(self) -> list:
        """
        The *actions* property contains the list of actions generated for
        the most recent section that has been parsed. This is overwritten when
        we execute a new parse.

        Returns:
            list: A *list* containing the sequence of actions that
            SetEnvironment has extracted from the configuration
            file section.
        """
        if not hasattr(self, '_actions'):
            self._actions = []
        return self._actions


    @actions.setter
    def actions(self, value) -> list:
        if not isinstance(value, (list)):
            raise TypeError("actions must be a list.")
        self._actions = value
        return self._actions


    # ------------------------------
    #   P U B L I C   M E T H O D S
    # ------------------------------

    def print_actions(self):
        """
        This is a stub-in function (WIP)

        Todo:
            Replace this or document it :p
        """
        print("Actions")
        print("=======")
        for action in self.actions:
            operation = action['op']

            print("--> {:<14} : ".format(operation), end="")
            if operation == "module-purge":
                print("")
            elif operation == "module-use":
                print("{}".format(action['value']))
            elif operation == "module-load":
                print("{}/{}".format(action['module'], action['value']))
            elif operation == "module-swap":
                print("{} {}".format(action['module'], action['value']))
            elif operation == "module-unload":
                print("{}".format(action['module']))
            elif operation == "envvar-set":
                print("{}=\"{}\"".format(action['envvar'], action['value']))
            elif operation == "envvar-prepend":
                arg = "${%s}"%(action['envvar'])
                print("{}=\"{}:{}\"".format(action['envvar'],action['value'],arg))
            elif operation == "envvar-append":
                arg = "${%s}"%(action['envvar'])
                print("{}=\"{}:{}\"".format(action['envvar'],arg,action['value']))
            elif operation == "envvar-unset":
                print("{}".format(action['envvar']))
            else:
                print("(unhandled) {}".format(action))

        return


    # --------------------
    #   H A N D L E R S
    # --------------------


    def handler_envvar_set(self, section_name, handler_parameters) -> int:
        """Handler: for envvar-set operations.

        Handles operations that wish to *set* an environment variable.

        Returns:
            integer: An integer value indicating if the handler was successful.
                0     : SUCCESS
                [1-10]: Reserved for future use (WARNING)
                > 10  : An unknown failure occurred (SERIOUS)
        """
        return self._helper_envvar_common(section_name, handler_parameters)


    def handler_envvar_append(self, section_name, handler_parameters) -> int:
        """Handler: for envvar-append operations.

        Append operations will set or append a value to an environment variable
        (envvar). If the envvar exists already then we will *append* the value to
        it with a separator. If the envvar does not already exist, we will create
        one with the value set.

        For example, if the envvar is "foo" and the value is "bar", if we already
        have ``foo = "bif"`` then the result is ``foo = "bif:bar"``, but if ``foo``
        did not already exist then the result would be ``foo = "bar"``

        Returns:
            integer: An integer value indicating if the handler was successful.
                0     : SUCCESS
                [1-10]: Reserved for future use (WARNING)
                > 10  : An unknown failure occurred (SERIOUS)
        """
        return self._helper_envvar_common(section_name, handler_parameters)


    def handler_envvar_prepend(self, section_name, handler_parameters) -> int:
        """Handler: for envvar-prepend operations.

        Handles operations that wish to *prepend* an environment variable.

        Returns:
            integer: An integer value indicating if the handler was successful.
                0     : SUCCESS
                [1-10]: Reserved for future use (WARNING)
                > 10  : An unknown failure occurred (SERIOUS)
        """
        return self._helper_envvar_common(section_name, handler_parameters)


    def handler_envvar_remove(self, section_name, handler_parameters) -> int:
        """Handler: for envvar-remove operations.

        Removes all envvar operations that operate on the specified
        envvar from the list of actions to be executed by SetEnvironment.

        Returns:
            integer: An integer value indicating if the handler was successful.
                0     : SUCCESS
                [1-10]: Reserved for future use (WARNING)
                > 10  : An unknown failure occurred (SERIOUS)
        """
        entry = handler_parameters.raw_option
        handler_name = handler_parameters.handler_name
        self.debug_message(1, "Enter handler: {}".format(handler_name))                             # Console
        self.debug_message(2, "--> option: {}".format(handler_parameters.raw_option))               # Console
        self._loginfo_add('handler-entry', {'name': handler_name, 'entry': entry})                  # Logging

        # -----[ Handler Content Start ]-------------------
        data_shared = handler_parameters.data_shared['setenvironment']
        envvar_name = handler_parameters.op_params[1]

        new_data_shared = []
        for idata in data_shared:

            if 'envvar' in idata.keys():
                if idata['envvar'] != envvar_name:
                    new_data_shared.append(idata)
                else:
                    self.debug_message(1, "Removed entry:{}".format(idata))
            else:
                new_data_shared.append(idata)

        handler_parameters.data_shared['setenvironment'] = new_data_shared
        # -----[ Handler Content End ]-------------------

        self.debug_message(1, "Exit handler: {}".format(handler_name))                              # Console
        self._loginfo_add('handler-exit', {'name': handler_name, 'entry': entry})                   # Logging
        return 0


    def handler_envvar_unset(self, section_name, handler_parameters) -> int:
        """Handler: for envvar-unset operations.

        Handles operations that wish to *unset* an environment variable.

        Returns:
            integer: An integer value indicating if the handler was successful.
                0     : SUCCESS
                [1-10]: Reserved for future use (WARNING)
                > 10  : An unknown failure occurred (SERIOUS)
        """
        return self._helper_envvar_common(section_name, handler_parameters)


    def handler_module_load(self, section_name, handler_parameters) -> int:
        """

        Args:
            section_name (str): The section name string.
            handler_parameters (object): A HandlerParameters object containing
                the state data we need for this handler.

        Returns:
            integer: An integer value indicating if the handler was successful.
                0     : SUCCESS
                [1-10]: Reserved for future use (WARNING)
                > 10  : An unknown failure occurred (SERIOUS)
        """
        return self._helper_module_common(section_name, handler_parameters)


    def handler_module_purge(self, section_name, handler_parameters) -> int:
        """

        Args:
            section_name (str): The section name string.
            handler_parameters (object): A HandlerParameters object containing
                the state data we need for this handler.

        Returns:
            integer: An integer value indicating if the handler was successful.
                0     : SUCCESS
                [1-10]: Reserved for future use (WARNING)
                > 10  : An unknown failure occurred (SERIOUS)
        """
        return self._helper_module_common(section_name, handler_parameters)


    def handler_module_remove(self, section_name, handler_parameters) -> int:
        """
        Removes all module operations that operate on the labeled module from
        the action lists at the time this command is encountered.

        Args:
            section_name (str): The section name string.
            handler_parameters (object): A HandlerParameters object containing
                the state data we need for this handler.

        Returns:
            integer: An integer value indicating if the handler was successful.
                0     : SUCCESS
                [1-10]: Reserved for future use (WARNING)
                > 10  : An unknown failure occurred (SERIOUS)
        """
        entry = handler_parameters.raw_option
        handler_name = handler_parameters.handler_name
        self.debug_message(1, "Enter handler: {}".format(handler_name))                             # Console
        self.debug_message(2, "--> option: {}".format(handler_parameters.raw_option))               # Console
        self._loginfo_add('handler-entry', {'name': handler_name, 'entry': entry})                  # Logging

        # -----[ Handler Content Start ]-------------------
        data_shared = handler_parameters.data_shared['setenvironment']
        module_name = handler_parameters.op_params[1]

        # do it all in a lambda? Look ma, I did it in one line that nobody can read.
        #tmp_shared = list(filter(lambda x:
        #    (('module' in x.keys()) and (x['module'] != module_name) and (module_name not in x['value'])) or
        #     ('module' not in x.keys()), data_shared))

        new_data_shared = []
        for idata in data_shared:

            if 'module' in idata.keys():
                if idata['module'] != module_name and module_name not in idata['value']:
                    new_data_shared.append(idata)
                else:
                    self.debug_message(1, "Removed entry:{}".format(idata))
            else:
                new_data_shared.append(idata)

        handler_parameters.data_shared['setenvironment'] = new_data_shared
        # -----[ Handler Content End ]-------------------

        self.debug_message(1, "Exit handler: {}".format(handler_name))                              # Console
        self._loginfo_add('handler-exit', {'name': handler_name, 'entry': entry})                   # Logging
        return 0


    def handler_module_swap(self, section_name, handler_parameters) -> int:
        """

        Args:
            section_name (str): The section name string.
            handler_parameters (object): A HandlerParameters object containing
                the state data we need for this handler.

        Returns:
            integer: An integer value indicating if the handler was successful.
                0     : SUCCESS
                [1-10]: Reserved for future use (WARNING)
                > 10  : An unknown failure occurred (SERIOUS)
        """
        return self._helper_module_common(section_name, handler_parameters)


    def handler_module_unload(self, section_name, handler_parameters) -> int:
        """

        Args:
            section_name (str): The section name string.
            handler_parameters (object): A HandlerParameters object containing
                the state data we need for this handler.

        Returns:
            integer: An integer value indicating if the handler was successful.
                0     : SUCCESS
                [1-10]: Reserved for future use (WARNING)
                > 10  : An unknown failure occurred (SERIOUS)
        """
        return self._helper_module_common(section_name, handler_parameters)


    def handler_module_use(self, section_name, handler_parameters) -> int:
        """

        Args:
            section_name (str): The section name string.
            handler_parameters (object): A HandlerParameters object containing
                the state data we need for this handler.

        Returns:
            integer: An integer value indicating if the handler was successful.
                0     : SUCCESS
                [1-10]: Reserved for future use (WARNING)
                > 10  : An unknown failure occurred (SERIOUS)
        """
        return self._helper_module_common(section_name, handler_parameters)


    def handler_finalize(self, section_name, handler_parameters) -> int:
        """Finalize a recursive parse search.

        Returns:
            integer value
                0     : SUCCESS
                [1-10]: Reserved for future use (WARNING)
                > 10  : An unknown failure occurred (SERIOUS)

        Todo:
            Implement the 'cleanup' portion of finalize. See inline comment(s).
        """
        handler_name = handler_parameters.handler_name

        self.debug_message(1, "Enter handler: {}".format(handler_name))                             # Console
        self.debug_message(1, "--> option: {}".format(handler_parameters.raw_option))               # Console
        self._loginfo_add('handler-entry', {'name': handler_name})                                  # Logging

        # Save out the results into the 'actions' list for the class.
        self.actions = handler_parameters.data_shared["setenvironment"]

        # Todo:
        # Invoke a cleanup step here to curate the list of actions.
        # primarily, this means handle things like the 'remove' operations.

        self.debug_message(1, "Exit handler: {}".format(handler_name))                              # Console
        self._loginfo_add('handler-exit', {'name': handler_name})                                   # Logging
        return 0

    # ---------------
    #  H E L P E R S
    # ---------------


    def _helper_envvar_common(self, section_name, handler_parameters) -> int:
        """Common handler for envvar actions

        All the *envvar* actions do basically the same thing so we can move the
        general handling of them into a more generic handler method.

        This helper appends entries to ``handler_parameters.data_shared``
        data structure's "setenvironment" entry. Results look something like:

            >>> handler_parameters.data_shared['setenvironment']
            [
                {'op': 'envvar-set',     'envvar': 'FOO', 'value': 'bar'},
                {'op': 'envvar-append',  'envvar': 'FOO', 'value': 'baz'},
                {'op': 'envvar_prepend', 'envvar': 'FOO', 'value': 'foo'},
                {'op': 'envvar-set',     'envvar': 'BAR', 'value': 'foo'},
                {'op': 'envvar-set',     'envvar': 'BAZ', 'value': 'bar'},
                {'op': 'envvar_unset',   'envvar': 'FOO', 'value': 'None'},
                {'op': 'envvar_remove',  'envvar': 'BAZ', 'value': 'None'}
            ]

        Args:
            section_name (str): The section name string.
            handler_parameters (object): A HandlerParameters object containing
                the state data we need for this handler.

        Returns:
            integer: An integer value indicating if the handler was successful.
                0     : SUCCESS
                [1-10]: Reserved for future use (WARNING)
                > 10  : An unknown failure occurred (SERIOUS)
        """
        entry = handler_parameters.raw_option
        handler_name = handler_parameters.handler_name

        self.debug_message(1, "Enter handler: {}".format(handler_name))                             # Console
        self.debug_message(2, "--> option: {}".format(handler_parameters.raw_option))               # Console
        self._loginfo_add('handler-entry', {'name': handler_name, 'entry': entry})                  # Logging

        operation_ref    = handler_parameters.op_params[0]
        envvar_name_ref  = handler_parameters.op_params[1]
        envvar_value_ref = handler_parameters.value
        data_shared_ref  = handler_parameters.data_shared

        if not 'setenvironment' in data_shared_ref.keys():
            handler_parameters.data_shared['setenvironment'] = []

        data_shared_actions_ref = handler_parameters.data_shared['setenvironment']

        action = {'op'    : operation_ref,
                  'envvar': envvar_name_ref,
                  'value' : envvar_value_ref
                 }

        self.debug_message(3, "--> Append to 'setenvironment' action list:")                        # Console
        self.debug_message(3, "    {}".format(action))                                              # Console
        data_shared_actions_ref.append(action)

        self.debug_message(1, "Exit handler: {}".format(handler_name))                              # Console
        self._loginfo_add('handler-exit', {'name': handler_name, 'entry': entry})                   # Logging
        return 0


    def _helper_module_common(self, section_name, handler_parameters) -> int:
        """Common handler for module actions

        All the *module* actions care about the same sets of parameters so we
        can use this to add the appropriate entry to the actions list when
        processing the .ini file.

        This helper appends entries to ``handler_parameters.data_shared``
        data structure's "setenvironment" entry. Results look something like:

            >>> handler_parameters.data_shared['setenvironment']
            [
                {'op': 'module-purge',  'module': None,          'value': ''},
                {'op': 'module-use',    'module': None,          'value': '/foo/bar/baz'},
                {'op': 'module-load',   'module': 'sems-gcc',    'value': '4.8.4'},
                {'op': 'module-load',   'module': 'sems-boost',  'value': '1.10.1'},
                {'op': 'module-load',   'module': 'sems-python', 'value': '3.9.0'},
                {'op': 'module-load',   'module': 'sems-gcc',    'value': '4.8.4'},
                {'op': 'module-unload', 'module': 'sems-boost',  'value': ''},
                {'op': 'module-remove', 'module': 'sems-python', 'value': ''},
            ]

        Args:
            section_name (str): The section name string.
            handler_parameters (object): A HandlerParameters object containing
                the state data we need for this handler.

        Returns:
            integer: An integer value indicating if the handler was successful.
                0     : SUCCESS
                [1-10]: Reserved for future use (WARNING)
                > 10  : An unknown failure occurred (SERIOUS)
        """
        entry = handler_parameters.raw_option
        handler_name = handler_parameters.handler_name

        self.debug_message(1, "Enter handler: {}".format(handler_name))                             # Console
        self.debug_message(2, "--> option: {}".format(handler_parameters.raw_option))               # Console
        self._loginfo_add('handler-entry', {'name': handler_name, 'entry': entry})                  # Logging

        operation_ref    = handler_parameters.op_params[0]
        module_name_ref  = handler_parameters.op_params[1]
        module_value_ref = handler_parameters.value
        data_shared_ref  = handler_parameters.data_shared

        if not 'setenvironment' in data_shared_ref.keys():
            handler_parameters.data_shared['setenvironment'] = []

        data_shared_actions_ref = handler_parameters.data_shared['setenvironment']

        action = {'op'    : operation_ref,
                  'module': module_name_ref,
                  'value' : module_value_ref
                 }

        self.debug_message(3, "--> Append to 'setenvironment' action list:")
        self.debug_message(3, "    {}".format(action))
        data_shared_actions_ref.append(action)

        self.debug_message(1, "Exit handler: {}".format(handler_name))                              # Console
        self._loginfo_add('handler-exit', {'name': handler_name, 'entry': entry})                   # Logging
        return 0

# EOF
