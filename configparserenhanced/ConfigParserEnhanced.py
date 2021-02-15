#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
The ConfigParserEnhanced provides extended functionality for the `configparser`
module. This class enables configurable parsing of .ini files by splitting
the **key** portion of an option in a configuration section into an **operation**
and a **parameter**.  For example, given this .ini file:


.. code-block:: ini
    :linenos:

    [SECTION_NAME]
    key: value
    operation parameter: optional value
    operation parameter uniquestr: optional value

The built-in parser will process each OPTION (``key:value`` pairs)
in-order within a SECTION. During the parsing process we attempt to
split the *key* field into two pieces consisting of an *operation*
and a *parameter*.

If there is a **handler method** associated with the **operation**
field that is extracted then the parser will call that handler.
Handlers are added as methods named like ``_handler_<operation>()``
and will be called if they exist.  For example, if the **operation**
field resolves to ``use``, then the parser looks for a method called
``_handler_use()``.

If the handler exists, then it is invoked. Otherwise the parser treats
the OPTION field as a generic **key:value** pair as normal.

In this way, we can customize our processing by subclassing
ConfigParserEnhanced and defining our own handler methods.


:Authors:
    William C. McLendon III
:Version: 0.0.1-alpha

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



# ===================================
#  S U P P O R T   F U N C T I O N S
# ===================================



# ===============================
#   M A I N   C L A S S
# ===============================



class ConfigParserEnhanced(Debuggable, ExceptionControl):
    """An enhanced .ini file parser built using configparser.

    Provides an enhanced version of the ``configparser`` module which enables some
    extended processing of the information provided in a ``.ini`` file.

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
    def inifilepath(self) -> list:
        """list: provides access to the path to the .ini file (or files)

        inifilepath can be set to one of these things:
        1. a `str` contining a path to a .ini file.
        2. a `pathlib.Path` object pointing to a .ini file.
        3. a `list` of one or more of (1) or (2).

        entries in the list will be converted to pathlib.Path objects.

        Returns:
            A `list` containing the .ini files that will be processed.

        Note:
            Subclass(es) should not override this.
        """
        if not hasattr(self, '_inifilepath'):
            raise ValueError("ERROR: The filename has not been specified yet.")
        else:
            return self._inifilepath


    @inifilepath.setter
    def inifilepath(self, value) -> list:
        if not isinstance(value, (str,Path,list)):
            raise TypeError("ERROR: .ini filename must be a `str`, a `Path` or a `list` of either.")

        # if we have already loaded a .ini file, we should reset the data
        # structure. Delete any lazy-created properties, etc.
        if hasattr(self, '_inifilepath'):
            if hasattr(self, '_configdata'):
                delattr(self, '_configdata')
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
    def configdata(self) -> configparser.ConfigParser:
        """The raw results to a vanilla configparser processed .ini file.

        This property is lazy-evaluated and will be processed the first time it is
        accessed.

        Returns:
            configparser.ConfigParser object containing the contents of the configuration
            file that is loaded from a .ini file.

        Raises:
            ValueError if the length of `self.inifilepath` is zero.
            IOError if any of the files in `self.inifilepath` don't
                exist or are not files.

        Note:
            Subclass(es) should not override this.

        .. configparser reference:
            https://docs.python.org/3/library/configparser.html
        """
        if not hasattr(self, '_configdata'):
            self._configdata = configparser.ConfigParser(allow_no_value=True)

            # prevent ConfigParser from lowercasing the keys
            self._configdata.optionxform = str

            # configparser.ConfigParser.read() will not fail if it doesn't read the
            # .ini file(s) in the list, it'll just happily continue on and return
            # whatever it does get... or an empty configuration if no files were found.
            # We want to fail if we provide a bad file name so we need to check here.
            if len(self.inifilepath) == 0:
                raise ValueError("ERROR: No .ini filename(s) were provided.")

            for inifilepath_i in self.inifilepath:

                # Sanity type check here -- we'd throw on the .exists() and .is_file()
                # methods below if the entry isn't a Path object, but the erorr might
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

            self._configdata.read(self.inifilepath, encoding='utf-8')

        return self._configdata


    @property
    def configdata_parsed(self):
        """Enhanced configdata .ini file information (unhandled key-value pairs).

        This *property* returns a *parsed* representation of the configdata that would
        be loaded from our .ini file. The data in this will return the contents of a
        section plus its parsed results. For example, if we have this in our .ini
        file:

        .. code-block:: ini

            [SEC A]
            key A1: value A1

            [SEC B]
            use 'SEC A':
            key B1: value B1

        Extracting the data from 'SEC B' would result the contents of 'SEC B' + 'SEC A':

            >>> ConfigParserEnhancedObj.configdata_parsed["SEC B"]
            { 'key A1': 'value A1', 'key B1': 'value B1' }

        Returns:
            :class:`~configparserenhanced.ConfigParserEnhanced.ConfigParserEnhancedData`

        Note:
            Subclass(es) should not override this.
        """
        if not hasattr(self, '_configdata_parsed'):
            self._configdata_parsed = self.ConfigParserEnhancedData(owner=self)
        return self._configdata_parsed


    # --------------------
    #   P A R S E R
    # --------------------


    def new_handler_parameters(self) -> HandlerParameters:
        """Generate a new :class:`~configparserenhanced.HandlerParameters` object.

        This is called inside the parser to generate HandlerParameters.
        If subclasses extend the :class:`~configparserenhanced.HandlerParameters`
        class, this can be overridden.

        Returns:
            :class:`~configparserenhanced.HandlerParameters` object.
        """
        params = HandlerParameters()
        return params


    @property
    def regex_op_splitter(self) -> re.Pattern:
        """re.Pattern: Regular expression based key splitter to op(param) pairs.

        This parameter stores the regex used to match operation lines in the parser.

        We provide this as a property in case a subclass needs to override it.

        Warning: There be dragons here!
        This is only something you should do if you _really_ understand the
        core parser engine. If this is changed significantly, you will likely also
        need to override the following methods too:

        * :meth:`~ConfigParserEnhanced.get_op1_from_regex_match()`
        * :meth:`~ConfigParserEnhanced.get_op2_from_regex_match()`
        * :meth:`~ConfigParserEnhanced.regex_op_matcher()`

        Returns:
            re.Pattern: A compiled regular expression pattern.

        Note:
            This should not be overridden unless you _really_ know what you're
            doing since it'll probably also break the parser. Changing this could
            cascade into a lot of changes.
        """
        if not hasattr(self, '_regex_op_splitter'):
            # regex op splitter to extract op1 and op2, this is pretty complicated so here's the
            # deets:
            # - The goal is to capture op1 and op2 into groups from a regex match.
            # - op1 will always be captured by group1. We only allow this to be letters,
            #   numbers, dashes, or underscores.
            #   - No spaces are ever allowed for op1 because this will get mapped to a handler method
            #     name of the form `_handler_{op1}()`
            # - op2 is captured by group 2 or 3
            #   - group2 if op2 is single-quoted (i.e., 'op 2' or 'op2' or 'op-2')
            #   - group3 if op2 is not quoted.
            # - op2 is just a string that gets passed down to the handler function so we will
            #   let this include spaces, but if you do include spaces it _must_ be single quoted
            #   otherwise we treat everything after the space as 'extra' stuff.
            #   - This 'extra' stuff is discarded by ConfigParserEnhanced so that it can be used
            #     to differentiate multiple commands in a section from one another that might otherwise
            #     map to the same key. Note, in a normal `configparser` `.ini` file each section is
            #     a list of key:value pairs. The keys must be unique but that can be problematic
            #     if we're implementing a simple parsed language on top of it.
            #     For example, if we're setting envvars and wanted multiple entries for PATH:
            #         envvar-prepend PATH: /something/to/prepend/to/path
            #         envvar-prepend PATH: /another/path/to/prepend
            #     Here, the keys would be invalid for configparser because they're identical.
            #     By allowing 'extra' entries after op2 we can allow a user to make each one unique.
            #     So our example above could be changed to:
            #         envvar-prepend PATH A: /something/to/prepend/to/path
            #         envvar-prepend PATH B: /another/path/to/prepend
            #     In both cases, op1 = 'envvar-prepend' and op2 = 'PATH' but the addition of the
            #     'A' and 'B' will differentiate these keys from the configparser's perspective.
            #  - Note: This comment information should find its way into the docs sometime.
            # regex_string = r"^([\w\d\-_]+)( '([\w\d\-_ ]+)'| ([\w\d\-_]+)(?: .*)*)?"   # (old and busted)
            regex_string = r"^([\w\d\-_]+) ?('([\w\d\-_ ]+)'|([\w\d\-_]+)(?: .*)*)?"
            #                  ^^^^^^^^^^    ^^^^^^^^^^^^^    ^^^^^^^^^^
            #                      \              \                \-- op3 : group 3
            #                       \              \--- op2 : group 2
            #                        \--- op1 : group 1
            self._regex_op_splitter = re.compile(regex_string)

        return self._regex_op_splitter


    def regex_op_matcher(self, text):
        """Execute the regex match operation for operations.

        Executes the regex match operation using the regex returned by
        :class:`~ConfigParserEnhanced.regex_op_splitter`.

        This method adds the ability to add in extra checks for sanity
        that can be inserted into the parser. If the results of the match
        fails the extra scrutiny, then return None.

        Args:
            text (str): The string in which we're searching.

        Returns:
            Regex match if one exists and we pass any sanity checks that are
            added to this method.
        """
        m = self.regex_op_splitter.match(text)

        # Sanity checks: Change match to None if we fail
        if m != None:
            if m.groups()[0] != text.split()[0]:
                m = None
        return m


    def get_op1_from_regex_match(self, regex_match) -> str:
        """Extracts op1 from the regular expression match groups.

        Args:
            regex_match (object): A `re.match()` object.

        Returns:
            String containing the op1 parameter, formatted properly for use
            as part of a handler name.

        Note:
            op1 must be a string that could be used in a method name since this gets
            used by the parser to call a function of the pattern `_handler_{op1}`
        """
        output = str(regex_match.groups()[0])
        output = output.strip()
        output = output.replace('-','_')
        return output


    def get_op2_from_regex_match(self, regex_match) -> str:
        """Extracts op2 from the regular expression match groups.

        Args:
            regex_match (object): A `re.match()` object.

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


    def parse_configuration(self, section):
        """Execute parser operations for the provided *section*.

        Args:
            section (str): The section name that will be parsed and retrieved.

        Returns:
            :attr:`~.HandlerParameters.data_shared` property from :class:`~.HandlerParameters`.
        """
        if not isinstance(section, str):
            raise TypeError("`section` must be a string type.")

        if section == "":
            raise ValueError("`section` cannot be empty.")

        # clear out loginfo from any previous run(s)
        if hasattr(self, '_loginfo'):
            delattr(self, '_loginfo')

        result = self._parse_configuration_r(section)

        return result


    def _parse_configuration_r(self, section_name, handler_parameters=None):
        """Recursive driver of the parser.

        Args:
            section_name (str):
            handler_parameters (object):

        Returns:
            :attr:`~HandlerParameters.data_shared`
        """
        if section_name == None:
            raise TypeError("ERROR: a section name must not be None.")

        # initialize handler_parameters if not currently set up.
        if handler_parameters is None:
            handler_parameters = self.new_handler_parameters()

            if not isinstance(handler_parameters, (HandlerParameters)):
                raise TypeError("handler_parameters must be `HandlerParameters` or a derivitive.")

            handler_parameters.section_root = section_name
            handler_parameters.data_shared      # initializes default (lazy eval, not necessary)
            handler_parameters.data_internal    # initializes default (lazy eval, not necessary)
            handler_parameters.data_internal['processed_sections'] = set()                          # SCAFFOLDING (future use)

            # Pitfall: Only add 'sections_checked' for the _root_ node
            #          because configdata_parsed recurses through and we
            #          want it's "meta section" to encapsulate the result
            #          of the fully parsed entry from the the root section
            #          of the search only.
            self.configdata_parsed.sections_checked.add(section_name)

        self.debug_message(1, "Enter section: `{}`".format(section_name))                           # Console Logging
        self._loginfo_add('section-entry', {'name': section_name})                                  # Logging

        # Load the section from the configparser.ConfigParser data.
        current_section = None
        try:
            current_section = self.configdata[section_name]
        except KeyError:
            message = "ERROR: No section named `{}` was found in the configuration file.".format(section_name)
            raise KeyError(message)

        # Verify that we actually got a section returned. If not, raise a KeyError.
        # - Might not be reachable but let's keep this in place for now.
        if current_section is None:
            raise Exception("ERROR: Unable to load section `{}` for unknown reason.".format(section_name))

        # Initialize and set processed_sections
        handler_parameters.data_internal['processed_sections'].add(section_name)

        for sec_k,sec_v in current_section.items():
            sec_k = str(sec_k).strip()
            sec_v = str(sec_v).strip()
            sec_v = sec_v.strip('"')
            handler_parameters.raw_option = (sec_k, sec_v)

            self.debug_message(2, "- Entry: `{}` : `{}`".format(sec_k, sec_v))                      # Console
            self._loginfo_add('section-key-value', {'key': sec_k, 'value': sec_v})                  # Logging

            # Extract operation parameters (op1, op2) using the regex matcher
            regex_op_splitter_m = self.regex_op_matcher(sec_k)

            # initialze handler return value.
            handler_rval = 0

            if regex_op_splitter_m is None:
                # Call the generic handler if the key:value pair fails to produce a regex match.

                self.debug_message(5, "Option regex did not find 'operation(s)'.")                  # Console
                handler_rval = self._handler_generic(section_name, handler_parameters)

            else:
                # If we have a regex match, process the operation code and launch the
                # operation-specific handler if it exists or the generic handler if
                # it does not.

                self.debug_message(5, "regex-groups {}".format(regex_op_splitter_m.groups()))       # Console

                op1 = self.get_op1_from_regex_match(regex_op_splitter_m)
                op2 = self.get_op2_from_regex_match(regex_op_splitter_m)
                handler_parameters.op_params  = (op1,   op2)

                self._loginfo_add('section-operands', {'op1': op1, 'op2': op2})                     # Logging
                self.debug_message(2, "- op1: {}".format(op1))                                      # Console
                self.debug_message(2, "- op2: {}".format(op2))                                      # Console

                # Generate handler name and check if we have one defined.
                handler_name = "_handler_{}".format(op1)
                ophandler_f = getattr(self, handler_name, None)

                # Call the appropriate 'handler' for this entry.
                if ophandler_f is not None:
                    # Call the computed handler for the detected operation.
                    handler_rval = ophandler_f(section_name, handler_parameters)
                else:
                    # Call the generic handler to update the 'generic' view
                    # of the (all key:value pairs that don't map to any other handlers)
                    handler_rval = self._handler_generic(section_name, handler_parameters)

            # Check the return code from the handler
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


        # Remove the section from the `processed_sections` field when we exit.
        # - This properly enables a true DFS of `use` links.
        handler_parameters.data_internal['processed_sections'].remove(section_name)

        self._loginfo_add('section-exit', {'name': section_name})                                   # Logging
        self.debug_message(1, "Exit section: `{}`".format(section_name))                            # Console

        return handler_parameters.data_shared


    # --------------------
    #   H A N D L E R S
    # --------------------


    def _handler_generic(self, section_name, handler_parameters) -> int:
        """
        A generic handler - this handler processes all _optons_ in a .ini
        file section that do not have an operation handler defined for them.

        Returns:
            integer value
                0     : SUCCESS
                [1-10]: Reserved for future use (WARNING)
                > 10  : An unknown failure occurred (SERIOUS)

        Note:
            This handler implements a 'last one wins' strategy for handling
            key naming conflicts. We simply overrwite the existing key in
            ``configdata_parsed`` when conflicts occur. If one wanted to
            raise an excpetion on a key conflcit we'd need to override this
            method and add that.
        """
        entry        = handler_parameters.raw_option
        section_root = handler_parameters.section_root

        self.debug_message(1, "Enter handler: _handler_generic")                                    # Console
        self.debug_message(1, "--> option: {}".format(handler_parameters.raw_option))               # Console
        self._loginfo_add('handler-entry', {'name': '_handler_generic', 'entry': entry})            # Logging

        # Note: this generic handler implements a 'last one wins' strategy for
        #       handling

        self.configdata_parsed.set(section_root, entry[0], entry[1])

        self.debug_message(1, "Exit handler: _handler_generic")                                     # Console
        self._loginfo_add('handler-exit', {'name': '_handler_generic', 'entry': entry})             # Logging
        return 0


    def _handler_use(self, section_name, handler_parameters) -> int:
        """
        This is a handler that will get executed when we detect a `use` operation in
        our parser.

        Args:
            section_name (str): The section name of the current _section_ we're processing.
            op1 (str): The first operation parameter
                       (i.e., `use` if the full key is `use section_name`)
            op2 (str): The second operation parameter
                       (i.e., `section_name` if the full key is `use section_name`)

        Returns:
            integer value
                0     : QAPLA'
                [1-10]: Reserved for future use (WARNING)
                > 10  : An unknown failure occurred (SERIOUS)

        Todo:
            Once we can use Python 3.8 in our environments, we can use the @final decorator
            to mark this as something that should not be overridden. We also have to
            import it: `from typing import final`

        See Also:
            https://stackoverflow.com/questions/321024/making-functions-non-override-able
        """
        op1,op2 = handler_parameters.op_params
        entry   = handler_parameters.raw_option

        self._loginfo_add('handler-entry', {'name': '_handler_use', 'entry': entry})                # Logging
        self.debug_message(1, "Enter handler: _handler_use ({} -> {})".format(section_name, op2))   # Console

        if op2 not in handler_parameters.data_internal['processed_sections']:
            self._parse_configuration_r(op2, handler_parameters)
        else:
            self._loginfo_add('cycle-detected', {'sec-src': section_name, 'sec-dst': op1})          # Logging
            self._loginfo_add('handler-exit', {'name': '_handler_use', 'entry': entry})             # Logging

            message  = "Detected a cycle in `use` dependencies in .ini file.\n"
            message += "- cannot load [{}] from [{}].".format(op2, section_name)
            self.exception_control_event("WARNING", ValueError, message)

            return 0

        self._loginfo_add('handler-exit', {'name': '_handler_use', 'entry': entry})                 # Logging
        self.debug_message(1, "Exit handler: _handler_use ({} -> {})".format(section_name, op2))    # Console
        return 0


    # --------------------
    #   L O G I N F O
    # --------------------


    def _loginfo_add(self, typeinfo, entry) -> None:
        """
        If in debug mode, we can use this to log operations.
        Appends to _loginfo

        Args:
            typeinfo (str): What kind of operation is this. This generates the
                           'type' entry in the loginfo dict. (Required)
            entry (dict): A dictionary containing log information that we're appending.
                          At minimum it should have: `type: typestring`.

        Returns:
            Nothing


        Todo:
            Once we can use Python 3.8 in our environments, we can use the @final decorator
            to mark this as something that should not be overridden. We also have to
            import it: `from typing import final`

        See Also:
            https://stackoverflow.com/questions/321024/making-functions-non-override-able
        """
        if not hasattr(self, '_loginfo'):
            self._loginfo = []

        if self.debug_level > 0:
            if not isinstance(entry, dict):
                raise TypeError("entry should be a dictionary type.")
            entry['type'] = typeinfo

            self._loginfo.append(entry)
        else:
            pass
        return


    def _loginfo_print(self, pretty=True) -> None:
        """
        This is a helper to pretty-print the loginfo object

        Todo:
            Once we can use Python 3.8 in our environments, we can use the @final decorator
            to mark this as something that should not be overridden. We also have to
            import it: `from typing import final`

        See Also:
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
                        if key != special_keys[0]:
                            line = "--> {} : {} ".format(key.ljust(len_max_key), entry[key])
                        else:
                            line = "{} : {} ".format(key.ljust(len_max_key+4), entry[key])
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
    #  I N N E R   C L A S S E S
    # ===========================================================


    class ConfigParserEnhancedData(Debuggable, ExceptionControl):
        """ConfigParserEnhancedData

        This class is intended to serve as a *lite* analog to
        ``configparser.ConfigParser`` to provide a similar result but with
        the :class:`~ConfigParserEnhanced` class's ability to parse .ini files and
        follow entries that implement a ``use <section name>:`` rule. In
        this case, when a section parses through we will return sections with
        all options that *were not* handled by some handler.

        For example, if we have this .ini file:

        .. code-block:: ini

            [SEC A]
            opt1: value1-A
            opt2: value2-A

            [SEC B]
            opt1: value1-B
            use 'SEC A':

            [SEC C]
            use 'SEC A':
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
            opt2: value1-A

        Since the recursion of the ``use`` operations is a DFS, when there are
        entries with the same keys, then the 'last one visited' will win.

        When we parse a particular section this object the result for a given
        section name is union of all options in the transitive closure of the
        DAG generated by the `use` operations. For example:

        .. code-block:: ini

            [SEC A]
            use 'SEC B'
            opt1: value1-A
            opt2: value2-A

            [SEC B]
            use 'SEC A':
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
            This _MUST_ be an inner class of :class:`~ConfigParserEnhanced` because it
            contains a 'hook' back to the instance of :class:`~ConfigParserEnhanced` in
            in which this entry exists. This allows us to access the owner's
            state so we can implement our lazy-evaluation and caching schemes. When
            an intance of ConfigParserEnhanced accesses a section via the ``configdata_parsed``
            property, the parser will be invoked on this section to generate the result.
        """
        def __init__(self, owner=None):
            self.owner = owner
            self.set_owner_options()


        @property
        def owner(self):
            if not hasattr(self, '_owner'):
                self._owner = None
            return self._owner


        @owner.setter
        def owner(self, value):
            if not isinstance(value, (ConfigParserEnhanced)):
                raise TypeError("Owner class must be a ConfigParserEnhanced or derivitive.")
            self._owner = value
            return self._owner


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


        @property
        def sections_checked(self):
            """
            Implements a set that contains section names that
            have already been parsed via lazy evaluation.
            """
            if not hasattr(self, '_sections_checked'):
                self._sections_checked = set()
            return self._sections_checked


        def set_owner_options(self):
            """
            Get options from the owner class, if we have an owner class.
            """
            if self.owner != None:
                self.exception_control_level = self.owner.exception_control_level
                self.debug_level = self.owner.debug_level


        def items(self, section=None):
            section_list = self.data.keys()
            if self.owner != None:
                section_list = self.owner.configdata.keys()

            output = None
            if section is None:
                for seci in section_list:
                    self.parse_owner_section(seci)
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
            if self.owner != None and section not in self.sections_checked:
                try:
                    self.parse_owner_section(section)
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
            if self.owner != None and section not in self.sections_checked:
                self.parse_owner_section(section)
            return option in self.data[section].keys()


        def get(self, section, option):
            """
            Get a section/option pair if it exists. If we have not
            parsed the section yet, we should run the parser to
            fully get the key data.
            """
            if self.owner != None and section not in self.sections_checked:
                self.parse_owner_section(section)

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
            Directly set an option. If the section is missing we create an empty one.
            """
            if not self.has_section(section):
                self.add_section(section)

            # Note: we overwrite the option, even if it's already there.
            self.data[section][option] = value
            return self.data[section][option]


        def parse_owner_section(self, section):
            """
            Parse the section from the owner class
            """
            if self.owner != None:
                self.set_owner_options()
                self.sections_checked.add(section)
                self.owner.parse_configuration(section)



# EOF
