#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
#===============================================================================
# Copyright Notice
# ----------------
# Copyright 2021 National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS,
# the U.S. Government retains certain rights in this software.
#
# License (3-Clause BSD)
# ----------------------
# Copyright 2021 National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS,
# the U.S. Government retains certain rights in this software.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#===============================================================================
"""
The :class:`~configparserenhanced.ConfigParserEnhanced` provides extended functionality for the :class:`~configparser.ConfigParser`
module. This class enables configurable parsing of ``.ini`` files by splitting
the **key** portion of an option in a configuration section into an **operation**
and a **parameter**.  For example, given this ``.ini`` file:

.. code-block:: ini
    :linenos:

    [SECTION_NAME]
    key: value
    operation parameter: optional value
    operation parameter uniquestr: optional value

The built-in parser will process each OPTION (``key: value`` pairs)
in-order within a SECTION. During the parsing process we attempt to
split the *key* field into two pieces consisting of an *operation*
and a *parameter*.

If there is a **handler method** associated with the **operation**
field that is extracted, then the parser will call that handler.
Handlers are added as methods named like ``_handler_<operation>()``
(with or without the leading underscore, which denotes a method not intended
to be overriden by subclasses)
and will be called if they exist.  For example, if the **operation**
field resolves to ``use``, then the parser looks for a method called
``_handler_use()``.

If the handler exists, then it is invoked. Otherwise the parser treats
the OPTION field as a generic ``key: value`` pair as normal.

In this way, we can customize our processing by subclassing
:class:`~configparserenhanced.ConfigParserEnhanced` and defining our own handler methods.

Todo:
    Determine if we can use the @final decorators (requires Python 3.8).
    If it doesn't hurt older python versions we should use them to indicate
    what methods should not be overridden, not that Python will enforce this
    but it's better than nothing.

:Authors:
    - William C. McLendon III <wcmclen@sandia.gov>
"""
from __future__ import print_function

import configparser
import inspect
import io
import os
from pathlib import Path
from pprint import pprint
import re
import shlex
import sys

try:
    # @final decorator, requires Python 3.8.x
    from typing import final # pragma: no cover
except ImportError:          # pragma: no cover
    pass                     # pragma: no cover

from .Debuggable import Debuggable
from .ExceptionControl import ExceptionControl
from .HandlerParameters import HandlerParameters
from .TypedProperty import typed_property

# Check for minimum required Python version
MIN_PYTHON = (3, 6)
if sys.version_info < MIN_PYTHON: # pragma: no cover
    raise RuntimeError("Python %s.%s or later is required.\n" % (MIN_PYTHON))

# ============================================================
#  S U P P O R T   F U N C T I O N S   A N D   C L A S S E S
# ============================================================



class AmbiguousHandlerError(Exception):
    """Raised when the parser encounters ambiguity in Handler methods.

    Attributes:
        previous -- state at beginning of transition
        next -- attempted new state
        message -- explanation of why the specific transition is not allowed
    """
    pass



# ===============================
#   M A I N   C L A S S
# ===============================



class ConfigParserEnhanced(Debuggable, ExceptionControl):
    """An enhanced ``.ini`` file parser built using :class:`ConfigParser`.

    Provides an enhanced version of the :class:`ConfigParser` module, which enables some
    extended processing of the information provided in a ``.ini`` file.

    See Also:
        - `ConfigParser reference <https://docs.python.org/3/library/configparser.html>`
    """

    def __init__(self, filename=None):
        """Constructor

        Args:
            filename (str,Path,list): The ``.ini`` file or files to be loaded. If a ``str``
                or ``Path`` is provided then we load only the one file. A ``list`` of strings
                or ``Path`` s can also be provided, which will be loaded by :class:`ConfigParser`'s
                `read() <https://docs.python.org/3/library/configparser.html#configparser.ConfigParser.read>`_
                method.
        """
        if filename is not None:
            self.inifilepath = filename

    # -----------------------
    #   P R O P E R T I E S
    # -----------------------

    parse_section_last_result = typed_property(
        "parse_section_last_result", (dict), default=None, internal_type=dict
    )

    default_section_name = typed_property("default_section_name", str, default="DEFAULT")

    _internal_default_section_name = typed_property(
        "_internal_default_section_name", str, default="CONFIGPARSERENHANCED_COMMON"
    )

    @property
    def inifilepath(self) -> list:
        """Provides access to the path to the ``.ini`` file (or files).

        ``inifilepath`` can be set to one of these things:

        1. A ``str`` contining a path to a ``.ini`` file.
        2. A ``pathlib.Path`` object pointing to a ``.ini`` file.
        3. A ``list`` of one or more of (1) or (2).

        Entries in the list will be converted to ``pathlib.Path`` objects.

        Returns:
            list: A ``list`` containing the ``.ini`` files that will be processed.

        Note:
            Subclasses should not override this.
        """
        if not hasattr(self, '_inifilepath'):
            raise ValueError("ERROR: The filename has not been specified yet.")
        return self._inifilepath

    @inifilepath.setter
    def inifilepath(self, value) -> list:
        self._validate_parameter(value, (str, list, Path))

        # If we have already loaded a .ini file, we should reset the data
        # structure. Delete any lazy-created properties, etc.
        if hasattr(self, '_inifilepath'):
            if hasattr(self, '_configparserdata'):
                delattr(self, '_configparserdata')
            self._reset_lazy_attr("_loginfo")

        # Internally we represent the inifile as a `list of Path` objects.
        # Do the necessary conversions to make that so.
        if not isinstance(value, list):
            value = [value]

        self._inifilepath = []

        for entry in value:
            try:
                self._inifilepath.append(Path(entry))
            except TypeError as ex:
                self.debug_message(0, "ERROR: invalid entry in `inifilepath` list.")
                raise ex

        return self._inifilepath

    @property
    def configparserdata(self) -> configparser.ConfigParser:
        """The raw results to a vanilla :class:`ConfigParser`-processed ``.ini`` file.

        This property is lazy-evaluated and will be processed the first time it is
        accessed.

        Returns:
            ConfigParser:  The object containing the contents of the loaded
            ``.ini`` file.

        Raises:
            ValueError: If the length of ``self.inifilepath`` is zero.
            IOError: If any of the files in ``self.inifilepath`` don't
                exist or are not files.

        Note:
            Subclasses should not override this.

        See Also:
            - Python library: `configparser <https://docs.python.org/3/library/configparser.html>`_
              reference and user-guide.
        """
        if not hasattr(self, '_configparserdata'):
            self._configparserdata = configparser.ConfigParser(
                allow_no_value=True,
                delimiters=self.configparser_delimiters,
                default_section=self._internal_default_section_name
            )

            # Prevent ConfigParser from lowercasing the keys.
            self._configparserdata.optionxform = str

            # configparser.ConfigParser.read() will not fail if it doesn't read the
            # .ini file(s) in the list, it'll just happily continue on and return
            # whatever it does get... or an empty configuration if no files were found.
            # We want to fail if we provide a bad file name so we need to check here.
            if len(self.inifilepath) == 0:
                raise ValueError("ERROR: No .ini filename(s) were provided.")

            for inifilepath_i in self.inifilepath:

                # Sanity type check here -- we'd throw on the .exists() and .is_file()
                # methods below if the entry isn't a Path object, but the error might
                # be cryptic. This will throw a more explicit error.
                # This should never happen if the users set things up through the
                # property interface.
                if isinstance(inifilepath_i, Path) is not True:
                    raise TypeError("INTERNAL ERROR: .ini file paths should be Path objects!")

                if (inifilepath_i.exists() and inifilepath_i.is_file()) is not True:
                    msg = f"\n" + \
                          f"+" + "="*78 + "+\n" + \
                          f"|   ERROR: Unable to load configuration .ini file\n" + \
                          f"|   - Requested file: `{inifilepath_i}`\n" + \
                          f"|   - CWD: `{os.getcwd()}`\n" + \
                          f"+" + "="*78 + "+\n"
                    raise IOError(msg)

            try:
                self._configparserdata.read(self.inifilepath, encoding='utf-8')
            except configparser.DuplicateOptionError as ex:
                delattr(self, '_configparserdata')
                message = "ERROR: Configparser found a section with "
                message += "two options with identical keys."
                self.debug_message(0, message)
                raise ex

        return self._configparserdata

    @property
    def configparser_delimiters(self) -> tuple:
        """Delimiters for the configparser

        Changing the value of this will trigger a **reset** of
        the cached data in the class since this fundamentally
        changes how `ConfigParser` will parse the .ini file.

        This defaults to ``('=', ':')`` which is the default
        in ConfigParser (https://docs.python.org/3/library/configparser.html)

        Returns:
            tuple: Returns a tuple containing the delimiters.

        Raises:
            TypeError: If assignment of something other than a ``tuple``,
                a ``list``, or a ``str`` is attempted.
        """
        if not hasattr(self, '_configparser_delimiters'):
            self._configparser_delimiters = ('=', ':')
        return self._configparser_delimiters

    @configparser_delimiters.setter
    def configparser_delimiters(self, value) -> tuple:
        self._validate_parameter(value, (tuple, list, str))

        self._reset_configparserdata()

        self._configparser_delimiters = tuple(value)

        return self._configparser_delimiters

    @property
    def configparserenhanceddata(self):
        """Enhanced ``configparserdata`` ``.ini`` file information data.

        This *property* returns a *parsed* representation of the ``configparserdata``
        that would be loaded from our ``.ini`` file. The data in this will return the
        contents of a section plus its parsed results. For example, if we have this
        in our ``.ini`` file:

        .. code-block:: ini

            [SEC A]
            key A1: value A1

            [SEC B]
            use 'SEC A':
            key B1: value B1

        Extracting the data from 'SEC B' would result the contents of 'SEC B' + 'SEC A':

            >>> ConfigParserEnhancedObj.configparserenhanceddata["SEC B"]
            {
                'key A1': 'value A1',
                'key B1': 'value B1'
            }

        Options that resolve to a format matching an operation
        (``operation parameter : value``) what *also* have a handler
        defined (i.e, the operation is "handled") will **not** be included
        in the data of a section. This is shown in the example above where
        the ``use 'SEC A':`` option in ``[SEC B]`` is not included in
        ``configparserenhanceddata["SEC B"]`` after processing.

        Returns:
            :class:`~configparserenhanced.ConfigParserEnhanced.ConfigParserEnhancedData`

        Note:
            Subclasses should not override this.
        """
        if not hasattr(self, '_configparserenhanceddata'):
            self._configparserenhanceddata = self.ConfigParserEnhancedData(owner=self)
        return self._configparserenhanceddata

    # ---------------------------------------
    #   P U B L I C   A P I   M E T H O D S
    # ---------------------------------------

    def write(
        self, file_object, space_around_delimiters=True, section=None, use_base_class_parser=True
    ) -> int:
        """File writer utility for ConfigParserEnhanced objects.

        Writes the output of :py:meth:`unroll_to_str` to a file.

        Args:
            file_object (:obj:`File Ptr`): Pointer to the file that should be written.
            space_around_delimiters (bool): If ``True`` the delimiter is given an extra
                space of padding.
            section (:obj:`str`): If a section name is provided we only generate the specified
                section (if it exists), otherwise we generate output for all sections.

        Raises:
            TypeError: If ``file_object`` is not a file pointer (instance or derivitive
                of ``io.IOBase``).
        """
        self._validate_parameter(file_object, (io.IOBase))

        text = self.unroll_to_str(
            section=section,
            space_around_delimiters=space_around_delimiters,
            use_base_class_parser=use_base_class_parser
        )

        file_object.write(text)

        return 0

    def assert_file_all_sections_handled(self) -> int:
        """
        Checks that ALL the options within a file are fully handled.
        This calls ``assert_section_all_options_handled`` on all the sections
        of a .ini file.

        Returns:
            int: 0 indicates a successful parse with no errors. Otherwise if problems
                 are detected then the return code will be nonzero.
                 Note the return value only occurs if ``exception_control_level`` is
                 2 or lower (See **Raises** notes on this method for more details).

        Raises:
            ValueError: A ``ValueError`` is raised if there are any *unhandled options*
                        detected in the file(s) loaded in *any* section. The error can
                        be suppressed by setting ``exception_control_level`` to suppress
                        ``SERIOUS`` errors (2 or lower).
                        If the exception is suppressed then this method will return a
                        nonzero integer.
        """
        output = 0

        for section in self.configparserenhanceddata.sections(parse=False):
            err = self.assert_section_all_options_handled(section, do_raise=False)

            if err != 0:
                self.debug_message(0, err)
                output = 1

        if output != 0:
            tmp_fileslist = [str(x) for x in self.inifilepath]
            message = self.get_known_operations_message()
            message += "\nThis configuration was loaded from the file(s):\n|- "
            message += "\n|- ".join(tmp_fileslist)
            self.debug_message(0, message)
            self.exception_control_event("SERIOUS", ValueError, message.strip())

        return output

    def assert_section_all_options_handled(self, section_name: str, do_raise: bool = True) -> int:
        """
        This method provides a validation capability against a *section* in a
        .ini file to validate that all of the entries are handled. The use case
        of this is fairly specific will flag any 'unhandled' options within
        a section under an expectation that the intent or design of the .ini
        file is that _all_ options are handled by some handler and _any_ that
        are not indicate an error or typo of some sort.

        Args:
            section_name (str): The _name_ of the section that will be searched.
                Note: in ``ConfigParserEnhanced`` this includes the fully parsed
                section which includes the *transitive closure* of the dependency
                graph imposed by ``use`` operations.

            do_raise (bool): If True (default) then this assert will trigger
                an ``exception_control_event`` that may raise a ``ValueError``
                if there are unhandled entries detected.
                If False then the return value is set to nonzero if unhandled
                entries are found but the **ece** is not triggered.

        Returns:
            int: 0 indicates a successful parse with no errors, otherwise
                 any nonzero return value indicates there is at least one
                 entry in the section that was not properly handled.
                 IF a *bad* entry is found then the output will be a string
                 containing a message that indicates what the bad entries
                 are.

        Raises:
            ValueError: A ``ValueError`` is raised if there are any *unhandled options*
                        detected in the file(s) loaded in *any* section. The error can
                        be suppressed by setting ``exception_control_level`` to suppress
                        ``SERIOUS`` errors (2 or lower).
                        If the exception is suppressed then this method will return a
                        nonzero integer.
        """
        output = 0
        section_data = self.configparserenhanceddata.get(section_name)

        if len(section_data):
            message = f"Unhandled option found in section `{section_name}`"
            message += " or one of its dependent sections.\n"
            message += "The following entries are unhandled:\n"
            for k, v in section_data.items():
                message += f"|- '{k}'\n"
            if do_raise:
                tmp_fileslist = [str(x) for x in self.inifilepath]
                message += self.get_known_operations_message()
                message += "\nThis configuration was loaded from the file(s):\n|- "
                message += "\n|- ".join(tmp_fileslist)
                self.exception_control_event("SERIOUS", ValueError, message.strip())
            output = message.rstrip()
        return output

    def get_known_operations_message(self):
        """
        Generate a string that lists valid **operations**.

        Returns:
            str: A string containing the message listing the valid operations.
        """
        message = "Valid operations are:\n"
        for op in self.get_known_operations():
            message += f"|- '{op}'\n"
        return message.rstrip()

    def get_known_operations(self):
        """
        Generate a list of *known* operation keywords based on the
        existing handlers defined in this class.

        There is potentially some data loss here since there is nothing in
        ConfigParserEnhanced that would prevent someone from defining an
        *operation* of the form ``foo_bar`` rather than ``foo-bar`` but since
        the parser will always convert ``-`` to ``_``, in terms of processing
        an operation there would be no distinction between ``foo-bar`` and
        ``foo_bar``.

        Returns:
            list: A list of strings is returned containing the list of
                  known operations based on existing handlers.
        """
        # Regex that looks for ``_handler`` or ``handler`` at the front of a string
        re_handler_name = re.compile(r"^_?handler_")

        # Regex that looks for strings that match any one of these options:
        # - "_handler_initialize"
        # - "_handler_finalize"
        # - "handler_initialize"
        # - "handler_finalize"
        re_handler_init_final = re.compile(r"^_?handler_((finalize)|(initialize))$")

        # Regex that is used in the list comprehension below to strip the handler
        # prefix out of the name when we attempt to generate the operation names.
        # - Matches "_handler_" and "handler_"
        re_strip_handler_prefix = re.compile(r"^_?handler_")

        # This list comprehension scans through the defined methods and will
        # pull out every method that starts with "_handler" or "handler"
        # and then strips the optional leading "_" off, then strips the
        # leading "handler_" component off and finally replaces "_" with "-"
        # in the handler name to generate the operation name.
        # wcmclen - 2021-09-03 - The TypedProperty entry for `parse_Section_last_result`
        #           was triggering the exception that required assignment before use
        #           in the `getmembers` call here. I removed that condition on the property
        #           but it might be worth figuring out why the inspection triggered it.
        #           Perhaps `TypedProperty` needs a proper _getter_ implemented?
        output = [
            re_strip_handler_prefix.sub("", x[0]).replace("_", "-")
            for x in inspect.getmembers(self, predicate=inspect.ismethod)
            if re_handler_name.search(x[0]) and not re_handler_init_final.search(x[0])
        ]
        return output

    def unroll_to_str(self, section=None, space_around_delimiters=True, use_base_class_parser=True) -> str:
        """Unroll a section or whole .ini file to a string

        This method generates a string that is the equivalent to the original
        ``.ini`` file that is loaded with all the ``use`` operations processed
        so that the output will look like a regular ``.ini`` file.

        If ``use_base_class_parser`` is set then we instantiate a base-class
        :py:class:`ConfigParserEnhanced` that will load and (re)parse the
        :py:attr:`inifilepath` file(s) to generate a "clean" copy. Because all
        options that have *handled* operations in them will be stripped from the
        generated .ini file, the most common use case is that we just want the
        ``use`` operations processed and stripped, but this paramter gives the
        option to disable that capability.

        Args:
            section (:obj:`str`): If a section name is provided we only generate the specified
                section (if it exists), otherwise we generate output for all sections.
            space_around_delimiters (bool): If ``True`` the delimiter is given an extra
                space of padding.
            use_base_class_parser (bool): If ``Tru`` then we instantiate a
                :py:class:`ConfigParserEnhanced` object to parse the .ini file.
                If ``False`` then we use the current class (possibly a sub-class)
                of :py:class:`ConfigParserEnhanced`, which will strip out all options
                that have *handled* operations.

        Raises:
            TypeError: If ``section`` is not a ``str`` or ``None`` object.
        """

        def __generate_section(section: str, parser, delimiter=":"):
            """
            Helper function (inner function)

            This function generates the string containing the section header
            and options.
            """
            output = ""
            if parser.configparserenhanceddata.has_section(section):
                output += f"[{section}]\n"
                for key, value in parser.configparserenhanceddata.items(section):
                    if value is None:
                        value = ""
                    output += delimiter.join([key, value]).strip() + "\n"
            else:
                raise KeyError(f"Section `{section}` was not found.")
            return output

        self._validate_parameter(section, (type(None), str))

        output_str = ""

        delimiter = ":"
        if space_around_delimiters:
            delimiter = " {} ".format(delimiter)

        parser = None
        if use_base_class_parser:
            parser = ConfigParserEnhanced(filename=self.inifilepath)
        else:
            parser = self

        # Turn off ECL notifications
        ecl = parser.exception_control_level
        parser.exception_control_level = 0

        section_list = parser.configparserenhanceddata.sections()

        if section is None:
            for section in section_list:
                output_str += __generate_section(section, parser, delimiter)
                output_str += "\n"
        else:
            output_str += __generate_section(section, parser, delimiter)

        # reset parser ECL (only useful when not using base class parser)
        parser.exception_control_level = ecl

        output_str = output_str.strip()
        output_str += "\n"

        return output_str

    # -------------------------------------
    #   P A R S E R   P U B L I C   A P I
    # -------------------------------------

    def parse_all_sections(self):
        """Parse ALL sections in the .ini file.

        This can be useful if the user wishes to pre-parse all the sections
        of an ``ini`` file in one go.
        """
        self.configparserenhanceddata.sections(True)
        return

    def parse_section(self, section, initialize=True, finalize=True):
        """Execute parser operations for the provided *section*.

        Args:
            section (str): The section name that will be parsed and retrieved.
            initialize (bool): If True then :meth:`handler_initialize()` will be executed
                at the start of the search.
            finalize (bool): If True then :meth:`handler_finalize()` will be executed
                at the end of the search.
        Returns:
            :attr:`~.HandlerParameters.data_shared` property from :class:`~.HandlerParameters`.
            Unless :class:`~.HandlerParameters` is changed, this wil be a ``dict`` type.
        """
        # If a previous run generated _loginfo, clear it before this run.
        self._reset_lazy_attr("_loginfo")

        self.debug_message(1, f"[" + "-"*58 + ']')
        self.debug_message(1, f"  Parse section `{section}` START")
        self.debug_message(1, f"[" + "-"*58 + ']')
        self._validate_parameter(section, (str))

        if section == "":
            raise ValueError("`section` cannot be empty.")

        # Parse the requested section.
        result = self._parse_section_r(section, initialize=initialize, finalize=finalize)

        # caches the "data_shared" component of handler_parameters
        self.parse_section_last_result = result

        self.debug_message(1, f"[" + "-"*58 + ']')
        self.debug_message(1, f"  Parse section `{section}` FINISH")
        self.debug_message(1, f"[" + "-"*58 + ']')
        return result

    # ---------------------------------
    #   D E C O R A T O R S
    # ---------------------------------

    def operation_handler(func_handler):
        """
        Implements the ``operation_handler`` decorator.

        This decorator is used on *handlers* and implements entry and exit
        calls and exit value checks.

        .. code-block:: python
            :linenos:

            @operation_handler
            def handler_my_operation(self, section_name, handler_parameters) -> int:
                # do stuff
                return 0

        Args:
            func_handler (Callable): Reference to the handler function.
                This gets managed through Python's decorator syntax.
        """

        def wrapper(self, section_name, handler_parameters):
            self._validate_parameter(section_name, (str))
            self.enter_handler(handler_parameters)
            output = func_handler(self, section_name, handler_parameters)
            self.exit_handler(handler_parameters)
            self._check_handler_rval(handler_parameters.handler_name, output)
            return output

        return wrapper

    # ---------------------------------
    #   P U B L I C   H A N D L E R S
    # ---------------------------------

    def enter_handler(self, handler_parameters):
        """General tasks to do when entering a handler

        This executes some general operations that should be executed when entering
        a handler. Generally, these are just logging and console messages for
        debugging.

        Args:
            handler_parameters (HandlerParameters): The parameters passed to
                the handler.
        """
        self._validate_handlerparameters(handler_parameters)

        handler_name = handler_parameters.handler_name
        self.debug_message(1, f"Enter handler    : {handler_name}")                     # Console
        self.debug_message(1, f" -> raw_option   : {handler_parameters.raw_option}")    # Console
        self.debug_message(2, f" -> op           : {handler_parameters.op}")            # Console
        self.debug_message(2, f" -> params       : {handler_parameters.params}")        # Console
        self.debug_message(2, f" -> value        : {handler_parameters.value}")         # Console
        self.debug_message(3, f" -> data_shared  : {handler_parameters.data_shared}")   # Console
        self.debug_message(4, f" -> data_internal: {handler_parameters.data_internal}") # Console

        self._loginfo_add(
            'handler-entry', {
                'name': handler_name,
                'entry': handler_parameters.raw_option,
                'parameters': handler_parameters
            }
        )
        return

    def exit_handler(self, handler_parameters):
        """General tasks to do when entering a handler

        This executes some general operations that should be executed when entering
        a handler. Generally, these are just logging and console messages for
        debugging.

        Args:
            handler_parameters (HandlerParameters): The parameters passed to
                the handler.
        """
        self._validate_handlerparameters(handler_parameters)

        handler_name = handler_parameters.handler_name
        self.debug_message(1, f"Exit handler     : {handler_name}")                     # Console
        self.debug_message(1, f" -> raw_option   : {handler_parameters.raw_option}")    # Console
        self.debug_message(3, f" -> data_shared  : {handler_parameters.data_shared}")   # Console
        self.debug_message(4, f" -> data_internal: {handler_parameters.data_internal}") # Console

        self._loginfo_add(
            'handler-exit', {
                'name': handler_name,
                'entry': handler_parameters.raw_option,
                'parameters': handler_parameters
            }
        )
        return

    @operation_handler
    def _generic_option_handler(self, section_name, handler_parameters) -> int:
        """Generic Handler Template

        This handler is used for options whose ``key:value`` pair does not
        get resolved to a proper ``<operation>`` and therefore do not get
        routed to a ``handler_<operation>()`` method.

        This method provides a great *template* for subclasses to use when
        creating new custom handlers according to the naming scheme
        ``handler_<operation>()`` or ``_handler_<operation>()``.

        Note:
            This method should not be overridden by subclasses.

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
        # -----[ Handler Content Start ]-------------------
        # -----[ Handler Content End ]---------------------
        return 0

    @operation_handler
    def handler_initialize(self, section_name, handler_parameters) -> int:
        """Initialize a recursive parse search.

        This handler is called at the start of a recursive search of the
        ``.ini`` structure. Subclasses can override this method to perform setup
        actions at the start of a search.

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
        # -----[ Handler Content Start ]-------------------
        # -----[ Handler Content End ]---------------------
        return 0

    @operation_handler
    def handler_finalize(self, section_name, handler_parameters) -> int:
        """Finalize a recursive parse search.

        This handler is called at the end of a search and can be used
        to *finalize* processing of ``.ini`` sections or save/cache
        data from the search that other handlers added to
        ``handler_parameters.data_shared``.

        Args:
            section_name (str): The name of the section being processed.
            handler_parameters (HandlerParameters): The parameters passed to
                the handler.

        For this handler, the ``handler_parameters`` entries will only populate
        the ``handler_name`` and ``data_shared`` properties.

        Returns:
            int:
            * 0     : SUCCESS
            * [1-10]: Reserved for future use (WARNING)
            * > 10  : An unknown failure occurred (CRITICAL)
        """
        # -----[ Handler Content Start ]-------------------
        # -----[ Handler Content End ]---------------------
        return 0

    # ---------------------------------------------------
    #   P A R S E R   H E L P E R S   ( P R I V A T E )
    # ---------------------------------------------------

    def _parse_section_r(self, section_name, handler_parameters=None, initialize=True, finalize=True):
        """Recursive driver of the parser.

        This is the main heavy lifter of the parser.

        Args:
            section_name (str): The name of the section being processed.
            handler_parameters (HandlerParameters): The parameters passed to
                the handler.
            initialize (bool): If enabled *and* this level of recursion is the *root*
                level then we will call ``handler_initialize()`` to do some preprocessing
                activities.
            finalize (bool): If enabled *and* this level of recursion is the *root*
                level then we will call ``handler_finalize()`` to wrap up the
                recursion.

        Returns:
            :attr:`~HandlerParameters.data_shared`
        """
        self._validate_parameter(section_name, (str))
        self._validate_parameter(initialize, (bool))
        self._validate_parameter(finalize, (bool))

        # Initialize handler_parameters if not currently set up.
        if handler_parameters is None:
            handler_parameters = self._new_handler_parameters()

            # Check that we got the right data structure from _new_handler_parameters
            # in case someone overrides this later on.
            self._validate_parameter(handler_parameters, (HandlerParameters))

            handler_parameters.section_root = section_name

            # Pitfall: Only add 'sections_checked' for the _root_ node
            #          because configparserenhanceddata recurses through and we
            #          want it's "meta section" to encapsulate the result
            #          of the fully parsed entry from the the root section
            #          of the search only.
            self.configparserenhanceddata._sections_checked.add(section_name)
        else:
            # If we got a handler_parameters handed to us (i.e., recursion)
            # we should make a new HandlerParameters object and copy references
            # of the parts that need to be updated by all levels of recursion
            # but not allow side-effects to modify the other entries that are
            # relevant to the caller's scope.
            handler_parameters = self._new_handler_parameters(handler_parameters)

        # Execute _handler_initialize to add a pre-processing step.
        if initialize and section_name == handler_parameters.section_root:
            handler_initialize_params = self._new_handler_parameters(handler_parameters)
            handler_initialize_params.handler_name = "handler_initialize"
            self.handler_initialize(section_name, handler_initialize_params)

            if self.configparserdata.has_section(self.default_section_name):
                self._parse_section_r(
                    self.default_section_name,
                    handler_parameters=handler_parameters,
                    initialize=False,
                    finalize=False
                )

        self.debug_message(1, f">>> Enter section    : `{section_name}`") # Console Logging
        self._loginfo_add('section-entry', {'name': section_name})      # Logging

        # Load the section from the configparser.ConfigParser data.
        current_section = None
        try:
            current_section = self.configparserdata[section_name]
        except KeyError:
            message = "ERROR: No section named `{}` was found in the configuration file {}.".format(
                section_name, self.inifilepath
            )
            raise KeyError(message)

        if current_section is None: # pragma: no cover (UNREACHABLE)
            raise Exception("ERROR: Unable to load section `{}` for an unknown reason.".format(section_name))

        # At this point we should know we have a valid/existing section.

        self.configparserenhanceddata.add_section(section_name)

        # Initialize and set processed_sections.
        self._validate_handlerparameters(handler_parameters)
        handler_parameters.data_internal['processed_sections'].add(section_name)

        for sec_k, sec_v in current_section.items():
            sec_k = str(sec_k).strip()

            # sec_v should be either a string or a NoneType entry. In the
            # general case of either `key: value` or `key = value`, the value
            # will be a string.  If the user specified `key:` (that is, with a
            # separator, but without a value), then the value is the empty
            # string "".  If the user omits the separator *and* the value,
            # e.g., by specifying only `key`, then the value will be a
            # NoneType.
            if sec_v is not None:
                sec_v = str(sec_v).strip()
                sec_v = sec_v.strip('"')

            handler_parameters.raw_option = (sec_k, sec_v)
            handler_parameters.value = sec_v

            self.debug_message(2, f"==>")
            self.debug_message(2, f"==> Entry        : `{sec_k}` : `{sec_v}`")         # Console
            self.debug_message(2, f"==>")
            self._loginfo_add('section-key-value', {'key': sec_k, 'value': sec_v}) # Logging

            # sec_k_tok = shlex.split(sec_k)                                                        # DEPRECATED
            sec_k_tok = self._tokenize_option_key(sec_k)

            if not re.match(r"^[\w\-]+$", sec_k_tok[0]):
                # Call generic_handler if the first entry has invalid characters
                self._launch_generic_option_handler(section_name, handler_parameters, sec_k, sec_v)
            else:
                # Otherwise, it _could_ be a 'handled' operation
                op, params = self._get_op_components_from_tokenized_option_key(sec_k_tok)

                #op = self._apply_transformation_to_operation(op)                                   # DEPRECATED
                #params = [self._apply_transformation_to_parameter(x) for x in params]              # DEPRECATED

                handler_parameters.op = op
                handler_parameters.params = params

                self._loginfo_add('section-operation', {'op': op, 'params': params}) # Logging
                self.debug_message(2, f" -> op           : {handler_parameters.op}")     # Console
                self.debug_message(2, f" -> params       : {handler_parameters.params}") # Console
                self.debug_message(2, f" -> value        : {handler_parameters.value}")  # Console

                handler_name, ophandler_f = self._locate_handler_method(handler_parameters.op)

                if ophandler_f is not None:
                    handler_parameters.handler_name = handler_name
                    ophandler_f(section_name, handler_parameters)
                else:
                    self._launch_generic_option_handler(section_name, handler_parameters, sec_k, sec_v)

        # If we're exiting recursion from the root node and and finalize is
        # enabled, we call the finalize handler.
        if finalize and section_name == handler_parameters.section_root:
            handler_finalize_params = self._new_handler_parameters(handler_parameters)
            handler_finalize_params.handler_name = "handler_finalize"
            self.handler_finalize(section_name, handler_finalize_params)

        # Remove the section from the `processed_sections` field when we exit.
        # - This properly enables a true depth-first search of `use` links.
        self._validate_handlerparameters(handler_parameters)
        handler_parameters.data_internal['processed_sections'].remove(section_name)

        # Set up the return value.
        output = handler_parameters.data_shared

        # Finalize the logging data / output
        self._loginfo_add('section-exit', {'name': section_name})      # Logging
        self.debug_message(1, "Exit section: `{}`".format(section_name)) # Console

        return output

    def _tokenize_option_key(self, option_key):
        """
        """
        option_key = str(option_key).strip()
        option_key_tok = shlex.split(option_key)
        return option_key_tok

    def _get_op_components_from_tokenized_option_key(self, option_key_tok):
        """
        Take a partitioned ``operation`` that comes in as a list and
        split it up into the ``operation`` and ``parameters``.

        Returns:
            tuple: A tuple containing the ``(op, params)`` where ``op`` is
                   a string and ``params`` will be a list of 0..N parameters.
        """
        op = option_key_tok[0]
        params = option_key_tok[1 :]

        # Clean up / apply necessary transformations to the operation and parameters
        op = self._apply_transformation_to_operation(op)
        params = [self._apply_transformation_to_parameter(x) for x in params]

        return (op, params)

    def _validate_handlerparameters(self, handler_parameters):
        """Check :class:`HandlerParameters`.

        Check the ``handler_parameters`` object that's being passed around
        to the handlers to verify that items in it have the proper types.

        Raises:
            TypeError: Raises a ``TypeError`` if
                ``handler_parameters.data_internal['processed_sections']`` is not a ``set``
                type.
        """
        self._validate_parameter(handler_parameters, (HandlerParameters))

        if not isinstance(handler_parameters.data_internal['processed_sections'], set):
            message = "`handler_parameters.data_internal['processed_sections']` " + \
                      "must be a `set` type."
            raise TypeError(message)

        return None

    def _new_handler_parameters(self, handler_parameters=None) -> HandlerParameters:
        """Generate a new :class:`~configparserenhanced.HandlerParameters` object.

        This is called inside the parser to generate :class:`HandlerParameters`.
        If subclasses extend the :class:`~configparserenhanced.HandlerParameters`
        class, this can be overridden.

        Args:
            handler_parameters: an existing ``HandlerParameters`` object to copy the
                *persistent* state over from (i.e., ``data_shared``, ``data_internal``)
                for continuity in the new object.

        Returns:
            :class:`~configparserenhanced.HandlerParameters` object.
        """
        new_handler_parameters = HandlerParameters()
        new_handler_parameters.data_internal['processed_sections'] = set()

        # Copy the 'persistent' state from the old handler_parameters object.
        if handler_parameters != None:
            new_handler_parameters.data_internal = handler_parameters.data_internal
            new_handler_parameters.data_shared = handler_parameters.data_shared
            new_handler_parameters.section_root = handler_parameters.section_root

        return new_handler_parameters

    def _apply_transformation_to_operation(self, operation) -> str:
        """
        Apply transformations to the **operator** parameters which are necessary
        for the parser and down-stream handlers.

        Current transformations:

            - Repalce all occurrences of `-` with `_`

        Returns:
            str: A string containing the transformed operator parameter.
        """
        output = operation.replace("-", "_")
        return output

    def _apply_transformation_to_parameter(self, parameter) -> str:
        """
        Applies transformations to the **parameter** field if necessary.

        Current transformations:

            - *none at this time*

        Returns:
            str: A string containing the transformed operator parameter.
        """
        output = parameter
        return output

    def _locate_handler_method(self, operation) -> tuple:
        """Convert ``operation`` to a handler name and get the reference to the handler.

        This method converts the *operation* parameter (op) to a
        handler name and searches for the existence of a matching
        method.

        Handlers may be of the format: ``_handler_<operation>`` for
        internal/private handlers (that should not be overridden)
        or ``handler_<operation>`` for handlers that are considered
        fair game for subclasses to override and customize.

        In the case where there are both public and private handlers for
        the same operation defined, we will optionally raise a
        ``AmbiguousHandlerErorr`` if the ``exception_control_level`` is set
        high enough to trigger "SERIOUS" events. Otherwise, we will choose
        the *PUBLIC* handler definition to execute.

        Args:
            operation (str): The operation parameter that is converted to
              a proper handler name of the form ``_handler_{operation}()``
              or ``handler_{operation}()``.

        Returns:
            tuple: A tuple containing the ``(handler_name, handler_method)`` where:
              - ``handler_name`` is a string.
              - ``handler_method`` is either a reference to the handler method
                if it exists, or None if it does not exist.

        Raises:
            AmbiguousHandlerError: An ``AmbiguousHandlerError`` might be raised
                if both a *public* and a *private* handler of the same name are
                defined and the ``exception_control_level`` is set to raise
                exceptions for "SERIOUS" events.
        """
        self._validate_parameter(operation, (str))

        handler_name = operation
        handler_name = self._apply_transformation_to_operation(handler_name)

        handler_name_private = "_handler_{}".format(handler_name)
        handler_name_public = "handler_{}".format(handler_name)

        handler_public = self._locate_class_method(handler_name_public)
        handler_private = self._locate_class_method(handler_name_private)

        if (handler_private[1] is not None) and (handler_public[1] is not None):
            message = "Ambiguous handler name."
            message += " Both `{}` and `{}` exist".format(handler_name_private, handler_name_public)
            message += " but only one is allowed."
            self.exception_control_event("SERIOUS", AmbiguousHandlerError, message)

        output = (None, None)
        if handler_public[1] is not None:
            self.debug_message(4, f" -> Using _public_ handler : `{handler_name_public}`")  # Console
            output = handler_public
        elif handler_private[1] is not None:
            self.debug_message(4, f" -> Using _private_ handler: `{handler_name_private}`") # Console
            output = handler_private
        else:
            self.debug_message(4, f" -> No handler found for operation `{handler_name}`")   # Console

        return output

    def _locate_class_method(self, method_name) -> tuple:
        """Helper that locates a class method (if it exists)

        Args:
            method_name (str): The name of the class method we're searching for.

        Returns:
            tuple: A tuple containing the name and a reference to the method if it
                is found or None if not found. ``(method_name, method_ref or None)``
        """
        output = (None, None)
        method_f = getattr(self, method_name, None)
        output = (method_name, method_f)

        if output[1] == None:
            self.debug_message(5, f" -> Class method `{method_name}` was not found.") # Console

        return output

    def _check_handler_rval(self, handler_name, handler_rval) -> 0:
        """Check the returned value from a handler.

        Args:
            handler_name (string): The name of the handler.
            handler_rval (int): The return value from a handler being processed.

        Returns:
            int: Returns a 0 if everything is ok or a 1 if a warning occurred.

        Raises:
            RuntimeError: If ``handler_rval > 0`` and the ``exception_control_level``
                is high enough, depending on the value of ``handler_rval``.
        """
        self._validate_parameter(handler_name, (str))
        self._validate_parameter(handler_rval, (int))

        self.debug_message(2, f"_check_handler_rval({handler_name}, {handler_rval})")

        output = 0
        if handler_rval == 0:
            pass
        elif handler_rval <= 10:
            # These rvals are currently reserved. If someone uses it we should
            # throw a critical error to get the developers' attention to either
            # expand rval handling or users should use something > 10.
            self.exception_control_event(
                "WARNING", RuntimeError, f"Handler `{handler_name}` returned {handler_rval}"
            )
            output = 1
        else:
            self.exception_control_event(
                "CATASTROPHIC", RuntimeError, f"Handler `{handler_name}` returned {handler_rval}"
            )
        return output

    def _launch_generic_option_handler(self, section_name, handler_parameters, sec_k, sec_v) -> int:
        """Launcher for ``_generic_option_handler()``

        ``_generic_option_handler()`` is called in two places inside the recursive parser.

        1. It is called when the ``key:value`` pair in an option does not parse out
           to ``operation`` and ``parameter`` fields.
        2. It is called when the ``key:value`` pair in an option does parse to
           an ``operation`` and a ``parameter`` field, but there are no handlers
           defined for the ``operation``.

        This helper just manages the call in both places so thay're done the same way.

        Returns:
            int: Returns the output value from ``_generic_option_handler()``
        """
        self._validate_parameter(section_name, (str))
        self._validate_handlerparameters(handler_parameters)
        self._validate_parameter(sec_k, (str, None))
        self._validate_parameter(sec_v, (str, None))

        output = 0

        self.configparserenhanceddata.set(handler_parameters.section_root, sec_k, sec_v)

        handler_parameters.handler_name = "_generic_option_handler"
        output = self._generic_option_handler(section_name, handler_parameters)

        return output

    # ---------------------------------------
    #   H A N D L E R S   ( P R I V A T E )
    # ---------------------------------------

    @operation_handler
    def _handler_use(self, section_name, handler_parameters) -> int:
        """
        This is a handler that will get executed when we detect a `use` operation in
        our parser.

        Args:
            section_name (str): The name of the section being processed.
            handler_parameters (HandlerParameters): The parameters for the current operation.

        Returns:
            int:
            * 0     : SUCCESS
            * [1-10]: Reserved for future use (WARNING)
            * > 10  : An unknown failure occurred (CRITICAL)

        Todo:
            Once we can use Python 3.8 in our environments, we can use the @final decorator
            to mark this as something that should not be overridden. We also have to
            import it: `from typing import final`.
            https://stackoverflow.com/questions/321024/making-functions-non-override-able
        """
        entry = handler_parameters.raw_option
        handler_name = handler_parameters.handler_name
        op1 = handler_parameters.op
        op2 = handler_parameters.params[0]

        if op2 not in handler_parameters.data_internal['processed_sections']:
            self._parse_section_r(op2, handler_parameters, finalize=False)
        else:
            self._loginfo_add('cycle-detected', {'sec-src': section_name, 'sec-dst': op1}) # Logging
            self._loginfo_add('handler-exit', {'name': handler_name, 'entry': entry})      # Logging

            message = f"Detected a cycle in `use` dependencies in .ini file {self.inifilepath}.\n"
            message += f"- cannot load [{op2}] from [{section_name}]."
            self.exception_control_event("WARNING", ValueError, message)

        return 0

    # -------------------------------------
    #   H E L P E R S   ( P R I V A T E )
    # -------------------------------------

    def _reset_configparserdata(self) -> int:
        """Reset the internal state for all of the ConfigParser data.

        Resets these properties to their initial state:
        - ``configparserdata``
        - ``configparserenhanceddata``
        - ``parse_section_last_result``
        - ``_loginfo``
        """
        self._reset_lazy_attr("_loginfo")
        self._reset_lazy_attr("_configparserdata")
        self._reset_lazy_attr("_configparserenhanceddata")
        del self.parse_section_last_result
        return 0

    def _reset_lazy_attr(self, attribute: str) -> int:
        """Deletes an attribute of the class if it exists.

        This is used to reset lazy-evaluated property private storage
        back down to the initial ground-state.
        """
        self._validate_parameter(attribute, (str))
        if hasattr(self, attribute):
            delattr(self, attribute)
        return 0

    def _loginfo_add(self, typeinfo, entry) -> None:
        """
        If in debug mode, we can use this to log operations by appending to ``_loginfo``.

        Args:
            typeinfo (str): The kind of operation this is. This generates the
                'type' entry in the ``_loginfo`` dict. (Required)
            entry (dict): A dictionary containing log information that we're appending.
                At minimum it should have: ``{ type: typestring }``.

        Todo:
            Once we can use Python 3.8 in our environments, we can use the @final decorator
            to mark this as something that should not be overridden. We also have to
            import it: `from typing import final`.
            https://stackoverflow.com/questions/321024/making-functions-non-override-able
        """
        if not hasattr(self, '_loginfo'):
            self._loginfo = []

        if self.debug_level > 0:
            if not isinstance(entry, dict):
                raise TypeError("Entry should be a `dict` type.")
            entry['type'] = typeinfo

            self._loginfo.append(entry)

        return

    def _loginfo_print(self, pretty=True) -> None:
        """
        This is a helper to pretty-print the ``_loginfo`` object.

        Todo:
            Once we can use Python 3.8 in our environments, we can use the @final decorator
            to mark this as something that should not be overridden. We also have to
            import it: `from typing import final`.
            https://stackoverflow.com/questions/321024/making-functions-non-override-able
        """
        if pretty:
            self.debug_message(1, "Loginfo:")
            len_max_type = 0
            len_max_key = 0
            for entry in self._loginfo:
                len_max_type = max(len_max_type, len(entry['type']))
                for k, v in entry.items():
                    len_max_key = max(len_max_key, len(k))

            special_keys = ["type", "name"]

            for entry in self._loginfo:

                for key in special_keys:
                    if key in entry.keys():
                        line = ("--> " if key != special_keys[0] else "    ")
                        line += "{} : {} ".format(key.ljust(len_max_key), entry[key])
                        self.debug_message(1, line)

                for k, v in entry.items():
                    if k not in special_keys:
                        line = "--> {} : {}".format(k.ljust(len_max_key), v)
                        self.debug_message(1, line)
                self.debug_message(1, "")
        else:
            print(self._loginfo)

        return

    def _validate_parameter(self, parameter, type_restriction, exception_class="CATASTROPHIC") -> int:
        """Parameter validation with ExcpetionControl event on failure.

        Returns:
            int: 0 if typecheck succeeds. 1 if typecheck fails and the
                ``exception_control_level`` prevented the exception from
                being raised.

        Raises:
            TypeError: If the typecheck fails.
        """
        output = 0

        # It's pretty common for someone to enter (int, None) to isinstance()
        # which is wrong, `None` isn't a type.
        if not isinstance(type_restriction, tuple):
            type_restriction = tuple([type_restriction])
        type_restriction = tuple([x if x != None else type(x) for x in type_restriction])

        if not isinstance(parameter, type_restriction):
            output = 1
            self.exception_control_event(
                exception_class, TypeError, f"`{parameter}` must be a `{type_restriction}` type."
            )
        return output

    # ===========================================================
    #  I N N E R   C L A S S ( E S )
    # ===========================================================

    class ConfigParserEnhancedData(Debuggable, ExceptionControl):
        """ConfigParserEnhancedData

        This class is intended to serve as a *lite* analog to
        :class:`ConfigParser` to provide a similar result but with
        the :class:`~ConfigParserEnhanced` class's ability to parse ``.ini`` files and
        follow entries that implement a ``use <section name>`` rule. In
        this case, when a section parses through, we will return sections with
        all options that *were not* handled by some handler.

        For example, if we have this ``.ini`` file:

        .. code-block:: ini

            [SEC A]
            opt1: value1-A
            opt2: value2-A

            [SEC B]
            opt1: value1-B
            use 'SEC A'

            [SEC C]
            use 'SEC A'
            opt1: value1-C

        and we pull the ``SEC B`` data from it using, say, ``options("SEC B")``,
        the result we should expect is:

        .. code-block:: ini

            [SEC B]
            opt1: value1-A
            opt2: value2-A

        but if we loaded ``options("SEC C")`` then we should get:

        .. code-block:: ini

            [SEC C]
            opt1: value1-C
            opt2: value2-A

        Since the recursion of the ``use`` operations is a depth-first search, when there are
        entries with the same keys, then the 'last one visited' will win.

        When we parse a particular section, the result for a given
        section name is the union of all options in the transitive closure of the
        directed acyclic graph generated by the ``use`` operations. For example:

        .. code-block:: ini

            [SEC A]
            use 'SEC B'
            opt1: value1-A
            opt2: value2-A

            [SEC B]
            use 'SEC A'
            opt1: value1-B

        The results of ``options('SEC A')`` and ``options('SEC B)`` will be different:

            >>> options("SEC A")
            [SEC A]
            opt1: value1-A
            opt2: value2-A

            >>> options("SEC B")
            [SEC B]
            opt1: value1-B
            opt2: value1-A

        Note:
            This *MUST* be an inner class of :class:`~ConfigParserEnhanced` because it
            contains a 'hook' back to the instance of :class:`~ConfigParserEnhanced` in
            in which this entry exists. This allows us to access the owner's
            state so we can implement our lazy-evaluation and caching schemes. When
            an intance of :class:`ConfigParserEnhanced` accesses a section via the ``configparserenhanceddata``
            property, the parser will be invoked on this section to generate the result.
        """

        def __init__(self, owner=None):
            self._owner = owner
            self._set_owner_options()

        def __repr__(self):
            repr_entries = ["owner={}".format(self._owner), "data={}".format(self.data)]
            return "ConfigParserEnhancedData({})".format(", ".join(repr_entries))

        @property
        def data(self) -> dict:
            """
            """
            if not hasattr(self, '_data'):
                self._data = {}
            return self._data

        @data.setter
        def data(self, value) -> dict:
            """
            """
            if not isinstance(value, dict):
                raise TypeError("data must be a `dict` type.")
            self._data = value
            return self._data

        def items(self, section=None):
            """Iterator over all sections and their values in the ``.ini`` file.
            """
            section_list = self.keys()

            output = None
            if section is None:
                for sec_i in section_list:
                    self._parse_owner_section(sec_i)
                output = self.data.items()
            else:
                output = self.options(section).items()
            return output

        def keys(self):
            """
            Returns an iterable of sections in the ``.ini`` file.

            Returns:
                iterable object: containing the sections in the ``.ini`` file.
            """
            section_list = self.data.keys()

            if self._owner != None:
                section_list = self._owner.configparserdata.sections()

            return section_list

        def __iter__(self):
            for k in self.keys():
                yield k

        def __getitem__(self, key):
            if not self.has_section(key):
                raise KeyError(key)
            return self.data[key]

        def __len__(self) -> int:
            """
            Returns the # of sections in the ``.ini`` file.
            This will always be the total # of sections in the file as detected
            by ``ConfigParser``. We may or may not have them parsed at this time
            but accessing a given section via the ``[]`` or other means will cause
            it to be parsed at that time if it hasn't been yet.

            Returns:
                int: The number of sections in the .ini file.
            """
            return len(self.keys())

        def sections(self, parse=False):
            """
            Returns an iterable of sections in the ``.ini`` file.

            Args:
                parse (str,bool): Determines whether or not we will parse the sections
                    as well. This can be a string or a boolean type.

                    - ``False``: (default): Only returns the section names.
                    - ``True`` : Return the section names but also execute a parse of the sections.
                    - "force"  : Same as ``True`` but we *force* a (re)parse of all sections
                        even if they've already been parsed before.

            Returns:
                iterable object: containing the sections in the ``.ini`` file.
            """
            force_parse = False

            # Check the parameters.
            if not isinstance(parse, (bool, str)):
                raise TypeError("parse option must be a bool or str type.")
            if isinstance(parse, (str)):
                parse = parse.lower()
                force_parse = parse == "force"
                if parse != "force":
                    self.exception_control_event(
                        "CATASTROPHIC",
                        ValueError,
                        "`parse` should be a bool or a"
                        "string that is set to 'force'"
                    )

            if parse:
                for section in self.keys():
                    self._parse_owner_section(section, force_parse)
            return self.keys()

        def has_section(self, section) -> bool:
            """Checks if the section exists in the data.

            Returns:
                boolean: True if the section exists, False if otherwise.
            """
            if self._owner != None:
                # If this section exists...
                if self._owner.configparserdata.has_section(section):
                    # if we haven't already checked it then parse it.
                    if section not in self._sections_checked:
                        try:
                            self._parse_owner_section(section)
                        except KeyError:                                                       # pragma: no cover
                                                                                               # This might not be reachable.
                            self.exception_control_event(
                                "CATASTROPHIC",
                                KeyError,
                                "Reached 'unreachable' code? Please notify developers of this"
                            )

            return self.has_section_no_parse(section)

        def has_section_no_parse(self, section):
            """Check for existence of the section without parsing

            This will return True if the section exists or False if
            it does not. In this check, if the section does not exist
            the owner parser will NOT be invoked.

            Returns:
                boolean: True if the section exists in the data and
                    False if it does not.
            """
            return section in self.data.keys()

        def options(self, section):
            if not self.has_section(section):
                raise KeyError("Section {} does not exist.".format(section))
            return self.data[section]

        def has_option(self, section, option) -> bool:
            """
            """
            if self._owner != None:
                self._parse_owner_section(section)
            return (section in self.data.keys()) and (option in self.data[section].keys())

        def get(self, section, option=None):
            """
            Get a section/option pair, if it exists. If we have not
            parsed the section yet, we should run the parser to
            fully get the key data.
            """
            if self._owner != None and section not in self._sections_checked:
                self._parse_owner_section(section)

            if self.has_section(section):
                if option is None:
                    return self.data[section]
                elif self.has_option(section, option):
                    return self.data[section][option]
                else:
                    self.exception_control_event(
                        "CATASTROPHIC",
                        KeyError,
                        "Missing section:option -> '{}': '{}'".format(section, option)
                    )

            # This is not reachable with a bad section name
            # because the call to parse_owner_section(section) will
            # raise a KeyError if the section name is bad, and
            # the owner setter doesn't allow a NoneType to be assigned.
            # But if someone assigned None to self._owner directly
            # which Python won't prevent, we could get here... so
            # this check helps prevent one from doing bad things.
            raise KeyError("Missing section {}.".format(section))

        def add_section(self, section, force=False):
            """Add a new empty section.

            Adds a new empty section if an existing one does not
            already exist. We can override this and force the new
            section if we enable the ``force`` option.

            Args:
                section (str): The new section name.
                force (boolean): If True then we will FORCE the
                    new section to be added regardless of whether
                    or not this will overwrite an existing section.

            Returns:
                dict: A dictionary containing the new section added.
            """
            if (force) or (not self.has_section_no_parse(section)):
                self.data[section] = {}
            return self.data[section]

        def set(self, section, option, value):
            """
            Directly set an option. If the section is missing, we create an empty one.
            """
            if not self.has_section(section):
                self.add_section(section)

            # Note: We overwrite the option, even if it's already there.
            self.data[section][option] = value
            return self.data[section][option]

        # -------------------------------------
        #   H E L P E R S   ( P R I V A T E )
        # -------------------------------------

        @property
        def _owner(self):
            if not hasattr(self, '_owner_data'):
                self._owner_data = None
            return self._owner_data

        @_owner.setter
        def _owner(self, value):
            if not isinstance(value, (ConfigParserEnhanced)):
                raise TypeError("Owner class must be a ConfigParserEnhanced or derivitive.")
            self._owner_data = value
            return self._owner_data

        @property
        def _sections_checked(self):
            """
            Implements a set that contains section names that
            have already been parsed via lazy evaluation.
            """
            if not hasattr(self, '_sections_checked_data'):
                self._sections_checked_data = set()
            return self._sections_checked_data

        def _set_owner_options(self):
            """
            Get options from the owner class, if we have an owner class.

            Todo: Test what happens if self._owner == None
            """
            if self._owner != None:
                self.exception_control_level = self._owner.exception_control_level
                self.debug_level = self._owner.debug_level

            return

        def _parse_owner_section(self, section, force_parse=False):
            """Parse the section from the owner class.

            The ``force_parse`` parameter determins if we will perform a parse of the
            section even if it's already been parsed.

            Args:
                section (str): The section name of the section to parse.
                force_parse (bool,str): Determins if we should parse the section or not.

            Raises:
                TypeError: If the ``force_parse`` option is not a ``bool`` or ``str`` type.
            """
            # Check the parameters.
            if not isinstance(force_parse, (bool)):
                self.exception_control_event(
                    "CATASTROPHIC", TypeError, "`force_parse` must be a `bool` type."
                )

            if self._owner != None:

                do_parse_section = section not in self._sections_checked
                do_parse_section = do_parse_section or force_parse

                if do_parse_section:
                    self._set_owner_options()
                    self._sections_checked.add(section)
                    self._owner.parse_section(section)

            return
