#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
Helper functions for testing
"""
import os
import subprocess



#===============================================================================
#
# Mock Helpers
#
#===============================================================================

def mock_function_noreturn(*args):
    """
    Mock a function that does not return a value (i.e., returns NoneType)
    """
    print("\nmock> f({}) ==> NoneType".format(args))                                                # pragma: no cover


def mock_function_pass(*args):
    """
    Mock a function that 'passes', i.e., returns a 0.
    """
    print("\nmock> f({}) ==> 0".format(args))                                                       # pragma: no cover
    return 0                                                                                        # pragma: no cover


def mock_function_fail(*args):
    """
    Mock a function that 'fails', i.e., returns a 1.
    """
    print("\nmock> f({}) ==> 1".format(args))                                                       # pragma: no cover
    return 1                                                                                        # pragma: no cover



class mock_run_status_ok(object):
    """
    Mock for ``subprocess.run``. Has ``returncode=0``. In ModuleHelper,
    ``subprocess.run`` is only used to check for the path of modulecmd via the
    module bash function. So, we want to mock the output of ``$ type module``.
    """
    def __init__(self, cmd, stdout=None, stderr=None, shell=True):
        print(f"mock_run> {cmd}")
        self.stdout = (
            b"module is a function\nmodule () \n{ \n    eval "
            b"`/opt/cray/pe/modules/3.2.11.4/bin/modulecmd bash $*`\n}\n"
        )
        self.stderr = stderr
        self.returncode = 0



class mock_popen(subprocess.Popen):
    """
    Abstract base class for popen mock
    """
    def __init__(self, cmd, bufsize=None, shell=None, stdout=None, stderr=None):
        print("mock_popen> {}".format(cmd))
        self.bufsize = bufsize
        self.shell = shell
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = None
        super(mock_popen, self).__init__(cmd,bufsize=bufsize,shell=shell,stdout=stdout,stderr=stderr)

    def communicate(self):
        print("mock_popen> communicate()")
        stdout = b"os.environ['__foobar__'] ='baz'\ndel os.environ['__foobar__']"
        stderr = b"stderr=1"
        self.returncode = 0
        return (stdout,stderr)



class mock_popen_status_ok(mock_popen):
    """
    Specialization of popen mock that will return with success.
    """
    def __init__(self, cmd, bufsize=None, shell=None, stdout=None, stderr=None):
        super(mock_popen_status_ok, self).__init__(cmd,bufsize,shell,stdout,stderr)

#===============================================================================
#
# General Utility Functions
#
#===============================================================================

def find_config_ini(filename="config.ini", rootpath="." ):
    """
    Recursively searches for a particular file among the subdirectory structure.
    If we find it, then we return the full relative path to `pwd` to that file.

    The _first_ match will be returned.

    Args:
        filename (str): The _filename_ of the file we're searching for. Default: 'config.ini'
        rootpath (str): The _root_ path where we will begin our search from. Default: '.'

    Returns:
        String containing the path to the file if it was found. If a matching filename is not
        found then `None` is returned.

    """
    output = None
    for dirpath,dirnames,filename_list in os.walk(rootpath):
        if filename in filename_list:
            output = os.path.join(dirpath, filename)
            break
    if output is None:
        raise FileNotFoundError("Unable to find {} in {}".format(filename, os.getcwd()))            # pragma: no cover
    return output

