#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
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
    William C. McLendon III
    Jason M. Gates
:Version: 0.1.3

"""
from __future__ import print_function

import configparser
import os
from pathlib import Path
import re
import sys

try:
    # @final decorator, requires Python 3.8.x
    from typing import final                                                                        # pragma: no cover
except ImportError:                                                                                 # pragma: no cover
    pass                                                                                            # pragma: no cover


from .Debuggable import Debuggable
from .ExceptionControl import ExceptionControl
from .HandlerParameters import HandlerParameters



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
    pass # Does this need to be implemented?



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
    def __init__(self, filename):
        """Constructor

        Args:
            filename (str,Path,list): The ``.ini`` file or files to be loaded. If a ``str``
                or ``Path`` is provided then we load only the one file. A ``list`` of strings
                or ``Path`` s can also be provided, which will be loaded by :class:`ConfigParser`'s
                `read() <https://docs.python.org/3/library/configparser.html#configparser.ConfigParser.read>`_
                method.
        """
        self.inifilepath = filename


    # -----------------------
    #   P R O P E R T I E S
    # -----------------------


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
        if not isinstance(value, (str,Path,list)):
            raise TypeError("ERROR: .ini filename must be a `str`, a `Path` or a `list` of either.")

        # If we have already loaded a .ini file, we should reset the data
        # structure. Delete any lazy-created properties, etc.
        if hasattr(self, '_inifilepath'):
            if hasattr(self, '_configparserdata'):
                delattr(self, '_configparserdata')
            if hasattr(self, '_loginfo'):
                delattr(self, '_loginfo')

        # Internally we represent the inifile as a `list of Path` objects.
        # Do the necessary conversions to make that so.
        if not isinstance(value, list):
            value = [ value ]

        self._inifilepath = []

        for entry in value:
            try:
                self._inifilepath.append( Path(entry) )
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
            self._configparserdata = configparser.ConfigParser(allow_no_value=True)

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
                    msg = "\n" + \
                          "+" + "="*78 + "+\n" + \
                          "|   ERROR: Unable to load configuration .ini file\n" + \
                          "|   - Requested file: `{}`\n".format(inifilepath_i) + \
                          "|   - CWD: `{}`\n".format(os.getcwd()) + \
                          "+" + "="*78 + "+\n"
                    raise IOError(msg)

            try:
                self._configparserdata.read(self.inifilepath, encoding='utf-8')
            except configparser.DuplicateOptionError as ex:
                delattr(self, '_configparserdata')
                message  = "ERROR: Configparser found a section with "
                message += "two options with identical keys."
                self.debug_message(0, message)
                raise ex

        return self._configparserdata


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


    # -------------------------------------
    #   P A R S E R   P U B L I C   A P I
    # -------------------------------------


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
        if not isinstance(section, str):
            raise TypeError("`section` must be a string type.")

        if section == "":
            raise ValueError("`section` cannot be empty.")

        # If a previous run generated _loginfo, clear it before this run.
        if hasattr(self, '_loginfo'):
            delattr(self, '_loginfo')

        result = self._parse_section_r(section, initialize=initialize, finalize=finalize)

        return result


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
        handler_name = handler_parameters.handler_name
        self.debug_message(1, "Enter handler    : {}".format(handler_name))                         # Console
        self.debug_message(1, "--> option       : {}".format(handler_parameters.raw_option))        # Console
        self.debug_message(2, "--> op_params    : {}".format(handler_parameters.op_params))         # Console
        self.debug_message(2, "--> data shared  : {}".format(handler_parameters.data_shared))       # Console
        self.debug_message(3, "--> data internal: {}".format(handler_parameters.data_shared))       # Console

        self._loginfo_add('handler-entry', {'name': handler_name,                                   # Logging
                                            'entry': handler_parameters.raw_option,                 # Logging
                                            'parameters': handler_parameters})                      # Logging
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
        handler_name = handler_parameters.handler_name
        self.debug_message(1, "Exit handler: {}".format(handler_name))                              # Console
        self._loginfo_add('handler-exit', {'name': handler_name,                                    # Logging
                                           'entry': handler_parameters.raw_option,                  # Logging
                                           'parameters': handler_parameters})                       # Logging
        return


    def handler_generic(self, section_name, handler_parameters) -> int:
        """Handler for non-operation ``key: value`` pairs.

        A generic handler that processes all *optons* in a ``.ini``
        file section that do not have an operation handler defined for them.

        Args:
            section_name (str): The name of the section being processed.
            handler_parameters (HandlerParameters): The parameters passed to
                the handler.

        Returns:
            int:
            * 0     : SUCCESS
            * [1-10]: Reserved for future use (WARNING)
            * > 10  : An unknown failure occurred (SERIOUS)
        """
        self.enter_handler(handler_parameters)
        self.debug_message(1, "--> option: {}".format(handler_parameters.raw_option))

        # -----[ Handler Content Start ]-------------------


        # -----[ Handler Content End ]---------------------

        self.exit_handler(handler_parameters)
        return 0


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
            * > 10  : An unknown failure occurred (SERIOUS)
        """
        self.enter_handler(handler_parameters)

        # -----[ Handler Content Start ]-------------------


        # -----[ Handler Content End ]---------------------

        self.exit_handler(handler_parameters)
        return 0


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
            * > 10  : An unknown failure occurred (SERIOUS)
        """
        self.enter_handler(handler_parameters)

        # -----[ Handler Content Start ]-------------------


        # -----[ Handler Content End ]---------------------

        self.exit_handler(handler_parameters)
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
        if section_name == None:
            raise TypeError("ERROR: a section name must not be None.")

        # Initialize handler_parameters if not currently set up.
        if handler_parameters is None:
            handler_parameters = self._new_handler_parameters()

            # check that we got the right data structure from _new_handler_parameters
            # in case someone overrides this later on.
            if not isinstance(handler_parameters, (HandlerParameters)):
                raise TypeError("handler_parameters must be of type `HandlerParameters` or a derivitive.")

            handler_parameters.section_root = section_name

            # Pitfall: Only add 'sections_checked' for the _root_ node
            #          because configparserenhanceddata recurses through and we
            #          want it's "meta section" to encapsulate the result
            #          of the fully parsed entry from the the root section
            #          of the search only.
            self.configparserenhanceddata._sections_checked.add(section_name)
        else:
            # if we got a handler_parameters handed to us (i.e., recursion)
            # we should make a new HandlerParameters object and copy references
            # of the parts that need to be updated by all levels of recursion
            # but not allow side-effects to modify the other entries that are
            # relevant to the caller's scope.
            handler_parameters = self._new_handler_parameters(handler_parameters)

        # Execute _handler_initialize to add a pre-processing step.
        if initialize and section_name == handler_parameters.section_root:
            handler_initialize_params = self._new_handler_parameters(handler_parameters)
            handler_initialize_params.handler_name = "handler_initialize"
            handler_rval = self.handler_initialize(section_name, handler_initialize_params)
            self._check_handler_rval("handler_initialize", handler_rval)

        self.debug_message(1, "Enter section: `{}`".format(section_name))                           # Console Logging
        self._loginfo_add('section-entry', {'name': section_name})                                  # Logging

        # Load the section from the configparser.ConfigParser data.
        current_section = None
        try:
            current_section = self.configparserdata[section_name]
        except KeyError:
            message = "ERROR: No section named `{}` was found in the configuration file {}.".format(section_name, self.inifilepath)
            raise KeyError(message)

        # Verify that we actually got a section returned. If not, raise a KeyError.
        if current_section is None:
            # This may be unreachable.
            raise Exception("ERROR: Unable to load section `{}` for an unknown reason.".format(section_name))

        # Initialize and set processed_sections.
        self._validate_handlerparameters(handler_parameters)
        handler_parameters.data_internal['processed_sections'].add(section_name)

        for sec_k,sec_v in current_section.items():
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

            handler_parameters.raw_option = (sec_k, sec_v) # Would it be better to add a key() property to handler_parameters in place of raw_option?
            handler_parameters.value = sec_v

            self.debug_message(2, "- Entry: `{}` : `{}`".format(sec_k, sec_v))                      # Console
            self._loginfo_add('section-key-value', {'key': sec_k, 'value': sec_v})                  # Logging

            # Extract the operation parameters (op1, op2) using the regex matcher.
            regex_op_splitter_m = self._regex_op_matcher(sec_k)

            # Initialze the handler return value.
            handler_rval = 0

            if regex_op_splitter_m is None:
                # Call generic_handler if the option key did not expand to an 'operation'.
                handler_rval = self._launch_handler_generic(section_name,
                                                            handler_parameters,
                                                            sec_k,
                                                            sec_v)

            else:
                # If we have a regex match, process the operation code and launch the
                # operation-specific handler if it exists or the generic handler if
                # it does not.

                self.debug_message(5, "regex-groups {}".format(regex_op_splitter_m.groups()))       # Console

                op1 = self._get_op1_from_regex_match(regex_op_splitter_m)
                op2 = self._get_op2_from_regex_match(regex_op_splitter_m)
                handler_parameters.op_params = (op1, op2)

                self._loginfo_add('section-operands', {'op1': op1, 'op2': op2})                     # Logging
                self.debug_message(2, "- op1: {}".format(op1))                                      # Console
                self.debug_message(2, "- op2: {}".format(op2))                                      # Console
                self.debug_message(2, "- val: {}".format(handler_parameters.value))                 # Console

                # Generate the handler name and check if we have one defined.
                handler_name,ophandler_f = self._locate_handler_method(op1)

                # Call the appropriate 'handler' for this entry.
                if ophandler_f is not None:
                    # Call the computed handler for the detected operation.
                    handler_parameters.handler_name = handler_name
                    handler_rval = ophandler_f(section_name, handler_parameters)
                else:
                    # Call generic_handler if no operation handler is found.
                    handler_rval = self._launch_handler_generic(section_name,
                                                                handler_parameters,
                                                                sec_k,
                                                                sec_v)

            # Check the return code from the handler.
            self._check_handler_rval(handler_parameters.handler_name, handler_rval)

        # If we're exiting recursion from the root node and and finalize is
        # enabled, we call the finalize handler.
        if finalize and section_name == handler_parameters.section_root:
            handler_finalize_params = self._new_handler_parameters(handler_parameters)
            handler_finalize_params.handler_name = "handler_finalize"
            handler_rval = self.handler_finalize(section_name, handler_finalize_params)
            self._check_handler_rval("handler_finalize", handler_rval)

        # Remove the section from the `processed_sections` field when we exit.
        # - This properly enables a true depth-first search of `use` links.
        self._validate_handlerparameters(handler_parameters)
        handler_parameters.data_internal['processed_sections'].remove(section_name)

        self._loginfo_add('section-exit', {'name': section_name})                                   # Logging
        self.debug_message(1, "Exit section: `{}`".format(section_name))                            # Console

        return handler_parameters.data_shared


    def _validate_handlerparameters(self, handler_parameters):
        """Check :class:`HandlerParameters`.

        Check the ``handler_parameters`` object that's being passed around
        to the handlers to verify that items in it have the proper types.

        Raises:
            TypeError: Raises a ``TypeError`` if
                ``handler_parameters.data_internal['processed_sections']`` is not a ``set``
                type.
        """
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
            new_handler_parameters.data_shared   = handler_parameters.data_shared
            new_handler_parameters.section_root  = handler_parameters.section_root

        return new_handler_parameters


    @property
    def _regex_op_splitter(self) -> re.Pattern:
        """Regular expression-based key splitter to op(param) pairs.

        This parameter stores the regex used to match operation lines in the parser.

        We provide this as a property in case a subclass needs to override it.

        **Warning: There be dragons here!**

        This is only something you should do if you **really** understand the
        core parser engine. If this is changed significantly, you will likely also
        need to override the following methods too:

        This function is tasked with generating the regular expression
        that parses out the *key* field of a ``configparser`` option
        into ``<operation> <parameter>`` fields that are used by *handlers*.

        * :meth:`~ConfigParserEnhanced.get_op1_from_regex_match()`
        * :meth:`~ConfigParserEnhanced.get_op2_from_regex_match()`
        * :meth:`~ConfigParserEnhanced.regex_op_matcher()`

        Returns:
            re.Pattern: A compiled regular expression pattern.

        Note:
            This should not be overridden unless you *really* know what you're
            doing since it'll probably also break the parser. Changing this could
            cascade into a lot of changes.

        See Also:
            - `regex tester <https://regexr.com/>` A useful REGEX tester.
        """
        if not hasattr(self, '_regex_op_splitter_value'):
            # This is the regex op splitter to extract op1 and op2.  This is
            # pretty complicated, so here are the details:
            # - The goal is to capture op1 and op2 into groups from a regex match.
            # - op1 will always be captured by group1. We only allow this to be letters,
            #   numbers, dashes, or underscores.
            #   - No spaces are ever allowed for op1 because this will get mapped to a
            #     handler method name of the form `_handler_{op1}()`
            # - op2 is captured by group 2 or 3
            #   - group2 if op2 is single-quoted (i.e., 'op 2' or 'op2' or 'op-2')
            #   - group3 if op2 is not quoted.
            # - op2 is just a string that gets passed down to the handler function
            #   so we will let this include spaces, but if you do include spaces it
            #   _must_ be single quoted otherwise we treat everything after the
            #   space as 'extra' stuff.
            #   - This 'extra' stuff is discarded by ConfigParserEnhanced so that
            #     it can be used to differentiate multiple commands in a section
            #     from one another that might otherwise map to the same key. Note,
            #     in a normal `ConfigParser` `.ini` file each section is a list of
            #     key:value pairs. The keys must be unique but that can be problematic
            #     if we're implementing a simple parsed language on top of it.
            #     For example, if we're setting envvars and wanted multiple entries for PATH:
            #
            #         envvar-prepend PATH: /something/to/prepend/to/path
            #         envvar-prepend PATH: /another/path/to/prepend
            #
            #     Here, the keys would be invalid for configparser because
            #     they're identical. By allowing 'extra' entries after op2
            #     we can allow a user to make each one unique. So our example
            #     above could be changed to:
            #
            #         envvar-prepend PATH A: /something/to/prepend/to/path
            #         envvar-prepend PATH B: /another/path/to/prepend
            #
            #     In both cases, op1 = 'envvar-prepend' and op2 = 'PATH' but the
            #     addition of the 'A' and 'B' will differentiate these keys from
            #     the ConfigParser's perspective.

            regex_string = r"^([\w\d\-_]+) *('([\w\d\-_ ]+)'|([\w\d\-_]+)(?: .*)*)?"
            #                  ^^^^^^^^^^    ^^^^^^^^^^^^^    ^^^^^^^^^^
            #                      \              \                \-- op2 : group 3
            #                       \              \--- op2 : group 2
            #                        \--- op1 : group 1
            #
            # Note: group 0 is the _full_ match
            #
            self._regex_op_splitter_value = re.compile(regex_string)

        return self._regex_op_splitter_value


    def _regex_op_matcher(self, text):
        """Execute the regex match operation for operations.

        Executes the regex match operation using the regex returned by
        :meth:`~ConfigParserEnhanced._regex_op_splitter`.

        This method adds the ability to add in extra checks for sanity
        that can be inserted into the parser. If the result of the match
        fails the extra scrutiny, then return None.

        Args:
            text (str): The string in which we're searching.

        Returns:
            re.Match: If one exists and we pass any sanity checks that are
            added to this method.
        """
        m = self._regex_op_splitter.match(text)

        # Sanity checks: Change match to None if we fail
        if m != None:
            if m.groups()[0] != text.split()[0]:
                m = None
        return m


    def _get_op1_from_regex_match(self, regex_match) -> str:
        """Extracts op1 from the regular expression match groups.

        Args:
            regex_match (re.Match): The regex match object.

        Returns:
            str: The op1 parameter, formatted properly for use
            as part of a handler name.

        Note:
            op1 must be a string that could be used in a method name, since this gets
            used by the parser to call a function of the pattern ``_handler_{op1}()``.
        """
        output = str(regex_match.groups()[0])
        output = output.strip()
        return output


    def _get_op2_from_regex_match(self, regex_match) -> str:
        """Extracts op2 from the regular expression match groups.

        Args:
            regex_match (re.Match): The regex match object.

        Returns:
            String containing the op2 parameter or None if one doesn't exist.
        """
        output = None

        # op2 matches group 2 or 3 depending on whether or not there were quotes.
        # (there are 4 groups)
        if regex_match.groups()[2]:
            output = str(regex_match.groups()[2]).strip()
        elif regex_match.groups()[3]:
            output = str(regex_match.groups()[3]).strip()

        return output


    def _locate_handler_method(self, operation) -> str:
        """Convert op1 to a handler name and get the reference to the handler.

        This method converts the *operation* parameter (op1) to a
        handler name and searches for the existence of a matching
        method.

        Handlers may be of the format: ``_handler_<operation>`` for
        internal/private handlers (that should not be overridden)
        or ``handler_<operation>`` for handlers that are considered
        fair game for subclasses to override and customize.

        Args:
            operation (str): The operation parameter that is converted to
                a proper handler name of the form ``_handler_{operation}()``
                or ``handler_{operation}()``.

        Returns:
            tuple: A tuple containing the ``(handler_name, handler_method)``.
            * ``handler_name`` is a string.
            * ``handler_method`` is either a reference to the handler method
              if it exists, or None if it does not exist.
        """
        if not isinstance(operation, (str)):
            # This is probably not reachable. Add a '# pragma: no cover' ?
            raise TypeError("op1 must be a string!")

        handler_name = operation
        handler_name = handler_name.replace('-','_')

        handler_name_private = "_handler_{}".format(handler_name)
        handler_name_public  = "handler_{}".format(handler_name)

        handler_private_f = getattr(self, handler_name_private, None)
        handler_public_f  = getattr(self, handler_name_public,  None)

        if (handler_private_f is not None) and (handler_public_f is not None):
            message  = "Ambiguous handler name."
            message += " Both `{}` and `{}` exist".format(handler_name_private, handler_name_public)
            message += " but only one is allowed."
            self.exception_control_event("SERIOUS", AmbiguousHandlerError, message)

        output = (None, None)
        if handler_private_f is not None:
            self.debug_message(5, "- Using _private_ handler: `{}`".format(handler_name_private))   # Console
            output = (handler_name_private, handler_private_f)
        elif handler_public_f is not None:
            self.debug_message(5, "- Using _public_ handler `{}`".format(handler_name_public))      # Console
            output = (handler_name_public, handler_public_f)
        else:
            self.debug_message(5, "- No handler found for operation `{}`".format(handler_name))     # Console

        return output


    def _check_handler_rval(self, handler_name, handler_rval):
        """Check the returned value from a handler.

        Args:
            handler_name (string): The name of the handler.
            handler_rval (int): The return value from a handler being processed.

        Raises:
            RuntimeError: If ``handler_rval > 0`` and the ``exception_control_level``
                is high enough, depending on the value of ``handler_rval``.
        """
        if handler_rval == 0:
            pass
        elif handler_rval <= 10:
            # These rvals are currently reserved. If someone uses it we should
            # throw a critical error to get the developers' attention to either
            # expand rval handling or users should use something > 10.
            self.exception_control_event("WARNING", RuntimeError,
                                         "Handler `{}` returned {}".format(handler_name, handler_rval))
        elif handler_rval > 10:
            self.exception_control_event("SERIOUS", RuntimeError,
                                         "Handler `{}` returned {}".format(handler_name, handler_rval))
        return


    def _launch_handler_generic(self, section_name, handler_parameters, sec_k, sec_v) -> int:
        """Launcher for ``handler_generic()``

        ``handler_generic()`` is called in two places inside the recursive parser.
        1. It is called when the ``key:value`` pair in an option does not parse out
           to ``operation`` and ``parameter`` fields.
        2. It is called when the ``key:value`` pair in an option does parse to
           an ``operation`` and a ``parameter`` field, but there are no handlers
           defined for the ``operation``.

        This helper just manages the call in both places so thay're done the same way.

        Returns:
            int: Returns the output value from ``handler_generic()``
        """
        output = 0

        self.configparserenhanceddata.set(handler_parameters.section_root, sec_k, sec_v)

        handler_parameters.handler_name = "handler_generic"
        output = self.handler_generic(section_name, handler_parameters)

        return output


    # ---------------------------------------
    #   H A N D L E R S   ( P R I V A T E )
    # ---------------------------------------


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
            * > 10  : An unknown failure occurred (SERIOUS)

        Todo:
            Once we can use Python 3.8 in our environments, we can use the @final decorator
            to mark this as something that should not be overridden. We also have to
            import it: `from typing import final`.
            https://stackoverflow.com/questions/321024/making-functions-non-override-able
        """
        entry        = handler_parameters.raw_option
        handler_name = handler_parameters.handler_name
        op1,op2      = handler_parameters.op_params

        self.enter_handler(handler_parameters)

        if op2 not in handler_parameters.data_internal['processed_sections']:
            self._parse_section_r(op2, handler_parameters, finalize=False)
        else:
            self._loginfo_add('cycle-detected', {'sec-src': section_name, 'sec-dst': op1})          # Logging
            self._loginfo_add('handler-exit', {'name': handler_name, 'entry': entry})               # Logging

            message  = "Detected a cycle in `use` dependencies in .ini file {}.\n".format(self.inifilepath)
            message += "- cannot load [{}] from [{}].".format(op2, section_name)
            self.exception_control_event("WARNING", ValueError, message)

        self.exit_handler(handler_parameters)
        return 0


    # -------------------------------------
    #   H E L P E R S   ( P R I V A T E )
    # -------------------------------------


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
            len_max_key  = 0
            for entry in self._loginfo:
                len_max_type = max(len_max_type, len(entry['type']))
                for k,v in entry.items():
                    len_max_key  = max(len_max_key, len(k))

            special_keys = ["type", "name"]

            for entry in self._loginfo:

                for key in special_keys:
                    if key in entry.keys():
                        line = ("--> " if key != special_keys[0] else "    ")
                        line += "{} : {} ".format(key.ljust(len_max_key), entry[key])
                        self.debug_message(1, line)

                for k,v in entry.items():
                    if k not in special_keys:
                        line = "--> {} : {}".format(k.ljust(len_max_key),v)
                        self.debug_message(1, line)
                self.debug_message(1, "")
        else:
            print(self._loginfo)

        return


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
            section_list = self.data.keys()
            if self._owner != None:
                section_list = self._owner.configparserdata.keys()

            output = None
            if section is None:
                for sec_i in section_list:
                    self._parse_owner_section(sec_i)
                output = self.data.items()
            else:
                output = self.options(section).items()
            return output


        def keys(self):
            return self.data.keys()


        def __iter__(self):
            for k in self.keys():
                yield k


        def __getitem__(self, key):
            if not self.has_section(key):
                raise KeyError(key)
            return self.data[key]


        def __len__(self):
            return len(self.data)


        def sections(self):
            return self.data.keys()


        def has_section(self, section):
            if self._owner != None and section not in self._sections_checked:
                try:
                    self._parse_owner_section(section)
                except KeyError:
                    pass
            return section in self.data.keys()


        def options(self, section):
            if not self.has_section(section):
                raise KeyError("Section {} does not exist.".format(section))
            return self.data[section]


        def has_option(self, section, option):
            """
            """
            if self._owner != None and section not in self._sections_checked:
                self._parse_owner_section(section)
            return option in self.data[section].keys()


        def get(self, section, option):
            """
            Get a section/option pair, if it exists. If we have not
            parsed the section yet, we should run the parser to
            fully get the key data.
            """
            if self._owner != None and section not in self._sections_checked:
                self._parse_owner_section(section)

            if self.has_section(section):
                if self.has_option(section, option):
                    return self.data[section][option]
                else:
                    raise KeyError("Missing section:option -> '{}': '{}'".format(section,option))

            # This is not reachable with a bad section name
            # because the call to parse_owner_section(section) will
            # raise a KeyError if the section name is bad, and
            # the owner setter doesn't allow a NoneType to be assigned.
            # But if someone assigned None to self._owner directly
            # which Python won't prevent, we could get here... so
            # this check helps prevent one from doing bad things.
            raise KeyError("Missing section {}.".format(section))


        def add_section(self, section):
            """
            Directly add a new section, if it does not exist.
            """
            if not self.has_section(section):
                self.data[section] = {}


        def set(self, section, option, value):
            """
            Directly set an option. If the section is missing, we create an empty one.
            """
            if not self.has_section(section):
                self.add_section(section)

            # Note: We overwrite the option, even if it's already there.
            self.data[section][option] = value
            return self.data[section][option]


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
            """
            if self._owner != None:
                self.exception_control_level = self._owner.exception_control_level
                self.debug_level = self._owner.debug_level


        def _parse_owner_section(self, section):
            """
            Parse the section from the owner class.
            """
            if self._owner != None:
                self._set_owner_options()
                self._sections_checked.add(section)
                self._owner.parse_section(section, initialize=False, finalize=False)
