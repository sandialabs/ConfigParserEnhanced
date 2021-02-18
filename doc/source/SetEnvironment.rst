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
.. automodule:: configparserenhanced.SetEnvironment
   :no-members:


Public Methods
++++++++++++++
.. autoclass:: configparserenhanced.SetEnvironment
   :noindex:
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
   :exclude-members:
      handler_initialize,
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

.. automethod:: configparserenhanced.SetEnvironment.handler_finalize

Environment Variable Handlers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: configparserenhanced.SetEnvironment.handler_envvar_append
.. automethod:: configparserenhanced.SetEnvironment.handler_envvar_prepend
.. automethod:: configparserenhanced.SetEnvironment.handler_envvar_remove
.. automethod:: configparserenhanced.SetEnvironment.handler_envvar_set
.. automethod:: configparserenhanced.SetEnvironment.handler_envvar_unset

Environment Modules Handlers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: configparserenhanced.SetEnvironment.handler_module_load
.. automethod:: configparserenhanced.SetEnvironment.handler_module_purge
.. automethod:: configparserenhanced.SetEnvironment.handler_module_remove
.. automethod:: configparserenhanced.SetEnvironment.handler_module_swap
.. automethod:: configparserenhanced.SetEnvironment.handler_module_unload
.. automethod:: configparserenhanced.SetEnvironment.handler_module_use

Helpers (Private)
+++++++++++++++++

.. automethod:: configparserenhanced.SetEnvironment._helper_envvar_common
.. automethod:: configparserenhanced.SetEnvironment._helper_module_common


