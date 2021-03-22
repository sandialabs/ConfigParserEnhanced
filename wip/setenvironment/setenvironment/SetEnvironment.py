#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
SetEnvironment Utility for environment vars and modules.



Todo:
    Fill in the docstring for this file.

:Authors:
    - William C. McLendon III <wcmclen@sandia.gov>

:Version: 0.2.0
"""
from __future__ import print_function

import inspect
import os
import re
from textwrap import dedent

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


def envvar_assign(envvar_name, envvar_value, allow_empty=True):
    """Assign an environment variable.

    Assigns an environment variable (envvar) to a set value.
    Optionally raise an exception if the value is empty.

    Args:
        envvar_name (str): The name of the envvar.
        envvar_value (str): The value to set to the envvar.
        allow_empty (bool): If False, we throw a ``ValueError`` if
            ``envvar_value`` is empty. Default: True.

    Raises:
        TypeError: if:

            - ``envvar_value`` is not a string.
            - ``envvar_value`` is not a string.
            - ``allow_empty`` is not a bool.

        ValueError if:

            - ``allow_empty`` is True *and* ``envvar_value`` is an empty string.
    """
    if not isinstance(envvar_name, (str)):
        raise TypeError("`envvar_name` must be a string.")
    if not isinstance(envvar_value, (str)):
        raise TypeError("`envvar_value` must be a string.")
    if not isinstance(allow_empty, (bool)):
        raise TypeError("`allow_empty` must be a boolean.")
    if not allow_empty and envvar_value == "":
        raise ValueError("`envvar_value` must not be empty.")
    os.environ[envvar_name] = envvar_value
    return


def envvar_find_in_path(exe_file) -> str:
    """Find an executable file in the current search path.

    This function attempts to locate an executable app in the current
    search path. If found it will return the path to the application,
    otherwise an exception is raised.

    Args:
        exe_file (str, Path): An executable application file to locate.

    Raises:
        FileNotFoundError: If the executable is not located we will
            raise this exception.
    """
    import distutils.spawn
    import shutil

    output = None
    try:
        output = distutils.spawn.find_executable(exe_file)
        if output is None:
            raise FileNotFoundError("Unable to find {}".format(exe_file))
    except:
        output = shutil.which(exe_file)
        if output is None:
            raise FileNotFoundError("Unable to find {}".format(exe_file))

    return str(output)


def envvar_op(op, envvar_name, envvar_value="", allow_empty=True):
    """Envvar operation helper

    This function generates a wrapper for envvar operations.

    Args:
        op (str): The operation to execute. Valid entries are:

          - ``set`` - Sets or resets an envvar to the specified value.
          - ``append`` - Append a value to an existing envvar
              or set if it doesn't exist.
          - ``prepend`` - Prepend a value to an existing envvar
              or set if it doesn't exist.
          - ``unset`` - Unset (delete) an envvar if it exists.
          - ``remove_substr`` - Removes a substring from an existing envvar.

        envvar_name (str): The *name* of the envvar to be modified.
        envvar_value (str): Optional envvar value for operations that
            need to set a value. Default: ""
        allow_empty (bool): If False, we throw a ``ValueError`` if
            assignment of an empty value is attempted. Default: True.


    """
    envvar_exists    = envvar_name in os.environ.keys()
    envvar_value_old = [os.environ[envvar_name]] if envvar_exists else []

    if envvar_value != "" and '$' in envvar_value:
        envvar_value = expand_envvars_in_string(envvar_value)

    if op == "set":
        envvar_assign(envvar_name, envvar_value, allow_empty)
    elif op == "append":
        tmp = envvar_value_old + [ envvar_value ]
        newval = os.pathsep.join(tmp)
        envvar_assign(envvar_name, newval, allow_empty)
    elif op == "prepend":
        tmp = [ envvar_value ] + envvar_value_old
        newval = os.pathsep.join(tmp)
        envvar_assign(envvar_name, newval, allow_empty)
    elif op == "unset":
        if envvar_exists:
            del os.environ[envvar_name]
    elif op == "remove_substr":
        if envvar_exists:
            newval = os.environ[envvar_name].replace(envvar_value,"")
            envvar_assign(envvar_name, newval, allow_empty)
    elif op == "remove_path_entry":
        if envvar_exists:
            entry_list_old = os.environ[envvar_name].split(os.pathsep)
            entry_list_new = [ x for x in entry_list_old if x != envvar_value ]
            newval = os.pathsep.join(entry_list_new)
            envvar_assign(envvar_name, newval, allow_empty)
    elif op == "find_in_path":
        try:
            envvar_value = envvar_find_in_path(envvar_value)
        except FileNotFoundError:
            envvar_value = ""
        envvar_assign(envvar_name, envvar_value, allow_empty)
    else:                                                                                           # pragma: no cover
        raise ValueError("Unknown command `{}`.".format(op))
    return 0


def expand_envvars_in_string(string_in) -> str:
    """
    Take an input string that may contain environment variables in the style
    of BASH shell environment vars (i.e., "${foobar}") and replace them with
    the actual environment variables.

    This looks like a bash variable expansion, it is not bash and
    we do not support expanding all forms of `bash` variables. For example,
    bash variables that look like ``$foo`` which don't have the enclosing ``{``
    and ``}`` braces can introduce unexpected results. For example:

    .. code-block:: bash
        :linenos:

        export var1=AAA
        export var2=B$var1B
        export var3=B${var1}B

    In this case, setting ``var2`` will likely fail because bash think you're
    appending the contents of ``$var1B`` to the end of ``B``, or if there is
    a ``$var1B`` that exists it would append that to ``B`` which might not be
    the desired result if you wanted output like what ``var3`` will get
    (``BAAAB``).

    Because of this, we only support the more *explicit* nature of requiring
    expansion to be performed within curly braces.

    Returns:
         A string that contains the contents of any `${ENVVAR}` entries expanded
         inline into the string.

    Raises:
         KeyError: Required environment variable does not exist.
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
    def __init__(self, filename=None):
        if filename is not None:
            self.inifilepath = filename


    # -----------------------
    #   P R O P E R T I E S
    # -----------------------


    @property
    def actions(self) -> dict:
        """
        A dictionary storing the set of actions by section name for any sections that
        have been parsed.

        An example of the structure of this object is the following:

        .. code-block:: python
            :linenos:

            { "SECTION_A":
                [
                    {'op': 'envvar_set',     'envvar': 'FOO', 'value': 'bar'},
                    {'op': 'envvar_append',  'envvar': 'FOO', 'value': 'baz'},
                    {'op': 'envvar_prepend', 'envvar': 'FOO', 'value': 'foo'}
                ]
            }

        Returns:
            dict: A *dict* containing an entry for every *section* that has been
            parsed by the parser during the life of this class instance. Each entry
            in the ``dict`` is a *list of actions*.
        """
        if not hasattr(self, "_var_actions_cache"):
            self._var_actions_cache = {}
        return self._var_actions_cache


    @actions.setter
    def actions(self, value) -> dict:
        if not isinstance(value, (dict)):
            self.exception_control_event("CATASTROPHIC", TypeError,
                                         "actions_cache must be a dict.")
        self._var_actions_cache = value
        return self._var_actions_cache


    # ------------------------------
    #   P U B L I C   M E T H O D S
    # ------------------------------


    def apply(self, section) -> int:
        """Apply the set of instructions stored in ``actions``.

        This method will cause the actions that are defined to be
        executed.

        Args:
            section (str): The desired *section* from the .ini file for this operation.

        Returns:
            integer: 0 if successful, nonzero if something went wrong that did not
                trigger an exception of some kind.

        Todo:
            - Replace this function with actions_cache use. Add parameters for section_name
        """
        if not isinstance(section, (str)):
            self.exception_control_event("CATASTROPHIC", TypeError,
                                         "`secton` must be a str type.")
        output = 0

        # kick off a parse of the section.
        self.configparserenhanceddata[section]

        for iaction in self.actions[section]:
            rval  = 0
            op    = iaction['op']
            value = iaction['value']

            if 'envvar' in iaction.keys():
                rval = self._apply_envvar(op, envvar_name=iaction['envvar'], envvar_value=value)

            if 'module' in iaction.keys():
                rval = self._apply_module(op, module_name=iaction['module'], module_value=value)

            output = max(output, rval)

        return output


    def pretty_print_actions(self, section):
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

        Args:
            section (str): The desired *section* from the .ini file for this operation.
        """
        # Trigger a parse of the section if we don't already have it.
        self.configparserenhanceddata[section]

        print("Actions")
        print("=======")
        for iaction in self.actions[section]:
            operation = iaction['op']

            print("--> {:<14} : ".format(operation), end="")
            if operation == "module_purge":
                print("")
            elif operation == "module_use":
                print("{}".format(iaction['value']))
            elif operation == "module_load":
                print("{}/{}".format(iaction['module'], iaction['value']))
            elif operation == "module_swap":
                print("{} {}".format(iaction['module'], iaction['value']))
            elif operation == "module_unload":
                print("{}".format(iaction['module']))
            elif operation == "envvar_set":
                print("{}=\"{}\"".format(iaction['envvar'], iaction['value']))
            elif operation == "envvar_prepend":
                arg = "${%s}"%(iaction['envvar'])
                print("{}=\"{}:{}\"".format(iaction['envvar'],iaction['value'],arg))
            elif operation == "envvar_append":
                arg = "${%s}"%(iaction['envvar'])
                print("{}=\"{}:{}\"".format(iaction['envvar'],arg,iaction['value']))
            elif operation == "envvar_unset":
                print("{}".format(iaction['envvar']))
            elif operation == "envvar_remove_substr":
                arg = "${%s}"%(iaction['envvar'])
                print("{}=\"{}:{}\"".format(iaction['envvar'],arg,iaction['value']))
            elif operation == "envvar_remove_path_entry":
                arg = "${%s}"%(iaction['envvar'])
                print("{}=\"{}:{}\"".format(iaction['envvar'],arg,iaction['value']))
            elif operation == "envvar_find_in_path":
                print("{}=\"{}\"".format(iaction['envvar'], iaction['value']))
            else:
                print("(unhandled) {}".format(iaction))

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


    def write_actions_to_file(self,
                              filename,
                              section,
                              include_header=True,
                              include_body=True,
                              include_shebang=True,
                              interpreter="bash") -> int:
        """Write the actions to an 'executable' file.

        Generates an executable script that will execute the actions
        that we generate in the same way ``apply()`` would.

        Args:
            filename (str,Path): The destination filename the
                actions should be written to.
            section (str): The desired *section* from the .ini file for this operation.
            include_header (bool): Include a `header` containing pre-defined
                functions used by the actions. Default: True
            include_body (bool): Include the `body` of the commands in the output
                file? (Set this to False and ``include_header=True`` to generate a
                *header-only* option.). Default: True
            include_shebang (bool): Include the shebang line (i.e., `#!/usr/bin/bash`)
                in the generated file. Python will use `python3`. Default: True
            interpreter (str): The kind of file to generate. We support
                generation of "bash" or "python" scripts. Default: 'bash'

        Raises:
            ValueError: If an unknown ``interpreter`` parameter is provided
                and ``exception_control_level`` is >= 2 (SERIOUS events raise
                exceptions instead of warn).

        Returns:
            int: 0 if successful

        Todo:
            In the future, generate options to write out the actions as
            "python".
        """
        allowable_interpreter_list = ["bash", "python"]
        if interpreter not in allowable_interpreter_list:
            errmsg  = "Invalid interpreter provided: {}\n".format(interpreter)
            errmsg += "Allowable values must be one of: {}.".format(", ".join(allowable_interpreter_list))
            self.exception_control_event("SERIOUS", ValueError, errmsg)
            return 1

        output_file_str = self.generate_actions_script(section,
                                                       incl_hdr=include_header,
                                                       incl_body=include_body,
                                                       incl_shebang=include_shebang,
                                                       interp=interpreter)
        with open(filename, "w") as ofp:
            ofp.write(output_file_str)

        return 0


    def generate_actions_script(self, section, incl_hdr=True, incl_body=True, incl_shebang=True, interp='bash') -> str:
        """Generate a script that will implement the computed list of actions.

        Generates a script in the language of the specified interpreter (currently
        just ``python`` and ``bash`` are allowed) that will execute the set of actions
        that have been specified by the most recent section scanned by the ``.ini`` file.

        Args:
            section (str): The desired *section* from the .ini file for this operation.
            incl_hdr (bool): Include standard header with functions
                definitions for functions used if True.
            incl_body (bool): Include the `body` of the commands in the output
                file? (Set this to False and ``include_header=True`` to generate a
                *header-only* option.). Default: True
            incl_shebang (bool): Include the shebang line (i.e., `#!/usr/bin/bash`)
                in the generated file. Python will use `python3`. Default: True
            interp (str): Specifies the generator for the script or script fragments.
                Allowable values are "bash" or "python". Default = "bash".

        Raises:
            ValueError: if an ``action`` does not have a ``envvar`` or
                a ``module`` key.

        Returns:
            str: containing the bash script that can be written.
        """
        if not isinstance(section, (str)):
            self.exception_control_event("CATASTROPHIC", TypeError,
                                         "Section names must be a str type.")

        allowable_interpreter_list = ["bash", "python"]
        if interp not in allowable_interpreter_list:
            errmsg  = "Invalid interpreter provided: {}\n".format(interp)
            errmsg += "Allowable values must be one of: {}.".format(", ".join(allowable_interpreter_list))
            self.exception_control_event("SERIOUS", ValueError, errmsg)
            return ""

        output_file_str = ""
        output_comment_str = self._output_comment_col0_str(interp=interp)

        if incl_hdr:
            if incl_shebang:
                output_file_str += self._gen_shebang_line(interp)
            if interp == "bash":
                output_file_str += self._gen_script_header_bash()
            elif interp == "python":
                output_file_str += self._gen_script_header_python()
            else:                                                                                   # pragma: no cover (unreachable)
                self.exception_control_event("CRITICAL", RuntimeError,
                    "'Unreachable' branch executed, something is broken!")
            output_file_str += "\n\n"

        if incl_body:
            if incl_shebang and not incl_hdr:
                output_file_str += self._gen_shebang_line(interp)

            output_file_str += "{} -------------------------------------------------\n".format(output_comment_str)
            output_file_str += "{}   S E T E N V I R O N M E N T   C O M M A N D S\n".format(output_comment_str)
            output_file_str += "{} -------------------------------------------------\n".format(output_comment_str)

            # kick off a parse of the section.
            if section not in self.actions.keys():
                self.parse_section(section)

            # Loop over the actions in the section
            for iaction in self.actions[section]:

                action_val = iaction['value']
                action_op  = iaction['op']

                if "envvar" in iaction.keys():
                    action_name = iaction['envvar']
                    output_file_str += self._gen_actioncmd_envvar(action_op,
                                                                  action_name,
                                                                  action_val,
                                                                  interp=interp)

                elif "module" in iaction.keys():
                    action_name = iaction['module']
                    output_file_str += self._gen_actioncmd_module(action_op,
                                                                  action_name,
                                                                  action_val,
                                                                  interp=interp)
                else:
                    raise ValueError("Unknown action class.")

                output_file_str += "\n"

            output_file_str += "\n\n"

        return output_file_str


    # --------------------
    #   H A N D L E R S
    # --------------------


    def _handler_envvar_remove_substr(self, section_name, handler_parameters) -> int:
        """Handler: for ``envvar-remove-substr``

        Handles operations that wish to remove *all* occurrences of a substring
        from a given envvar.

        .. code-block:: bash
            :linenos:

            [ENVVAR_REMOVE_SUBSTR_TEST]
            # Create an environment var FOO="BAAAB"
            envvar-set FOO           : BAAAB

            # Removes all "A" substrings from FOO
            envvar-remove-substr FOO : A

            # Result should be: FOO="BB"

        Args:
            section_name (str): The name of the section being processed.
            handler_parameters (HandlerParameters): The parameters passed to
                the handler.

        Returns:
            int:
            * 0     : SUCCESS
            * [1-10]: Reserved for future use (WARNING)
            * > 10  : An unknown failure occurred (CRITICAL)
        """
        return self._helper_handler_common_envvar(section_name, handler_parameters)


    def _handler_envvar_remove_path_entry(self, section_name, handler_parameters) -> int:
        """Handler: for ``envvar-remove-path-entry``

        Handles operations that remove all occurrences of a specific
        path from an envvar.

        .. code-block:: bash
            :linenos:

            [ENVVAR_REMOVE_PATH_ENTRY_TEST]
            # Create an TEST_PATH = "/foo:/bar:/bar/baz:/bar:/bif"
            envvar-set TEST_PATH : /foo:/bar:/bar/baz:/bar:/bif

            # Removes "/bar" from the path
            envvar-remove-path-entry TEST_PATH : /bar

            # Result should be: TEST_PATH = "/foo:/bar/baz:/bif"

        Args:
            section_name (str): The name of the section being processed.
            handler_parameters (HandlerParameters): The parameters passed to
                the handler.

        Returns:
            int:
            * 0     : SUCCESS
            * [1-10]: Reserved for future use (WARNING)
            * > 10  : An unknown failure occurred (CRITICAL)
        """
        return self._helper_handler_common_envvar(section_name, handler_parameters)


    def _handler_envvar_find_in_path(self, section_name, handler_parameters) -> int:
        """Handler: for ``envvar-find-in-path``

        This handler is used when the ``envvar-find-in-path`` command is issued which
        instructs SetEnvironment to generate code to *find* a given executable in the
        path.

        In this example, we give the command ``envvar-find-in-path`` to search for the
        ``ls`` executable. We're being a little sneaky by setting this into ``TEST_ENVVAR_EXE``
        first to demonstrate that we can use the ``${ENVVAR}`` expansion here as well.

        .. code-block:: bash
            :linenos:

            [ENVVAR_FIND_IN_PATH_TEST]
            envvar-set          TEST_ENVVAR_EXE  : ls
            envvar-find-in-path TEST_ENVVAR_PATH : ${TEST_ENVVAR_EXE}

        Args:
            section_name (str): The name of the section being processed.
            handler_parameters (HandlerParameters): The parameters passed to
                the handler.

        Returns:
            int:
            * 0     : SUCCESS
            * [1-10]: Reserved for future use (WARNING)
            * > 10  : An unknown failure occurred (CRITICAL)
        """
        return self._helper_handler_common_envvar(section_name, handler_parameters)


    def handler_envvar_set(self, section_name, handler_parameters) -> int:
        """Handler: for envvar-set operations.

        Handles operations that wish to *set* an environment variable.

        Returns:
            integer: An integer value indicating if the handler was successful.
                - 0     : SUCCESS
                - [1-10]: Reserved for future use (WARNING)
                - > 10  : An unknown failure occurred (SERIOUS)

        """
        return self._helper_handler_common_envvar(section_name, handler_parameters)


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
        return self._helper_handler_common_envvar(section_name, handler_parameters)


    def handler_envvar_prepend(self, section_name, handler_parameters) -> int:
        """Handler: for envvar-prepend operations.

        Handles operations that wish to *prepend* an environment variable.

        Returns:
            integer: An integer value indicating if the handler was successful.
                - 0     : SUCCESS
                - [1-10]: Reserved for future use (WARNING)
                - > 10  : An unknown failure occurred (SERIOUS)

        """
        return self._helper_handler_common_envvar(section_name, handler_parameters)


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
        return self._helper_handler_common_envvar(section_name, handler_parameters)


    def handler_module_load(self, section_name, handler_parameters) -> int:
        """Handler: for module-load operations.

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
        return self._helper_handler_common_module(section_name, handler_parameters)


    def handler_module_purge(self, section_name, handler_parameters) -> int:
        """Handler: for module-purge operations

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
        return self._helper_handler_common_module(section_name, handler_parameters)


    def handler_module_remove(self, section_name, handler_parameters) -> int:
        """Handler: for module-remove operations.

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
        """Handler: for module-swap operations.

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
        return self._helper_handler_common_module(section_name, handler_parameters)


    def handler_module_unload(self, section_name, handler_parameters) -> int:
        """Handler: for module-unload operations.

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
        return self._helper_handler_common_module(section_name, handler_parameters)


    def handler_module_use(self, section_name, handler_parameters) -> int:
        """Handler: for module-use operations.

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
        return self._helper_handler_common_module(section_name, handler_parameters)


    def handler_initialize(self, section_name, handler_parameters) -> int:
        """Initialize a recursive parse search.

        Args:
            section_name (str): The section name string.
            handler_parameters (object): A HandlerParameters object containing
                the state data we need for this handler.

        Returns:
            integer value
                - 0     : SUCCESS
                - [1-10]: Reserved for future use (WARNING)
                - > 10  : An unknown failure occurred (SERIOUS)
        """
        self.enter_handler(handler_parameters)

        self._initialize_handler_parameters(section_name, handler_parameters)

        self.exit_handler(handler_parameters)
        return 0


    def handler_finalize(self, section_name, handler_parameters) -> int:
        """Finalize a recursive parse search.

        Returns:
            integer value
                - 0     : SUCCESS
                - [1-10]: Reserved for future use (WARNING)
                - > 10  : An unknown failure occurred (SERIOUS)
        """
        self.enter_handler(handler_parameters)

        # save the results into the right `actions_cache` entry
        self.actions[section_name] = handler_parameters.data_shared["setenvironment"]

        self.exit_handler(handler_parameters)
        return 0


    # ---------------
    #  H E L P E R S
    # ---------------

    def _initialize_handler_parameters(self, section_name, handler_parameters):
        """Initialize ``handler_parameters``

        Initializes any default settings needed for ``handler_parameters``.
        Takes the same parameters as handlers.

        Args:
            section_name (str): The section name string.
            handler_parameters (object): A HandlerParameters object containing
                the state data we need for this handler.
        """
        data_shared_ref = handler_parameters.data_shared
        if 'setenvironment' not in data_shared_ref.keys():
            data_shared_ref['setenvironment'] = []

        return


    def _helper_handler_common_envvar(self, section_name, handler_parameters) -> int:
        """Common handler for envvar actions

        All the *envvar* actions do basically the same thing so we can move the
        general handling of them into a more generic handler method.

        This helper appends entries to ``handler_parameters.data_shared``
        data structure's "setenvironment" entry. Results look something like:

            >>> handler_parameters.data_shared['setenvironment']
            [
                {'op': 'envvar_set',     'envvar': 'FOO', 'value': 'bar' },
                {'op': 'envvar_append',  'envvar': 'FOO', 'value': 'baz' },
                {'op': 'envvar_prepend', 'envvar': 'FOO', 'value': 'foo' },
                {'op': 'envvar_set',     'envvar': 'BAR', 'value': 'foo' },
                {'op': 'envvar_set',     'envvar': 'BAZ', 'value': 'bar' },
                {'op': 'envvar_unset',   'envvar': 'FOO', 'value': 'None'},
                {'op': 'envvar_remove',  'envvar': 'BAZ', 'value': 'None'},
                {'op': 'envvar_remove_substr',    'envvar': 'MYENVVAR', 'value': 'B'   },
                {'op': 'envvar_remove_path_entry','envvar': 'MYPATH',   'value': '/foo'}
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

        self._initialize_handler_parameters(section_name, handler_parameters)

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


    def _helper_handler_common_module(self, section_name, handler_parameters) -> int:
        """Common handler for module actions

        All the *module* actions care about the same sets of parameters so we
        can use this to add the appropriate entry to the actions list when
        processing the .ini file.

        This helper appends entries to ``handler_parameters.data_shared``
        data structure's "setenvironment" entry. Results look something like:

            >>> handler_parameters.data_shared['setenvironment']
            [
                {'op': 'module_purge',  'module': None,          'value': ''},
                {'op': 'module_use',    'module': None,          'value': '/foo/bar/baz'},
                {'op': 'module_load',   'module': 'dummy-gcc',    'value': '4.8.4'},
                {'op': 'module_load',   'module': 'dummy-boost',  'value': '1.10.1'},
                {'op': 'module_load',   'module': 'dummy-python', 'value': '3.9.0'},
                {'op': 'module_load',   'module': 'dummy-gcc',    'value': '4.8.4'},
                {'op': 'module_unload', 'module': 'dummy-boost',  'value': ''},
                {'op': 'module_remove', 'module': 'dummy-python', 'value': ''},
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

        self._initialize_handler_parameters(section_name, handler_parameters)

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


    def _apply_envvar(self, operation, envvar_name, envvar_value) -> int:
        """Apply an ENVVAR operation

        Currently supported ENVVAR operations are:
        - ``envvar_append``
        - ``envvar_prepend``
        - ``envvar_set``
        - ``envvar_unset``
        - ``envvar_remove_substr``
        - ``envvar_remove_path_entry``

        Note:
            ``envvar_remove`` is handled in the ``handler_envvar_remove``
            directly because its context is most applicable at processing
            time.

        Args:
            operation (str): The *operation* to apply (i.e., ``set``, ``unset`` etc.)
            envvar_name (str): The name of the environment variable we're working on.
            envvar_value (str, None): The value to be assigned to the envvar.
                This is not used by ``unset``.

        Returns:
            int: 0 if successful

        Raises:
            TypeError: if any of the parameters fail a typecheck on method entry.
            ValueError: if the operation provided is invalid.
        """
        if not isinstance(operation, (str)):
            raise TypeError("operation must be a string.")
        if not isinstance(envvar_name, (str)):
            raise TypeError("envvar_name must be a string.")
        if not isinstance(envvar_value, (str, type(None))):
            raise TypeError("envvar_value must be either `string` or `None` types.")

        self.debug_message(2, "{} :: {} - {}".format(operation, envvar_name, envvar_value))         # Console

        command = self._gen_actioncmd_envvar(operation, envvar_name, envvar_value)
        output  = self._exec_helper(command)

        if output != 0:
            output  = 1
            message = "ENVVAR operation {} failed with {} rval.".format(operation, output)
            self.exception_control_event("CRITICAL", RuntimeError, message)

        return output


    def _apply_module(self, operation, module_name, module_value) -> int:
        """Apply MODULE operations

        Currently supported MODULE operations are:

        - ``module_load``
        - ``module_purge``
        - ``module_swap``
        - ``module_unload``
        - ``module_use``
        - ``module_remove_substr``

        Note:
            ``module_remove`` is handled in the handler itself since it's
            context is most applicable at the time of parsing.

        Args:
            operation (str): The operation to be executed (i.e., ``module_load``)
            module_name (str, None): The name of the module.
            module_value (str,None): The value from the operation field.

        Returns:
            integer: 0 if successful.

        Raises:
            TypeError: if any of the parameters fail a typecheck on method entry.
            ValueError: if the operation provided is invalid.
        """
        if not isinstance(operation, (str)):
            raise TypeError("operation must be a string.")
        if not isinstance(module_name, (str, type(None))):
            raise TypeError("module_name must be either `string` or `None` types.")
        if not isinstance(module_value, (str, type(None))):
            raise TypeError("module_value must be either `string` or `None` types.")

        self.debug_message(2, "{} :: {} - {}".format(operation, module_name, module_value))         # Console

        command = self._gen_actioncmd_module(operation, module_name, module_value)
        output  = self._exec_helper(command)

        if output != 0:
            message = "MODULE operation `{}` failed with rval == `{}`.".format(operation, output)
            self.exception_control_event("CRITICAL", RuntimeError, message)

        return output


    def _gen_script_header_bash(self) -> str:
        """Generate "common" Bash functions

        Generates a 'common' set of functions and helpers for Bash scripts.
        This is used if we wish to generate a script in Bash that would
        perform the same actions as the ``apply()`` method used in ``SetEnvironment``.

        Returns:
            str: A string containing the helper functions required if we generate
            a Python output script.
        """
        output = dedent("""\
        # ---------------------------------------------------
        #   S E T E N V I R O N M E N T   F U N C T I O N S
        # ---------------------------------------------------


        # envvar_append_or_create
        #  $1 = envvar name
        #  $2 = string to append
        function envvar_append_or_create() {
            if [[ ! -n "${!1+1}" ]]; then
                export ${1}="${2}"
            else
                export ${1}="${!1}:${2}"
            fi
        }

        # envvar_prepend_or_create
        #  $1 = envvar name
        #  $2 = string to prepend
        function envvar_prepend_or_create() {
            if [[ ! -n "${!1+1}" ]]; then
                export ${1}="${2}"
            else
                export ${1}="${2}:${!1}"
            fi
        }

        # envvar_set_or_create
        #  $1 = envvar name
        #  $2 = string to prepend
        function envvar_set_or_create() {
            export ${1:?}="${2:?}"
        }

        # envvar_remove_substr
        # $1 = envvar name
        # $2 = substring to remove
        function envvar_remove_substr() {
            local envvar=${1:?}
            local substr=${2:?}
            #echo "envvar   : ${envvar}" > /dev/stdout
            #echo "to_remove: ${substr}" > /dev/stdout
            if [[ "${substr}" == *"#"* ]]; then
                printf "%s\\n" "ERROR: $FUNCNAME: \"$substr\" contains a '#' which is invalid." 2>&1
                return
            fi
            if [ ! -z ${1:?} ]; then
                export ${envvar}=$(echo ${!envvar} | sed s#${substr}##g)
            fi
        }

        # envvar_remove_path_entry
        # $1 = A path style envvar name
        # $2 = Entry to remove from the path.
        function envvar_remove_path_entry() {
            local envvar=${1:?}
            local to_remove=${2:?}
            local new_value=${!envvar}
            #echo -e "envvar = ${envvar}" > /dev/stdout
            #echo -e "to_remove = ${to_remove}" > /dev/stdout
            #echo -e "new_value = ${new_value}" > /dev/stdout
            if [ ! -z ${envvar} ]; then
                new_value=:${new_value}:
                new_value=${new_value//:${to_remove}:/:}
                new_value=${new_value#:1}
                new_value=${new_value%:1}
                export ${envvar}=${new_value}
            fi
        }

        # envvar_op
        # $1 = operation    (set, append, prepend, unset)
        # $2 = arg1         (envvar name)
        # $3 = arg2         (envvar value - optional)
        function envvar_op() {
            local op=${1:?}
            local arg1=${2:?}
            local arg2=${3}
            if [[ "${op:?}" == "set" ]]; then
                envvar_set_or_create ${arg1:?} ${arg2:?}
            elif [[ "${op:?}" == "unset" ]]; then
                unset ${arg1:?}
            elif [[ "${op:?}" == "append" ]]; then
                envvar_append_or_create ${arg1:?} ${arg2:?}
            elif [[ "${op:?}" == "prepend" ]]; then
                envvar_prepend_or_create ${arg1:?} ${arg2:?}
            elif [[ "${op:?}" == "remove_substr" ]]; then
                envvar_remove_substr ${arg1:?} ${arg2:?}
            elif [[ "${op:?}" == "find_in_path" ]]; then
                envvar_set_or_create ${arg1:?} $(which ${arg2:?})
            else
                echo -e "!! ERROR (BASH): Unknown operation: ${op:?}"
            fi
        }
        """)
        return output


    def _gen_script_header_python(self) -> str:
        """Generate "common" Python functions

        Generates a common set of functions and helpers for Python
        scripts. This is used if we wish to generate a script in Python
        that performs the equivalent actions of ``apply()``. The generated
        python output of this should be inserted to the ``.py`` file that
        is generated.

        Returns:
            str: A string containing the helper functions required if we
                generate a Python output script.
        """

        output = dedent("""\

        # ---------------------------------------------------
        #   S E T E N V I R O N M E N T   F U N C T I O N S
        # ---------------------------------------------------
        import os
        import re
        import sys

        if not sys.version_info.major >= 3:
            raise Exception("Minimum Python required is 3.x")

        from setenvironment import ModuleHelper


        """)

        # Note: We use `inspect` here to pull in the same code that's
        #       used in SetEnvironment itself to reduce technical debt.

        output += inspect.getsource(envvar_find_in_path)
        output += "\n\n"
        output += inspect.getsource(envvar_assign)
        output += "\n\n"
        output += inspect.getsource(expand_envvars_in_string)
        output += "\n\n"
        output += inspect.getsource(envvar_op)

        return output


    def _gen_shebang_line(self, interp="bash") -> str:
        """
        """
        output = "#!/usr/bin/env "
        if interp == "bash":
            output += "bash"
        elif interp == "python":
            output += "python3"
        else:                                                                                       # pragma: no cover (unreachable)
            self.exception_control_event("CRITICAL", RuntimeError,
                "'Unreachable' branch executed, something is broken!")
        output += "\n"
        return output


    def _output_comment_col0_str(self, interp="bash") -> str:
        output="#"
        if interp in ["bash", "python"]:
            output="#"
        else:                                                                                       # pragma: no cover (unreachable)
            self.exception_control_event("CRITICAL", RuntimeError,
                "'Unreachable' branch executed, something is broken!")
        return output


    def _gen_actioncmd_module(self, op, *args, interp='python') -> str:
        """
        Generates an executable module command based on the selected interpreter.

        Operations defined for this are:

        +-------------+----------+---------------------------------------------------+
        | Operation   | Req Args | Description & required positional args            |
        +=============+==========+===================================================+
        | ``load``    |        2 | Load the specified module.                        |
        +-------------+----------+                                                   +
        |             |          |  - arg1: *module name* (``gcc``)                  |
        |             |          |  - arg2: *module version* (``7.3.0``)             |
        +-------------+----------+---------------------------------------------------+
        | ``purge``   |        0 | Purge all loaded modules and search paths.        |
        +-------------+----------+---------------------------------------------------+
        | ``swap``    |        2 | Swap a loaded module for another module.          |
        +-------------+----------+                                                   +
        |             |          | - arg1: *module name* (``gcc``)                   |
        |             |          | - arg2: *module name* + *version* (``gcc/9.2.0``) |
        +-------------+----------+---------------------------------------------------+
        | ``unload``  |        1 | Unload the specified module.                      |
        +-------------+----------+                                                   +
        |             |          | - arg1: *module name* (i.e., ``gcc``)             |
        +-------------+----------+---------------------------------------------------+
        | ``use``     |        1 | Add a path to be included in modules search path. |
        +-------------+----------+                                                   +
        |             |          | - arg1: *path to modules*                         |
        +-------------+----------+---------------------------------------------------+

        This method is invoked like this
        ``_gen_actioncmd_module(op, arg1, arg2, ... , argN, interp='python')``
        where there is a variable number of positional arguments after ``op``
        based on which operation is specified.

        Allowable interpreters for the ``interp`` parameter are "bash" or "python".

        - For ``python`` uses we use the ``module()`` function defined in ``ModuleHelper``.
        - For ``bash`` use cases we generate commands using the ``module`` application.

        Args:
            op (string): The module operation to perform.
            *args: Provide the (str) arguments needed for the given operation.
                See the table provided above.
            interp (str): Interpreter to generate code for. ``bash`` or ``python``
                are currently allowed.
        """
        output = ""
        op = self._remove_prefix(op, "module_")

        # Validate parameters
        num_args_req = 0
        if   op in ['purge']:          num_args_req = 0
        elif op in ['use',  'unload']: num_args_req = 1
        elif op in ['load', 'swap']:   num_args_req = 2

        if len(args) < num_args_req:
            errmsg = "Incorrect # of arguments provided for `module-{}`".format(op)
            self.exception_control_event("CRITICAL", IndexError, errmsg)

        arglist = [ op ]
        if op == "purge":
            pass
        elif op == "use":
            # Todo: Do we check these here? I'm torn on this because if we just wanted to
            #       parse the ini file and generate a bash script that might be relocated
            #       and run from a different CWD then checking here doesn't make sense.
            #       Maybe a WARNING?
            #       Depending on the Modules command available, we may get an error if
            #       the `module use` fails and give us a RuntimeError. I'll leave out for now
            #       and we can include it later once we have a chance to discuss in a code
            #       review.
            #if not os.path.exists(arg2):
            #    self.exception_control_event("SERIOUS", FileNotFoundError,
            #                                 "`module use` PATH not found: `{}`".format(arg2))
            #if  not os.path.isdir(arg2):
            #    self.exception_control_event("SERIOUS", FileNotFoundError,
            #                                 "`module use` PATH is not a dir: `{}`".format(arg2))
            arglist += [ args[1] ]
        elif op == "load":
            arglist += [ args[0] + "/" + args[1] ]
        elif op == "unload":
            arglist += [ args[0] ]
        elif op == "swap":
            arglist += [ args[0], args[1] ]
        else:
            self.exception_control_event("SERIOUS", ValueError,
                                         "Invalid module operation provided: {}".format(op))

        if interp=="python":
            arglist = [ '"' + x + '"' for x in arglist ]
            output = "ModuleHelper.module({})".format(",".join(arglist))
        elif interp=="bash":
            output = "module {}".format(" ".join(arglist))
        else:
            self.exception_control_event("SERIOUS", ValueError,
                                         "Invalid interpreter provided: {}".format(interp))

        return output


    def _gen_actioncmd_envvar(self, op, *args, interp='python'):
        """
        Generates an executable environment variable command based on
        the selected interpreter.

        Operations defined for this are:

        +-----------------------+----------+---------------------------------------------------+
        | Operation             | Req Args | Description & required positional args            |
        +=======================+==========+===================================================+
        | ``append``            |        2 | Append a value ot an existing environment var.    |
        +-----------------------+----------+                                                   +
        |                       |          | - arg1: *envvar name*                             |
        |                       |          | - arg2: *envvar value*                            |
        +-----------------------+----------+---------------------------------------------------+
        | ``prepend``           |        2 | Prepend a value to an existing environment var.   |
        +-----------------------+----------+                                                   +
        |                       |          | - arg1: *envvar name*                             |
        |                       |          | - arg2: *envvar value*                            |
        +-----------------------+----------+---------------------------------------------------+
        | ``set``               |        2 | Set an environment variable to a value.           |
        +-----------------------+----------+                                                   +
        |                       |          | - arg1: *envvar name*                             |
        |                       |          | - arg2: *envvar value*                            |
        +-----------------------+----------+---------------------------------------------------+
        | ``unset``             |        1 | Unset the environment variable if it exists.      |
        +-----------------------+----------+                                                   +
        |                       |          | - arg1: *module name* (i.e., ``gcc``)             |
        +-----------------------+----------+---------------------------------------------------+
        | ``remove_substr``     |        2 | Remove a substring from an envvar if it exists.   |
        +-----------------------+----------+                                                   +
        |                       |          | - arg1: *envvar name*                             |
        |                       |          | - arg2: *substrin to remove*                      |
        +-----------------------+----------+---------------------------------------------------+
        | ``remove_path_entry`` |        2 | Remove a substring from an envvar if it exists.   |
        +-----------------------+----------+                                                   +
        |                       |          | - arg1: *envvar name*                             |
        |                       |          | - arg2: *substrin to remove*                      |
        +-----------------------+----------+---------------------------------------------------+

        This method is invoked like this
        ``_gen_actioncmd_module(op, arg1, arg2, ... , argN, interp='python')``
        where there is a variable number of positional arguments after ``op``
        based on which operation is specified.
        This method generates an executable line of code in the language specified
        by the ``interp`` parameter. Currently, ``bash`` and ``python`` are allowed.

        +-------------+--------------------------------------------------------------+
        | ``interp``  | Common Functions Generator(s)                                |
        +=============+==============================================================+
        | ``python``  | ``_gen_script_common_python``, defines:                      |
        +-------------+                                                              +
        |             | - ``envvar_op()``                                            |
        |             | - ``expand_envvars_in_string()``                             |
        +-------------+--------------------------------------------------------------+
        | ``bash```   | ``_gen_script_common_bash``, defines:                        |
        +-------------+                                                              +
        |             | - ``envvar_op``                                              |
        |             | - ``envvar_append_or_create``                                |
        |             | - ``envvar_prepend_or_create``                               |
        |             | - ``envvar_set_or_create``                                   |
        |             | - ``envvar_remove_substr``                                   |
        +-------------+--------------------------------------------------------------+

        Args:
            - ``op`` (str): The operation to be executed.
                See the table above for more details.
            *args: Provide the (str) arguments needed for the given operation.
                See the table above for more details.
            interp (str): Interpreter to generate code for. ``bash`` or ``python``
                are currently allowed.

        Raises:
            IndexError: If the number of arguments provided is incompatible with
                the command.
            ValueError: If the operation provided is not in the list of available
                operations.
            ValueError: If the interpreter is not in the list of available interpreters.

        """
        output = ""
        op = self._remove_prefix(op, "envvar_")

        # Validate parameters
        num_args_req = 0
        if   op in ['unset']: num_args_req = 1
        else:                 num_args_req = 2

        if len(args) < num_args_req:
            errmsg = "Incorrect # of arguments provided for `envvar-{}`".format(op)
            self.exception_control_event("CRITICAL", IndexError, errmsg)

        arglist = [ op ]
        if op == "set":
            arglist += [ args[0], args[1] ]
        elif op == "append":
            arglist += [ args[0], args[1] ]
        elif op == "prepend":
            arglist += [ args[0], args[1] ]
        elif op == "unset":
            arglist += [ args[0] ]
        elif op == "remove_substr":
            arglist += [ args[0], args[1] ]
        elif op == "remove_path_entry":
            arglist += [ args[0], args[1] ]
        elif op == "find_in_path":
            arglist += [ args[0], args[1] ]
        else:
            self.exception_control_event("SERIOUS", ValueError,
                                         "Invalid module operation provided: {}".format(op))

        if interp=="python":
            arglist = [ '"' + x + '"' for x in arglist ]
            output = "envvar_op({})".format(",".join(arglist))
        elif interp=="bash":
            output = "envvar_op {}".format(" ".join(arglist))
        else:
            self.exception_control_event("SERIOUS", ValueError,
                                         "Invalid interpreter provided: {}".format(interp))

        return output


    def _remove_prefix(self, text, prefix) -> str:
        """Remove a prefix string from another string

        Removes a prefix string from some text. This is a better approach
        than ``my_string.strip("somestr")`` because Python doesn't treat the
        parameter to ``strip()`` as a proper substring.

        Args:
            text (str): The text string.
            prefix (str): The prefix to strip off.

        Returns:
            str: A string object with the prefix removed if it existed.

        Note:
            Python 3.9 introduced ``removeprefix()`` and ``removesuffix()``
            but until we can set 3.9.x as a minimum version we need to use
            this workaround.

        Raises:
            TypeError: if ``text`` or ``prefix`` are not both strings.
        """
        if not isinstance(text, (str)):
            raise TypeError("`text` must be a string type.")
        if not isinstance(prefix, (str)):
            raise TypeError("`prefix` must be a string type.")
        prefix = str(prefix)
        if text.startswith(prefix):
            return text[len(prefix):]
        return text


    def _exec_helper(self, command):
        """Wrapper for ``exec()`` that properly captures the return value.

        There are quirks with ``exec()`` and how hit handles return values
        so this wrapper does it the 'right' way.

        One can't fully rely on it to modify an existing local variable.
        I think if the local var doesn't exist it will create one but if
        it does exist then it won't overwrite it.

        See Also:
            - https://docs.python.org/3/library/functions.html#exec
        """
        ldict = {}
        exec( "_rval = "+ command, globals(), ldict)
        return ldict['_rval']



# EOF



