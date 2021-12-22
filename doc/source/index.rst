.. ConfigParserEnhanced documentation master file, created by
   sphinx-quickstart on Wed Jan 13 15:30:46 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ConfigParserEnhanced
====================
.. toctree::
   :maxdepth: 1
   :caption: Table of Contents:

   ConfigParserEnhanced
   Debuggable
   ExceptionControl
   HandlerParameters
   TypedProperty
   License <License>

Indices and Tables
------------------
* :ref:`genindex`
* :ref:`modindex`

.. * :ref:`search`

Overview
========

The ConfigParserEnhanced (CPE) package provides extended handling of ``.ini`` files
beyond what `ConfigParser <https://docs.python.org/3/library/configparser.html>`_ provides
by adding an active syntax to options within sections.

A _standard_ ``.ini`` file is generally formatted like this:

.. code-block:: ini
    :linenos:

    [Section 1]
    Foo: Bar
    Baz: Bif

    [Section 2]
    Foo: Bar2
    Bif: Baz

These files are used to organize sets of *key - value* pairs called "options" within
groups called "sections". In the example above there are two sections, "Section 1" and
"Section 2". Each of them contains two options where Section 1 has the keys 'Foo' and 'Baz'
which are assigned the values 'Bar' and 'Bif', respectively. For more details on .ini files
please see the documentation for `ConfigParser <https://docs.python.org/3/library/configparser.html>`_.

*ConfigParserEnhanced* extends the processing capabilities for .ini files by adding
an *active* component of handling of each option. This allows us to merge the processing
with the reading of each option. In this model, we treat individual options according to
the following syntax:

.. code-block:: ini

    command param1 param2 ... 'param with spaces' ... paramN : value

The entries on an option in the *key* portion are space-separated generally and the
*first* entry can be considered the *command*. CPE will attempt to map the detected
*command* to a handler method and if a matching one is found then it will send the
option to that handler for processing. Options that do not map to a handler will be
treated as a standard "key:value" pair.

Internally, these handlers methods defined according to a naming convention like
``handler_command()``.

CPE only provides one pre-defined command: ``use`` which is formatted as ``use TARGET:``
where *param1* is the TARGET (there is no value field for this one).  The TARGET paramter
takes the *name of a target section* that will be loaded in at this point. This works
in the same way a ``#include`` would work in C++ and serves to **insert** the contents or
processing of the target section into this location.

The **use** command is useful for .ini files for complex systems by allowing developers to
create a *common* section and then have *specializations* where they can customize options
for a given project. For example:

.. code-block:: ini
    :linenos:

    [COMMON]
    Key C1: Value C1
    Key C2: Value C2
    Key C3: Value C3

    [Data 1]
    Key D1: Value D1
    use COMMON
    Key D2: Value D2

In this example, processing section ``Data 1`` via CPE will result in the following options:
``Key D1: Value D1``, ``Key C1: Value C1``, ``Key C2: Value C2``, ``Key C2: Value C2``,
``Key D2: Value D2``.

An alternative way of looking at this is it's like having a .ini file
that is *effectively* the following where the ``use`` commands are replaced with the
results of a Depth-First expansion of the linked sections:

.. code-block:: ini
    :linenos:

    [COMMON]
    Key C1: Value C1
    Key C2: Value C2
    Key C3: Value C3

    [Data 1]
    Key D1: Value D1
    Key C1: Value C1
    Key C2: Value C2
    Key C3: Value C3
    Key D2: Value D2

Examples
========
Here we show example usages of ConfigParserEnhanced.
These examples can be found in the ``examples/`` directory
of the repository.

Example 1
----------

example-01.ini
++++++++++++++
.. literalinclude:: ../../examples/example-01.ini
    :language: ini
    :linenos:

ConfigParserEnhanced-example-01.py
++++++++++++++++++++++++++++++++++
.. literalinclude:: ../../examples/ConfigParserEnhanced-example-01.py
    :language: python
    :linenos:

Console Output
++++++++++++++
.. literalinclude:: ../../examples/ConfigParserEnhanced-example-01.log
    :language: text
    :linenos:
