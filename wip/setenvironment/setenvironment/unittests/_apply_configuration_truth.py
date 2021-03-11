#!/usr/bin/env python3
import os
import re
import sys

if not sys.version_info.major >= 3:
    raise Exception("Minimum Python required is 3.x")

from setenvironment import ModuleHelper


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


def envvar_op(op, envvar_name, envvar_value=""):
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

        envvar_name (str): The *name* of the envvar to be modified.
        envvar_value (str): Optional envvar value for operations that
            need to set a value. Default: ""
    """
    envvar_exists    = envvar_name in os.environ.keys()
    envvar_value_old = [os.environ[envvar_name]] if envvar_exists else []

    if envvar_value != "" and '$' in envvar_value:
        envvar_value = expand_envvars_in_string(envvar_value)

    if op == "set":
        os.environ[envvar_name] = envvar_value
    elif op == "append":
        tmp = envvar_value_old + [ envvar_value ]
        newval = os.pathsep.join(tmp)
        os.environ[envvar_name] = newval
    elif op == "prepend":
        tmp = [ envvar_value ] + envvar_value_old
        newval = os.pathsep.join(tmp)
        os.environ[envvar_name] = newval
    elif op == "unset":
        if envvar_exists:
            del os.environ[envvar_name]
    else:                                                                                           # pragma: no cover
        raise ValueError                                                                            # pragma: no cover
    return 0


envvar_op("set","FOO","bar")
envvar_op("append","FOO","baz")
envvar_op("prepend","FOO","foo")
envvar_op("set","BAR","foo")
envvar_op("unset","FOO")
ModuleHelper.module("purge")
ModuleHelper.module("use","setenvironment/unittests/modulefiles")
ModuleHelper.module("load","gcc/4.8.4")
ModuleHelper.module("load","boost/1.10.1")
ModuleHelper.module("load","gcc/4.8.4")
ModuleHelper.module("unload","boost")
ModuleHelper.module("swap","gcc","gcc/7.3.0")

