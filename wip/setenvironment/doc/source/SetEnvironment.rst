
SetEnvironment Class Reference
==============================

The SetEnvironment module is an extension of ``configparserenhanced.ConfigParserEnhanced``
which implements handlers for *environment variable* and *environment modules* rules in
a .ini file.


Supported .ini Actions
----------------------
This class implements the following new *operations* for .ini file processing:

.. csv-table:: Supported Operations
   :file: tbl_setenvironment_commands.csv
   :header-rows: 1
   :widths: 20,30,80


``envvar-append``
+++++++++++++++++
**Usage**: ``envvar-append <envvar_name> : <envvar_val>``

Appends ``envvar_val`` to an existing environment variable named ``envvar_name`` using
the delimiter defined by ``os.pathsep``. If ``envvar_name`` does not exist then it will
be created.


``envvar-assert-not-empty``
+++++++++++++++++++++++++++
**Usage**: ``envvar-assert-not-empty <envvar_name>: <optional_error_message>``

This will check an environment variable and will raise an error if
the environment variable specified does not exist or exists but is
an empty string.


``envvar-find-in-path``
+++++++++++++++++++++++
**Usage**: ``envvar-find-in-path <envvar_name>: <executable_name>``

This will attempt to locate an *executable* in the current ``PATH`` and
if it's found the path to it will be stored in the environment variable
``envvar_name``.

.. code-block:: bash
  :linenos:

  export envvar=$(which envvar_name)


``envvar-prepend``
++++++++++++++++++
**Usage**: ``envvar-prepend <envvar_name> : <envvar_val>``

Prepends ``envvar_val`` to an existing environment variable named ``envvar_name`` using
the delimiter defined by ``os.pathsep``. If ``envvar_name`` does not exist then it will
be created.


``envvar-remove``
+++++++++++++++++
**Usage**: ``envvar-remove <envvar_name>``

This command is used to *remove all occurrences* of some environment variable
named ``envvar_name`` from the actions list. Note: this is different from ``envvar-unset``
since this fully removes all preceeding occurrences of operations that involve
``envvar_name`` as though they were not even in the ``.ini`` file.


``envvar-remove-path-entry``
++++++++++++++++++++++++++++
**Usage**: ``envvar-remove-path-entry <envvar_name>: <path>``

TODO: Ph'nglui mglw'nafh Cthulhu R'lyeh wgah'nagl fhtagn. S'uhn llll 'bthnk throd czhro, y-gof'nn
f'chtenff wgah'n ch' stell'bsna f'lw'nafh sll'ha y-orr'e ilyaa.


``envvar-remove-substr``
++++++++++++++++++++++++
**Usage**: ``envvar-remove-substr <envvar_name>: <substr>``

TODO: Ph'nglui mglw'nafh Cthulhu R'lyeh wgah'nagl fhtagn. S'uhn llll 'bthnk throd czhro, y-gof'nn
f'chtenff wgah'n ch' stell'bsna f'lw'nafh sll'ha y-orr'e ilyaa.


``envvar-set``
++++++++++++++
**Usage**: ``envvar-set <envvar_name> : <envvar_val>``

Sets an environment variable. This is the equivalent of the bash
command: ``export envvar_name=envvar_val``.
If ``envvar_name`` already exists then it will be overwritten.


``envvar-set-if-empty``
+++++++++++++++++++++++
**Usage**: ``envvar-set-if-empty <envvar_name> : <envvar_val>``

Sets an environment variable only if it does not exist or is empty. This is the
equivalent of the following bash code:

.. code-block:: bash
  :linenos:

  if [[ -z "${ENVVAR_NAME}" ]]; then
      export ${ENVVAR_NAME}="${ENVVAR_VALUE}"
  fi


``envvar-unset``
++++++++++++++++
**Usage**: ``envvar-unset <envvar_name>``

Removes an existing envvar. This is the equivalent to the following bash command:

.. code-block:: bash
  :linenos:

   unset ${ENVVAR_NAME}


``module-load``
+++++++++++++++

Variant 1
~~~~~~~~~
**Usage**: ``module-load <module_name>``

Loads an environment module without a version specified, i.e., this loads the *default*
module version. This is equivalent to the following in bash:

.. code-block:: bash
  :linenos:

  module load <module_name>

Variant 2
~~~~~~~~~
**Usage**: ``module-load <module_name>: <module_ver>``

Loads an environment module with a version specified. This is equivalent to the following in bash:

.. code-block:: bash
  :linenos:

  module load <module_name>/<module_ver>


``module-purge``
++++++++++++++++
**Usage**: ``module-purge``

Executes a ``module purge`` operation, which *unloads* all currently loaded modules.

.. code-block:: bash
  :linenos:

  module purge


``module-remove``
+++++++++++++++++
**Usage**: ``module-remove <module name>``

This command is different from ``module-unload`` in that it will scan the **current**
action-list for any occurrences of ``<module_name>`` (i.e., any ``module-load``, ``module-swap``,
or ``module unload`` type commands) and will **remove** that command from the action list.

Unlike ``module-unload`` which would unload a module that was loaded, ``module-remove`` will
effectively **erase** that module from the list of actions.


``module-swap``
+++++++++++++++
**Usage**: ``module-swap <module_old> : <module_new>/<version>``

This operation will execute a *swap* command to replace ``module_old`` with ``module_new``.
The ``version`` argument is only necessary if a *default* version is not available and/or
you wish to be explicit about the version to load or you're loading a non-default version.
This command is equivalent to the following bash command:

.. code-block:: bash
  :linenos:

  module swap <module old> <module_new>/<version>


``module-unload``
+++++++++++++++++
**Usage**: ``module-unload <module_name>``

Executes the ``module unload`` command to invoke an unload of a module that has already been loaded.
Note that this is different from ``module-remove``. This is equivalent to the following command in
bash:

.. code-block:: bash
  :linenos:

  module unload <module_name>


``module-use``
++++++++++++++
**Usage**: ``module-use <path_to_modules>``

Appends a new path to the **environment modules** application's search space.
This is the equivalent of the bash command:

.. code-block:: bash
  :linenos:

  module use <path_to_modules>



API Documentation
-----------------
.. automodule:: setenvironment.SetEnvironment
   :no-members:


Public Methods
++++++++++++++
.. autoclass:: setenvironment.SetEnvironment
   :noindex:
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
   :exclude-members:
      handler_finalize,
      handler_initialize



Operation Handlers
++++++++++++++++++
Operation handlers for .ini file processing

.. automethod:: setenvironment.SetEnvironment.handler_initialize
.. automethod:: setenvironment.SetEnvironment.handler_finalize


Environment Variable Handlers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: setenvironment.SetEnvironment._handler_envvar_append
.. automethod:: setenvironment.SetEnvironment._handler_envvar_assert_not_empty
.. automethod:: setenvironment.SetEnvironment._handler_envvar_find_in_path
.. automethod:: setenvironment.SetEnvironment._handler_envvar_prepend
.. automethod:: setenvironment.SetEnvironment._handler_envvar_remove
.. automethod:: setenvironment.SetEnvironment._handler_envvar_remove_substr
.. automethod:: setenvironment.SetEnvironment._handler_envvar_remove_path_entry
.. automethod:: setenvironment.SetEnvironment._handler_envvar_set
.. automethod:: setenvironment.SetEnvironment._handler_envvar_unset


Environment Modules Handlers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: setenvironment.SetEnvironment._handler_module_load
.. automethod:: setenvironment.SetEnvironment._handler_module_purge
.. automethod:: setenvironment.SetEnvironment._handler_module_remove
.. automethod:: setenvironment.SetEnvironment._handler_module_swap
.. automethod:: setenvironment.SetEnvironment._handler_module_unload
.. automethod:: setenvironment.SetEnvironment._handler_module_use


Helpers (Private)
+++++++++++++++++
.. automethod:: setenvironment.SetEnvironment._apply_envvar
.. automethod:: setenvironment.SetEnvironment._apply_module
.. automethod:: setenvironment.SetEnvironment._helper_handler_common_envvar
.. automethod:: setenvironment.SetEnvironment._helper_handler_common_module
.. automethod:: setenvironment.SetEnvironment._gen_actioncmd_envvar
.. automethod:: setenvironment.SetEnvironment._gen_actioncmd_module
.. automethod:: setenvironment.SetEnvironment._remove_prefix
.. automethod:: setenvironment.SetEnvironment._exec_helper


Helpers (Private - Writers)
+++++++++++++++++++++++++++
.. automethod:: setenvironment.SetEnvironment._gen_script_header_bash
.. automethod:: setenvironment.SetEnvironment._gen_script_header_python


Free Functions
++++++++++++++
.. autofunction:: setenvironment.SetEnvironment.envvar_find_in_path
.. autofunction:: setenvironment.SetEnvironment.envvar_op
.. autofunction:: setenvironment.SetEnvironment.envvar_set
.. autofunction:: setenvironment.SetEnvironment.envvar_set_if_empty
