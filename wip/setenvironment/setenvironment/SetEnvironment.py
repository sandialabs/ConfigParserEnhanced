#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
SetEnvironment Utility for environment vars and modules.



Todo:
    Fill in the docstring for this file.

:Authors:
    - William C. McLendon III <wcmclen@sandia.gov>

:Version: 0.0.1
"""
from __future__ import print_function

import os
import re

try:
    # @final decorator, requires Python 3.8.x
    from typing import final                                                                        # pragma: no cover
except ImportError:                                                                                 # pragma: no cover
    pass                                                                                            # pragma: no cover

from configparserenhanced import *
import pathlib

from . import ModuleHelper


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

    Todo:
        Add docstrings to functions and handlers.

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

        Todo: add example of structure of the ``actions`` object.

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


    def pretty_print_actions(self):
        """Pretty print the list of actions that ``apply()`` would execute.

        This is a helper function that will print out a listing of the actions
        that will be executed when ``apply()`` is called.

        For example, output might look like:

            >>> setenvobj.pretty_print_actins()
            Actions
            =======
            --> envvar-set     : FOO="bar"
            --> envvar-append  : FOO="${FOO}:baz"
            --> envvar-prepend : FOO="foo:${FOO}"
            --> envvar-set     : BAR="foo"
            --> envvar-unset   : FOO
            --> module-purge   :
            --> module-use     : setenvironment/unittests/modulefiles
            --> module-load    : gcc/4.8.4
            --> module-load    : boost/1.10.1
            --> module-load    : gcc/4.8.4
            --> module-unload  : boost
            --> module-swap    : gcc gcc/7.3.0

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


    def pretty_print_envvars(self, envvar_filter=None, filtered_keys_only=False) -> int:
        """
        Print out a filtered list of environment variables. This routine provides
        a simplified view of the environment variables on a system since sometimes
        just printing out the contents of all envvars on a system can result in very
        cluttered console logs that are difficult to read through.

        `envvar_filter` contains a list of strings that is matched against envvar
        key names, if the envvar key contains one of the strings in envvar_filter
        then we print both the envvar and its value. Otherwise, we print just the
        envvar name.

        If we set filtered_keys_only to True then we ONLY print out envvars that
        matched envvar_filter.

        Example:

            >>> envvar_filter=["TEST_SETENVIRONMENT_", "FOO", "BAR", "BAZ"]
            >>> parser.pretty_print_envvars(envvar_filter, True)
            +====================================================================+
            |   P R I N T   E N V I R O N M E N T   V A R S
            +====================================================================+
            [envvar]: BAR = foo
            [envvar]: TEST_SETENVIRONMENT_GCC_VER = 7.3.0
            >>>

        In this case, we only printed out environment variables that contained
        either ``TEST_SETENVIRONMENT_``, ``FOO``, ``BAR`` or ``BAZ`` in the *name* of
        the environment variable and nothing else.

        Arguments:
            envvar_filter (list): a list of keys to print out the value.
                all envvar values are printed if omitted.
                Default: None
            filtered_keys_only (bool): If true, we only display envvars that contain
                a match to an entry in `envvar_filter`.
                If false, we display the keys of all envvars and key+value of envvars
                that matched a filter in the `envvar_filter` list.
                Default: False

        Returns:
            int 0

        Todo:
            This could probably be moved outside of this class since it's not
            really directly relevant to the environment setting stuff. Perhaps
            if we develop some soft of 'helpers' or 'utilities' module sometime.
        """
        if envvar_filter is not None:
            assert isinstance(envvar_filter, list)

        # Prefix for each envvar line
        prefix="[envvar]:"

        # Print a banner
        print("+" + "="*68 + "+")
        print("|   P R I N T   E N V I R O N M E N T   V A R S")
        print("+" + "="*68 + "+")
        for k,v in os.environ.items():
            matched_key = False
            if envvar_filter is not None:
                for f in envvar_filter:
                    if f in k:
                        matched_key = True
                        break
            else:
                filtered_keys_only = False

            if filtered_keys_only == False or matched_key:
                print("{} {}".format(prefix, k), end="")
                if envvar_filter is None:
                    print(" = {}".format(v), end="")
                elif matched_key:
                    print(" = {}".format(v), end="")
                print("")
        return 0


    def apply(self) -> int:
        """Apply the set of instructions stored in ``actions``.

        This method will cause the actions that are defined to be
        executed.

        Returns:
            integer: 0 if successful, nonzero if something went wrong that did not
                trigger an exception of some kind.

        Todo:
            - Print out some useful log message(s) indicating that actions have occurred.
              maybe a banner also or something?
        """
        output = 0

        for iaction in self.actions:
            rval  = 0
            op    = iaction['op']
            value = iaction['value']

            if 'envvar' in iaction.keys():
                rval = self._apply_envvar(op, envvar_name=iaction['envvar'], envvar_value=value)

            if 'module' in iaction.keys():
                rval = self._apply_module(op, module_name=iaction['module'], module_value=value)

            output = max(output, rval)

        return output


    # --------------------
    #   H A N D L E R S
    # --------------------


    def handler_envvar_set(self, section_name, handler_parameters) -> int:
        """Handler: for envvar-set operations.

        Handles operations that wish to *set* an environment variable.

        Returns:
            integer: An integer value indicating if the handler was successful.
                - 0     : SUCCESS
                - [1-10]: Reserved for future use (WARNING)
                - > 10  : An unknown failure occurred (SERIOUS)

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
                - 0     : SUCCESS
                - [1-10]: Reserved for future use (WARNING)
                - > 10  : An unknown failure occurred (SERIOUS)

        """
        return self._helper_envvar_common(section_name, handler_parameters)


    def handler_envvar_prepend(self, section_name, handler_parameters) -> int:
        """Handler: for envvar-prepend operations.

        Handles operations that wish to *prepend* an environment variable.

        Returns:
            integer: An integer value indicating if the handler was successful.
                - 0     : SUCCESS
                - [1-10]: Reserved for future use (WARNING)
                - > 10  : An unknown failure occurred (SERIOUS)

        """
        return self._helper_envvar_common(section_name, handler_parameters)


    def handler_envvar_remove(self, section_name, handler_parameters) -> int:
        """Handler: for envvar-remove operations.

        Removes all envvar operations that operate on the specified
        envvar from the list of actions to be executed by SetEnvironment.

        Returns:
            integer: An integer value indicating if the handler was successful.
                - 0     : SUCCESS
                - [1-10]: Reserved for future use (WARNING)
                - > 10  : An unknown failure occurred (SERIOUS)
        """
        self.enter_handler(handler_parameters)

        # -----[ Handler Content Start ]-------------------
        data_shared = handler_parameters.data_shared['setenvironment']
        envvar_name = handler_parameters.op_params[1]

        new_data_shared = []
        for idata in data_shared:

            if 'envvar' in idata.keys():
                if idata['envvar'] != envvar_name:
                    new_data_shared.append(idata)
                else:
                    self.debug_message(1, "Removed entry:{}".format(idata))                         # Console
            else:
                new_data_shared.append(idata)

        handler_parameters.data_shared['setenvironment'] = new_data_shared
        # -----[ Handler Content End ]-------------------

        self.exit_handler(handler_parameters)
        return 0


    def handler_envvar_unset(self, section_name, handler_parameters) -> int:
        """Handler: for envvar-unset operations.

        Handles operations that wish to *unset* an environment variable.

        Returns:
            integer: An integer value indicating if the handler was successful.
                - 0     : SUCCESS
                - [1-10]: Reserved for future use (WARNING)
                - > 10  : An unknown failure occurred (SERIOUS)
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
                - 0     : SUCCESS
                - [1-10]: Reserved for future use (WARNING)
                - > 10  : An unknown failure occurred (SERIOUS)
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
                - 0     : SUCCESS
                - [1-10]: Reserved for future use (WARNING)
                - > 10  : An unknown failure occurred (SERIOUS)

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
                - 0     : SUCCESS
                - [1-10]: Reserved for future use (WARNING)
                - > 10  : An unknown failure occurred (SERIOUS)

        """
        self.enter_handler(handler_parameters)

        # -----[ Handler Content Start ]-------------------
        data_shared = handler_parameters.data_shared['setenvironment']
        module_name = handler_parameters.op_params[1]

        # do it all in a lambda? Look ma, I did it all in "one line" that nobody can read.
        # yeah, let's not do this. Keeping the comment here though until I can capture this
        # in a snippet on Gitlab or something ;)
        #tmp_shared = list(filter(lambda x:
        #    (('module' in x.keys()) and (x['module'] != module_name) and (module_name not in x['value'])) or
        #     ('module' not in x.keys()), data_shared))

        new_data_shared = []
        for idata in data_shared:

            if 'module' in idata.keys():
                # Note: idata['value'] can be None in some cases
                if (idata['module'] != module_name) and ((idata['value'] == None) or (module_name not in idata['value'])):
                    new_data_shared.append(idata)
                else:
                    self.debug_message(1, "Removed entry:{}".format(idata))                         # Console
            else:
                new_data_shared.append(idata)

        handler_parameters.data_shared['setenvironment'] = new_data_shared
        # -----[ Handler Content End ]-------------------

        self.exit_handler(handler_parameters)
        return 0


    def handler_module_swap(self, section_name, handler_parameters) -> int:
        """

        Args:
            section_name (str): The section name string.
            handler_parameters (object): A HandlerParameters object containing
                the state data we need for this handler.

        Returns:
            integer: An integer value indicating if the handler was successful.
                - 0     : SUCCESS
                - [1-10]: Reserved for future use (WARNING)
                - > 10  : An unknown failure occurred (SERIOUS)

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
                - 0     : SUCCESS
                - [1-10]: Reserved for future use (WARNING)
                - > 10  : An unknown failure occurred (SERIOUS)

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
                - 0     : SUCCESS
                - [1-10]: Reserved for future use (WARNING)
                - > 10  : An unknown failure occurred (SERIOUS)

        """
        return self._helper_module_common(section_name, handler_parameters)


    def handler_finalize(self, section_name, handler_parameters) -> int:
        """Finalize a recursive parse search.

        Returns:
            integer value
                - 0     : SUCCESS
                - [1-10]: Reserved for future use (WARNING)
                - > 10  : An unknown failure occurred (SERIOUS)

        Todo:
            Implement the 'cleanup' portion of finalize. See inline comment(s).
        """
        self.enter_handler(handler_parameters)

        # Save out the results into the 'actions' list for the class.
        self.actions = handler_parameters.data_shared["setenvironment"]

        # Todo:
        # Invoke a cleanup step here to curate the list of actions.
        # primarily, this means handle things like the 'remove' operations.

        self.exit_handler(handler_parameters)
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
                - 0     : SUCCESS
                - [1-10]: Reserved for future use (WARNING)
                - > 10  : An unknown failure occurred (SERIOUS)
        """
        self.enter_handler(handler_parameters)

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

        self.exit_handler(handler_parameters)
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
                {'op': 'module-load',   'module': 'dummy-gcc',    'value': '4.8.4'},
                {'op': 'module-load',   'module': 'dummy-boost',  'value': '1.10.1'},
                {'op': 'module-load',   'module': 'dummy-python', 'value': '3.9.0'},
                {'op': 'module-load',   'module': 'dummy-gcc',    'value': '4.8.4'},
                {'op': 'module-unload', 'module': 'dummy-boost',  'value': ''},
                {'op': 'module-remove', 'module': 'dummy-python', 'value': ''},
            ]

        Args:
            section_name (str): The section name string.
            handler_parameters (object): A HandlerParameters object containing
                the state data we need for this handler.

        Returns:
            integer: An integer value indicating if the handler was successful.
                - 0     : SUCCESS
                - [1-10]: Reserved for future use (WARNING)
                - > 10  : An unknown failure occurred (SERIOUS)
        """
        self.enter_handler(handler_parameters)

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

        self.debug_message(3, "--> Append to 'setenvironment' action list:")                        # Console
        self.debug_message(3, "    {}".format(action))                                              # Console
        data_shared_actions_ref.append(action)

        self.enter_handler(handler_parameters)
        return 0


    def _expand_envvars_in_string(self, string_in) -> str:
        """
        Take an input string that may contain environment variables in the style
        of BASH shell environment vars (i.e., "${foobar}") and replace them with
        the actual environment variables.

        Returns:
             A string that contains the contents of any `${ENVVAR}` entries expanded
             inline into the string.

        Raises:
             KeyError: Required environment variable does not exist.

        Todo:
            Test this.
        """
        regexp = re.compile(r"(\$\{(\S*)\})")
        string_out = string_in
        for m in re.finditer(regexp, string_out):
            #v = m.group(1)  # The full ENVVAR sequence: ${VARNAME}
            s = m.group(2)  # Just the ENVVAR itself: VARNAME
            if(s in os.environ.keys()):
                string_out = re.sub(regexp, os.environ[s], string_in)
            else:
                msg = "Required environment variable `{}` does not exist.".format(s)
                raise KeyError(msg)
        return string_out


    def _apply_envvar(self, operation, envvar_name, envvar_value) -> int:
        """Apply ENVVAR operations

        Currently supported envvar operations are:

        - ``envvar-append``
        - ``envvar-prepend``
        - ``envvar-set``
        - ``envvar-unset``

        Args:
            operation (str): The operation to be executed (i.e., ``envvar-set``)
            envvar_name (str): The name of the environment variable.
            envvar_value (str,None): The value to assign the environment variable.

        Returns:
            integer: 0 if successful.

        Raises:
            KeyError: If an envvar_value contains a variable (``${envvar_name}``)
                that references an environment variable that does not exist.
            TypeError: if any of the parameters fail a typecheck on method entry.
        """
        # Validate parameters
        if not isinstance(operation, (str)):
            raise TypeError("operation must be a string.")
        if not isinstance(envvar_name, (str)):
            raise TypeError("envvar_name must be a string.")
        if not isinstance(envvar_value, (str, type(None))):
            raise TypeError("envvar_value must be either `string` or `None` types.")

        # Debug Message
        self.debug_message(2, "{} :: {} - {}".format(operation, envvar_name, envvar_value))

        # Detect if the envvar already exists, and if so get its value.
        envvar_exists = envvar_name in os.environ.keys()
        envvar_value_old = [os.environ[envvar_name]] if envvar_exists else []

        # Expand any `${envvar}` entries in the envvar string to
        # contain the actual envvar value.
        if envvar_value != None:
            envvar_value = self._expand_envvars_in_string(envvar_value)

        # Execute `envvar` operations:
        if operation == "envvar-set":
            os.environ[envvar_name] = envvar_value
            self.debug_message(3, "envvar :: {} = {}".format(envvar_name, envvar_value))

        # Todo: update documentation to note that we use `os.pathsep` for the separator
        elif operation == "envvar-append":
            _tmp = envvar_value_old + [ envvar_value ]
            newval = os.pathsep.join(_tmp)
            os.environ[envvar_name] = newval
            self.debug_message(3, "envvar :: {} = {}".format(envvar_name, newval))

        elif operation == "envvar-prepend":
            _tmp = [ envvar_value ] + envvar_value_old
            newval = os.pathsep.join(_tmp)
            os.environ[envvar_name] = newval
            self.debug_message(3, "envvar :: {} = {}".format(envvar_name, newval))

        elif operation == "envvar-unset":
            del os.environ[envvar_name]
            self.debug_message(3, "envvar :: del {}".format(envvar_name))

        else:
            # This is reachable if someone creates a new handler for
            # an envvar-<action> but does not update this if/elif
            # case statement.
            raise ValueError("Unknown envvar operation: {}".format(operation))

        return 0


    def _apply_module(self, operation, module_name, module_value) -> int:
        """Apply MODULE operations

        Currently supported MODULE operations are:

        - ``module-load``
        - ``module-purge``
        - ``module-swap``
        - ``module-unload``
        - ``module-use``

        Note:
            ``module-remove`` is handled in the handler itself since it's
            context is most applicable at the time of parsing.

        Args:
            operation (str): The operation to be executed (i.e., ``module-load``)
            module_name (str): The name of the module.
            module_value (str,None): The value from the operation field.

        Returns:
            integer: 0 if successful.

        Raises:
            TypeError: if any of the parameters fail a typecheck on method entry.
            ValueError: if the operation provided is invalid.
        """
        # Validate parameters
        if not isinstance(operation, (str)):
            raise TypeError("operation must be a string.")
        if not isinstance(module_name, (str, type(None))):
            raise TypeError("module_name must be either `string` or `None` types.")
        if not isinstance(module_value, (str, type(None))):
            raise TypeError("module_value must be either `string` or `None` types.")

        # Debug Message
        self.debug_message(2, "{} :: {} - {}".format(operation, module_name, module_value))

        # Process the commands (order by most likely operation)
        rval = 0
        if operation == "module-load":
            _tmp = "{}/{}".format(module_name, module_value)
            rval = ModuleHelper.module("load", _tmp)

        elif operation == "module-unload":
            rval = ModuleHelper.module("unload", module_name)

        elif operation == "module-swap":
            module_old = module_name
            module_new = module_value
            rval = ModuleHelper.module("swap", module_old, module_new)

        elif operation == "module-use":
            # Check the path existence for a `module use`. This could be moved to ModuleHelper later?
            if not pathlib.Path(module_value).exists():
                msg = "Requested path `{}` for `module use` does not exist.".format(module_value)
                self.exception_control_event("CRITICAL", FileNotFoundError, msg)

            rval = ModuleHelper.module("use", module_value)

        elif operation == "module-purge":
            rval = ModuleHelper.module("purge")

        else:
            raise ValueError("Unknown module operation: {}".format(operation))

        if rval != 0:
            message = "MODULE operation {} failed with {} rval.".format(operation, rval)
            self.exception_control_event("CRITICAL", RuntimeError, message)

        return rval


# EOF


# Notes
"""
1) The separator for envvars defaults to the os.pathsep (:), but this might
   be different for other things like CMake targets. We could add a new command
   like `envvar-set-separator` that could be used to change a property that caches
   the default separator which could also be changed during class instantiation.

2) Another option might be to enhance ConfigParserEnhanced to support Triples.
"""
