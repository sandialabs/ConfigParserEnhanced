#!/usr/bin/env python
"""
Module helper for Environment Modules and LMOD

This module contains a helper for using the modules subsystem.
It will attempt to load the env_modules_python
module and if that does not exist then we generate our own call
to the ``module()`` function.

This file implements two different versions of the ``module`` function
to do the same thing basically. If the LMOD-provided package
(``env_modules_python``) is found then we generate a ``module`` function
that uses that function. Otherwise, we attempt to locate an
**environment modules** based solution which uses ``/usr/bin/modulecmd``.

Both variations behave in the same general manner -- the command is used
to generate a snippet of Python code that we can execute to set up the
desired environment.

:Todo:
    This should get an overhaul at some point. It was originally just copied
    over from the old Trilinos framework infrastructure. It works so we can
    keep this around for now but it should get a refresh at some point to

    1. make this into a **class** type.
    2. Develop support for LMOD, which has *sticky* modules, etc.
    3. Clean up ability to identify failures (modulecmd / lmod tend to exit
       with status==0 even if they fail. Some implementations add the _mlstatus
       entry but it's not consistent across platforms and implementations.)
"""
from __future__ import print_function

import os
import re
import shutil
import subprocess
import sys


if "MODULESHOME" in os.environ.keys():                                                              # pragma: no cover
    sys.path.insert(1, os.path.join(os.environ['MODULESHOME'], 'init'))                             # pragma: no cover
else:                                                                                               # pragma: no cover
    print("WARNING: The environment variable 'MODULESHOME' was not found.")                         # pragma: no cover
    print("         ModuleHelper may not be able to locate modules.")                               # pragma: no cover



try: # pragma: cover if on lmod

    # Try to import the LMOD version of the module() function.
    # See: https://github.com/TACC/Lmod/blob/master/init/env_modules_python.py.in
    import env_modules_python
    # print("NOTICE> [ModuleHelper.py] Using the lmod based `env_modules_python` module handler.")


    def module(command, *arguments) -> int:
        """
        ``module`` wrapper for the LMOD based modules function.

        Args:
            command (str): The ``module`` command that we're executing.
                i.e., ``load``, ``unload``, ``swap``, etc.
            *arguments   : Variable length argument list.

        Returns:
            int: status indicating success or failure. 0 = success, nonzero for failure

            For now, because the LMOD ``module()`` command returns nothing (``NoneType``)
            and provides no way to determine success or failure, we will only return 0.

        Raises:
            Any exception thrown by env_modules_python.module() will get caught and passed along.

        """
        status = 0

        # LMOD does not capture stdout and stderr in an object, the locals below are used to capture
        # those descriptors for error checking in this function.
        stdout = ""
        stderr = ""

        # Check whether the LMOD module command exists on the system
        # We cannot use declare -F module via os.system or subprocess.Popen because
        # they are both "patched" for unit testing.... I am settling for os.getenv
        # of LMOD_CMD, which is not a bash function, for now. Note that declare -F
        # is the more robust approach.
        lmod_cmd_env = os.getenv("LMOD_CMD")
        if len(lmod_cmd_env) == 0:
            raise FileNotFoundError("Unable to find module function")

        # Attempt running the 'module' command
        # We cannot control whether module is passed to exec, that happens within
        # the env_modules_python.modules method.
        try:
            import io
            from contextlib import redirect_stdout
            from contextlib import redirect_stderr

            # env_modules_python.module does not support command as a list type, so we splat command here.
            if isinstance(command, (list)):
                _command = command
                with io.StringIO() as err, redirect_stderr(err), io.StringIO() as out, redirect_stdout(out):
                    env_modules_python.module(*command, *arguments)
                    stdout = out.getvalue()
                    stderr = err.getvalue()

            else:
                _command = []
                _command.append(command)

                with io.StringIO() as err, redirect_stderr(err), io.StringIO() as out, redirect_stdout(out):
                    env_modules_python.module(command, *arguments)
                    stdout = out.getvalue()
                    stderr = err.getvalue()

        except BaseException as error:
            print("!!")
            print("An ERROR occurred during execution of module command")
            print(stdout)
            print(stderr)
            print("!!")
            raise error

        # Check the module function output for errors
        stderr_ok = True
        if "error:" in stderr.lower():
            stderr_ok = False

        # Check for 'module' command success with short circuiting
        _arguments = _command[1:] + list(arguments)
        shell_cmds = []
        is_loaded   = "module is-loaded {0} && true  || false"
        is_unloaded = "module is-loaded {0} && false || true"
        is_file     = "[ -e {0} ] && true || false"
        # TODO: handle other commands: purge, etc.
        if _command[0] == 'load':
            shell_cmds += [is_loaded.format(_arguments[0])]
        elif _command[0] == 'unload':
            shell_cmds += [is_unloaded.format(_arguments[0])]
        elif _command[0] == 'swap':
            shell_cmds += [is_unloaded.format(_arguments[0])]
            shell_cmds += [is_loaded.format(_arguments[1])]
        elif _command[0] == 'use':
            shell_cmds += [is_file.format(_arguments[0])]

        # NOTE: mock.py does not recognize keyword argument 'shell' in __init__
        # so we bypass mock.py via os.system here instead of running:
        # proc = subprocess.run(shell_cmds, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for cmd in shell_cmds:
            status = os.system(cmd)

            if stderr_ok and status != 0:
                print("!!")
                print(stdout)
                print(stderr)
                print("!!")
                return status

        if not stderr_ok:
            print("!!")
            print("An ERROR occurred during execution of module command")
            print(stdout)
            print(stderr)
            print("!!")
            return 1

        print(stdout)
        print(stderr)

        return 0



except ImportError: # pragma: cover if not on lmod
    # print("NOTICE> [ModuleHelper.py] Using the modulecmd based environment modules handler.")


    def module(command, *arguments) -> int:
        """
        Function that enables operations on environment modules in
        the system.

        Args:
            command (str): The ``module`` command that we're executing.
                i.e., ``load``, ``unload``, ``swap``, etc.
            *arguments   : Variable length argument list.

        Returns:
            int: status indicating success or failure.  0 = success, nonzero for failure.

        Raises:
            FileNotFoundError: This is thrown if `modulecmd` is not found.

        Todo:
            Update documentation for this function to list args and how its called.
        """
        try:
            import distutils.spawn
            modulecmd = distutils.spawn.find_executable("modulecmd")
            if modulecmd is None:
                raise FileNotFoundError("Unable to find modulecmd")          # pragma: no cover
        except:
            modulecmd = shutil.which("modulecmd")

        if modulecmd is None:                                                # pragma: no cover
            # 'module' may be a bash function that points to modulecmd
            # A `module purge` might clear the location of `modulecmd` from the
            # PATH but preserve the bash function that points to `modulecmd`.
            # Use the output of `type module` to find the location.
            try:
                # $ type module
                #   - Returns something like:
                #
                #       module is a function
                #       module ()
                #       {
                #           eval `/opt/cray/pe/modules/3.2.11.4/bin/modulecmd bash $*`
                #       }

                module_func = subprocess.run(
                    "type module", stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, shell=True
                )
                matches = re.findall(r"eval `(\S*) bash.*",
                                     module_func.stdout.decode())
                if len(matches) != 1:
                    raise RuntimeError("Unable to find path to modulecmd from "
                                       "output of bash command: 'type module'")

                modulecmd = matches[0]
                if shutil.which(modulecmd) is None:
                    raise FileNotFoundError(
                        "Path to modulecmd, found by output of bash command "
                        "'type module', cannot be found by 'which' command."
                    )
            except:
                raise FileNotFoundError("Unable to find modulecmd")

        numArgs = len(arguments)

        cmd = [ modulecmd, "python", command ]

        if (numArgs == 1):
            cmd += arguments[0].split()
        else:
            cmd += list(arguments)

        # Execute the `modules` command (i.e., $ module <op> <module name(s)>)
        # but we don't actually set the environment. If successful, the STDOUT will
        # contain a sequence of Python commands that we can later execute to set up
        # the proper environment for the module operation
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (output,stderr) = proc.communicate()
        errcode = proc.returncode

        # Convert the bytes into UTF-8 strings
        output = output.decode()
        stderr = stderr.decode()

        stderr_ok = True
        if "ERROR:" in stderr:
            print("!!")
            print("!! An error occurred in modulecmd:")
            print("!!")
            stderr_ok = False
            errcode = 1

        if stderr_ok and errcode != 0:
            print("!!")
            print("!! Failed to execute the module command: {}".format(" ".join(cmd[2:])))
            print("!! - Returned {} exit status.".format(errcode))

        if stderr_ok and errcode == 0:
            try:
                # This is where we _actually_ execute the module command body.
                exec(output)

                # Check for _mlstatus = True/False (set by some versions of modulecmd)
                if "_mlstatus" in locals():
                    if locals()["_mlstatus"] == False:
                        print("!!")
                        print("!! modulecmd set _mlstatus == False, command failed")
                        print("!!")
                        errcode = 1

            except BaseException as error:
                print("!!")
                print("!! An ERROR occurred during execution of module commands")
                print("!!")
                raise error

        if errcode != 0:
            msg_output = output.strip().replace("\n", "\n!! ")
            print("!!")
            print("!! [module output start]")
            print("!! {}".format(msg_output))
            print("!! [module output end]")
            print("!! ")
            msg_stderr = stderr.strip().replace("\n", "\n!! ")
            print("!! [module stderr start]")
            print("!! {}".format(msg_stderr))
            print("!! [module stderr end]")
            print("!!")
            sys.stdout.flush()

        # Uncomment this if we want to throw an error rather than exit with nonzero code
        #if errcode != 0:
        #    raise OSError("Failed to execute module command: {}.".format(" ".join(args)))

        if errcode is None:
            raise TypeError("ERROR: the errorcode can not be `None`")

        return errcode
