
# ---------------------------------------------------
#   S E T E N V I R O N M E N T   F U N C T I O N S
# ---------------------------------------------------
import os
import re
import sys

if not sys.version_info.major >= 3:
    raise Exception("Minimum Python required is 3.x")

from setenvironment import ModuleHelper


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


