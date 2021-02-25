SetEnvironment Class Reference
==============================

The SetEnvironment module is an extension of ``configparserenhanced.ConfigParserEnhanced``
which implements handlers for *environment variable* and *environment modules* rules in
a .ini file.

This class implements the following new *operations* for .ini file processing:

.. csv-table:: Supported Operations
   :file: tbl_setenvironment_commands.csv
   :header-rows: 1
   :widths: 20,30,80


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
      handler_envvar_append,
      handler_envvar_prepend,
      handler_envvar_remove,
      handler_envvar_set,
      handler_envvar_unset,
      handler_module_load,
      handler_module_purge,
      handler_module_remove,
      handler_module_swap,
      handler_module_unload,
      handler_module_use


Operation Handlers
++++++++++++++++++
Operation handlers for .ini file processing

.. automethod:: setenvironment.SetEnvironment.handler_finalize

Environment Variable Handlers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: setenvironment.SetEnvironment.handler_envvar_append
.. automethod:: setenvironment.SetEnvironment.handler_envvar_prepend
.. automethod:: setenvironment.SetEnvironment.handler_envvar_remove
.. automethod:: setenvironment.SetEnvironment.handler_envvar_set
.. automethod:: setenvironment.SetEnvironment.handler_envvar_unset

Environment Modules Handlers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: setenvironment.SetEnvironment.handler_module_load
.. automethod:: setenvironment.SetEnvironment.handler_module_purge
.. automethod:: setenvironment.SetEnvironment.handler_module_remove
.. automethod:: setenvironment.SetEnvironment.handler_module_swap
.. automethod:: setenvironment.SetEnvironment.handler_module_unload
.. automethod:: setenvironment.SetEnvironment.handler_module_use

Helpers (Private)
+++++++++++++++++

.. automethod:: setenvironment.SetEnvironment._helper_envvar_common
.. automethod:: setenvironment.SetEnvironment._helper_module_common


