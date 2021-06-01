#!/usr/bin/env python3

# ---------------------------------------------------
#   S E T E N V I R O N M E N T   F U N C T I O N S
# ---------------------------------------------------
import os
import re
import sys

if not sys.version_info.major >= 3:
    raise Exception("Minimum Python required is 3.x")

from setenvironment import ModuleHelper


def envvar_set(envvar_name: str, envvar_value: str, allow_empty: bool=True) -> int:
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
    if not isinstance(envvar_name, (str)):     raise TypeError("`envvar_name` must be a string.")
    if not isinstance(envvar_value, (str)):    raise TypeError("`envvar_value` must be a string.")
    if not isinstance(allow_empty, (bool)):    raise TypeError("`allow_empty` must be a boolean.")
    if not allow_empty and envvar_value == "": raise ValueError("`envvar_value` must not be empty.")

    os.environ[envvar_name] = envvar_value
    return 0


def envvar_set_if_empty(envvar_name: str, envvar_value: str, allow_empty: bool=True) -> int:
    """Set an environment variable if it is empty or not set.

    Assigns an environment variable (envvar) to a value if
    the envvar either does not exist or is empty.

    Args:
        envvar_name (str): The name of the envvar.
        envvar_value (str): The value to set to the envvar.
        allow_empty (bool): If False, we throw a ``ValueError`` if
            ``envvar_value`` is empty. Default: True.

    Returns:
        int: Returns a zero.

    Raises:
        TypeError: if:

            - ``envvar_value`` is not a string.
            - ``envvar_value`` is not a string.
            - ``allow_empty`` is not a bool.

        ValueError if:

            - ``allow_empty`` is True *and* ``envvar_value`` is an empty string.
    """
    if not isinstance(envvar_name, (str)):     raise TypeError("`envvar_name` must be a string.")
    if not isinstance(envvar_value, (str)):    raise TypeError("`envvar_value` must be a string.")
    if not isinstance(allow_empty, (bool)):    raise TypeError("`allow_empty` must be a boolean.")
    if not allow_empty and envvar_value == "": raise ValueError("`envvar_value` must not be empty.")

    if envvar_name not in os.environ.keys() or os.environ[envvar_name]=="":
        os.environ[envvar_name] = envvar_value
    return 0


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


def envvar_op(op, envvar_name: str, envvar_value: str="", allow_empty: bool=True) -> int:
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
    if not isinstance(envvar_name, (str)):     raise TypeError("`envvar_name` must be a string.")
    if not isinstance(envvar_value, (str)):    raise TypeError("`envvar_value` must be a string.")
    if not isinstance(allow_empty, (bool)):    raise TypeError("`allow_empty` must be a boolean.")
    if not allow_empty and envvar_value == "": raise ValueError("`envvar_value` must not be empty.")

    envvar_exists    = envvar_name in os.environ.keys()
    envvar_value_old = [os.environ[envvar_name]] if envvar_exists else []

    if envvar_value != "" and '$' in envvar_value:
        envvar_value = os.path.expandvars(envvar_value)

    if op == "set":
        envvar_set(envvar_name, envvar_value, allow_empty)
    elif op == "set_if_empty":
        envvar_set_if_empty(envvar_name, envvar_value, allow_empty)
    elif op == "append":
        tmp = envvar_value_old + [ envvar_value ]
        newval = os.pathsep.join(tmp)
        envvar_set(envvar_name, newval, allow_empty)
    elif op == "prepend":
        tmp = [ envvar_value ] + envvar_value_old
        newval = os.pathsep.join(tmp)
        envvar_set(envvar_name, newval, allow_empty)
    elif op == "unset":
        if envvar_exists:
            del os.environ[envvar_name]
    elif op == "remove_substr":
        if envvar_exists:
            newval = os.environ[envvar_name].replace(envvar_value,"")
            envvar_set(envvar_name, newval, allow_empty)
    elif op == "remove_path_entry":
        if envvar_exists:
            entry_list_old = os.environ[envvar_name].split(os.pathsep)
            entry_list_new = [ x for x in entry_list_old if x != envvar_value ]
            newval = os.pathsep.join(entry_list_new)
            envvar_set(envvar_name, newval, allow_empty)
    elif op == "find_in_path":
        envvar_value = envvar_find_in_path(envvar_value)
        envvar_set(envvar_name, envvar_value, allow_empty)
    elif op == "assert_not_empty":
        if not envvar_exists or os.environ[envvar_name] == "":
            message = "ERROR: Required envvar `{}` is not set.".format(envvar_name)
            if envvar_value != "":
                message = envvar_value
            raise ValueError(message)
    else:
        raise ValueError("Unknown command `{}`.".format(op))
    return 0


# -------------------------------------------------
#   S E T E N V I R O N M E N T   C O M M A N D S
# -------------------------------------------------
envvar_op("set","FOO","bar")
envvar_op("append","FOO","baz")
envvar_op("prepend","FOO","foo")
envvar_op("set","BAR","foo")
envvar_op("remove_substr","FOO","bar")
envvar_op("unset","FOO")
ModuleHelper.module("purge")
ModuleHelper.module("use","setenvironment/unittests/modulefiles")
ModuleHelper.module("load","gcc/4.8.4")
ModuleHelper.module("load","boost/1.10.1")
ModuleHelper.module("load","gcc/4.8.4")
ModuleHelper.module("unload","boost")
ModuleHelper.module("swap","gcc","gcc/7.3.0")


