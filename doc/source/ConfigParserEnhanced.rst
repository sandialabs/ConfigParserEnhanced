====================================
ConfigParserEnhanced Class Reference
====================================

ConfigParserEnhanced provides extended functionality for the
`ConfigParser <https://docs.python.org/3/library/configparser.html>`_ module.
This class attempts to satisfy the following goals:

1. Provide an extended "parsing" capability in ``.ini`` style files by allowing
   the construction of *handlers* that can be triggered by specially formatted
   *options* to provide enhanced parsing capabilities for ``.ini`` files.
2. Enable chaining of ``[SECTIONS]`` within a single ``.ini`` file
   using the parsing capability noted in (1).
3. Provide an *extensible* capability.
   We intend :class:`~configparserenhanced.ConfigParserEnhanced` to be
   used as a base class for other tools so that subclasses can add
   additional handlers for new 'operations' which can be used by the
   parser.

.. note:: :class:`ConfigParser` SECTION entries are stored as a ``dict``.

    Because :class:`ConfigParser` treats OPTIONS as dictionary objects
    storing ``{ key: value }`` entries, the KEY fields must be
    unique within a SECTION or :class:`ConfigParser` will raise a ``KeyError``
    exception.

    This is why the default behavior of the parser is to partition
    keys into three parts: ``<operation> <parameter> <everything else>:``
    where ``<everything else>`` can be used to 'uniqueify' the overall
    OPTION field.



Normalization of Fields
=======================

Internally, the parser will apply a normalization transform to the
**operation** and the **parameter** fields.

The following operations are applied to the **operation** field:

- Replace occurrences of ``-`` with ``_``.



Extending through Inheritance
=============================

One example of how we might extend :class:`configparserenhanced.ConfigParserEnhanced`
to add an operation that might prepend to an environment variable could be
the following. Say we wish to prepend to the ``PATH`` environment variable
by adding a new *operation* called ``envvar-prepend`` that might be invoked
in this ``.ini`` snippet:

.. code-block:: ini
    :linenos:

    [SET_PATH_VARS]
    envvar-prepend PATH A: /some/new/path
    envvar-prepend PATH B: /another/path/to/prepend/to/PATH

:class:`~configparserenhanced.ConfigParserEnhanced` will identify an *operation* ``envvar-prepend``
with a parameter ``PATH``. It will then look for a method called
:meth:`_handler_envvar_prepend()` to handle the operation:

.. code-block:: python
    :linenos:

    def _handler_envvar_prepend(self, section_name, handler_parameters) -> int:
        op1,op2 = handler_parameters.op_params
        envvar_new = op2 # I think this was missing (if the envvar doesn't exist yet).  Is this right?
        if op1 in os.environ.keys():
            envvar_new = ":".join([
                op2,
                os.environ[op1]
            ])
        os.environ[op1] = envvar_new
        return 0

The strings "A" and "B" on lines 2 and 3 of the ``.ini`` file are solely
used to uniqueify the entries within the section ``SET_PATH_VARS``.


Dealing with DEFAULT sections
=============================
The underlying ``ConfigParser`` instance inside :class:`configparserenhanced.ConfigParserEnhanced`
has a notion of a special *default* section that it can process. The name of this section can be
changed but it defaults to "DEFAULT".

Normally, the contents of DEFAULT are prepended to *every section* that is read by ConfigParser.
This is a problem for ConfigParserEnhanced because the contents of this section will be re-applied
to a sections content *every time* a ``use`` operation is encountered because ``use`` triggers
the loading of a new section. When this happens, any values from the default section that had been
changed will be re-set to their original values. This is not something we want, but it is useful to
keep the concept of a "DEFAULT" section.

We implement this by changing the default section name for the internal ConfigParser object to
a new value: ``CONFIGPARSERENHANCED_COMMON``.  Generally speaking, one should not include this
in their .ini files for the reasons already presented. The name of this is controlled by the
new property :attr:`_internal_default_section_name`.

To include the original concept of a default section we have another property called
:attr:`default_section_name` which defaults to "DEFAULT". This section is processed once
at the start of parsing a new section and provides a behaviour that should be familiar
to users of ConfigParser.


API Documentation
=================

ConfigParserEnhanced
++++++++++++++++++++
.. automodule:: configparserenhanced.ConfigParserEnhanced
   :no-members:


Public Interface
~~~~~~~~~~~~~~~~
.. autoclass:: configparserenhanced.ConfigParserEnhanced
   :noindex:
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: ConfigParserEnhancedData,handler_initialize,handler_finalize
   :special-members: __init__


Operation Handlers (Public)
~~~~~~~~~~~~~~~~~~~~~~~~~~~
These handlers are defined by :class:`~configparserenhanced.ConfigParserEnhanced` and *may be overridden by
subclasses* to specialize parser behaviour. If you wish to do so, we recommend
cutting and pasting the default handlers into your code and customizing from
there.

.. automethod:: configparserenhanced.ConfigParserEnhanced.handler_initialize
.. automethod:: configparserenhanced.ConfigParserEnhanced.handler_finalize
.. automethod:: configparserenhanced.ConfigParserEnhanced._generic_option_handler


Operation Handlers (Private)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
These handlers perform tasks internal to :class:`~configparserenhanced.ConfigParserEnhanced` and should
not be overridden.

.. automethod:: configparserenhanced.ConfigParserEnhanced._handler_use


Parser Helpers (Private)
~~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: configparserenhanced.ConfigParserEnhanced._parse_section_r

.. automethod:: configparserenhanced.ConfigParserEnhanced._apply_transformation_to_operation
.. automethod:: configparserenhanced.ConfigParserEnhanced._apply_transformation_to_parameter

.. automethod:: configparserenhanced.ConfigParserEnhanced._new_handler_parameters
.. automethod:: configparserenhanced.ConfigParserEnhanced._validate_handlerparameters

.. automethod:: configparserenhanced.ConfigParserEnhanced._check_handler_rval
.. automethod:: configparserenhanced.ConfigParserEnhanced._launch_generic_option_handler
.. automethod:: configparserenhanced.ConfigParserEnhanced._locate_class_method
.. automethod:: configparserenhanced.ConfigParserEnhanced._locate_handler_method


Private Methods
~~~~~~~~~~~~~~~
.. automethod:: configparserenhanced.ConfigParserEnhanced._loginfo_add
.. automethod:: configparserenhanced.ConfigParserEnhanced._loginfo_print



Inner Classes
~~~~~~~~~~~~~


ConfigParserEnhancedData
++++++++++++++++++++++++
:class:`~configparserenhanced.ConfigParserEnhanced.ConfigParserEnhancedData` is
an *inner class* of :class:`~configparserenhanced.ConfigParserEnhanced` that
behaves somewhat like a partial implementation of a :class:`ConfigParser`
object that is customized to work in concert with
:class:`~configparserenhanced.ConfigParserEnhanced`.

This class operates using lazy-evaluation of the parser method in
:class:`~configparserenhanced.ConfigParserEnhanced` to process sections when requested.

The following table shows the main API and implementation differences
between a :class:`~configparserenhanced.ConfigParserEnhanced.ConfigParserEnhancedData`
object and a :class:`ConfigParser` object, illustrating what subset of features
a :class:`~configparserenhanced.ConfigParserEnhanced.ConfigParserEnhancedData`
object provides:

.. csv-table:: ConfigParserEnhancedData Comparison
   :file: tbl_configparserenhanceddata_comparison.csv
   :header-rows: 1
   :widths: 60,20,20
   :align: center
   :delim: |

Public Interface
~~~~~~~~~~~~~~~~
.. autoclass:: configparserenhanced::ConfigParserEnhanced.ConfigParserEnhancedData
   :members:
   :undoc-members:
   :show-inheritance:


ConfigParserEnhanced and ConfigParser Differences
=================================================
There are some differences between ConfigParser and ConfigParserEnhanced
that are worthwhile to note:

1. ``ConfigParser.keys()`` and ``ConfigParserEnhancedData.keys()`` work slightly differently:
    - ``ConfigParser.keys()`` will return a ``KeyView`` object that when iterated will
      include the ``DEFAULT`` section even if it's not present in the .ini file.
    - ``ConfigParserEnhancedData.keys()`` does not include the ``DEFAULT`` section if it
      does not exist in the file.
