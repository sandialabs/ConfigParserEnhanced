====================================
ConfigParserEnhanced Class Reference
====================================
The ConfigParserEnhanced provides extended functionality for the `configparser`
module. This class attempts to satisfy the following goals:

1. Provide a framework to embed extended 'parsing' into ``Config.ini`` style files.
2. Enable chaining of ``[SECTIONS]`` within a single .ini file which
   using the parsing capability noted in (1).
3. Provide an *extensible* capability. We intend ConfigParserEnhanced to be
   used as a base class for other tools so that subclasses can add additional
   handlers for new 'operations' which can be used by the parser.

.. note:: ConfigParser SECTION entries are stored as a dict.

    Because ConfigParser treats OPTIONS as dictionary objects
    storing ``{ key: value }`` entries the KEY fields must be
    unique within a SECTION or ConfigParser will raise a KeyError
    exception.

    This is why the default behaviour of the parser is to partition
    keys into a thruple: ``<operation> <parameter> <everything else>:``
    where ``<everything else>`` can be used to uniqueify the overall
    OPTION field.


Extending through Inheritance
-----------------------------

    One example of how we might extend ConfigParserEnhanced to add an
    operation that might prepend to an environment variable could be
    this. Say we wish to prepend to the PATH envvar by adding a new
    *operation* called ``envvar-prepend`` that might be invoked in this
    ``.ini`` snippet:

    .. code-block:: ini
        :linenos:

        [SET_PATH_VARS]
        envvar-prepend PATH A: /some/new/path
        envvar-prepend PATH B: /another/path/to/prepend/to/PATH

    ConfigParserEnhanced will identify an *operation* ``envvar-prepend``
    with a parameter ``PATH``. It will then look for a method called
    `_handler_envvar_prepend()` to handle the operation:

    .. code-block:: python
        :linenos:

        def _handler_envvar_prepend(self, section_name, handler_parameters) -> int:
            op1,op2 = handler_parameters.op_params
            if op1 in os.environ.keys():
                envvar_new = ":".join([
                    op2,
                    os.environ[op1]
                ])
            os.environ[op1] = envvar_new
            return 0

    The strings "A" and "B" on lines 2 and 3 of the .ini file are solely
    used to uniqueify the entries within the section ``SET_PATH_VARS``.


API Documentation
-----------------

ConfigParserEnhanced
++++++++++++++++++++
.. automodule:: configparserenhanced.ConfigParserEnhanced
   :no-members:

Public Methods
~~~~~~~~~~~~~~
.. autoclass:: configparserenhanced.ConfigParserEnhanced
   :noindex:
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: ConfigParserEnhancedData
   :special-members: __init__


Handlers (Private)
~~~~~~~~~~~~~~~~~~
These handlers defined by ConfigParserEnhanced and should not
be overridden.

.. automethod:: configparserenhanced.ConfigParserEnhanced._handler_use
.. automethod:: configparserenhanced.ConfigParserEnhanced._handler_generic
.. automethod:: configparserenhanced.ConfigParserEnhanced._handler_finalize


Helpers (Private)
~~~~~~~~~~~~~~~~~

.. automethod:: configparserenhanced.ConfigParserEnhanced._loginfo_add
.. automethod:: configparserenhanced.ConfigParserEnhanced._loginfo_print


ConfigParserEnhancedData
~~~~~~~~~~~~~~~~~~~~~~~~
.. autoclass:: configparserenhanced::ConfigParserEnhanced.ConfigParserEnhancedData
   :members:
   :undoc-members:
   :show-inheritance:


