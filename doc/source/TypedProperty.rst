TypedProperty Reference
=======================

This module contains methods for adding properties to *dataclasses* that provides
the ability to add strong type checking, control the internal storage type of a
property, enforce assign-before-use policies, validator callbacks, etc.

The work is based on the pattern presented in
`9.21 Avoiding Repetitive Property Methods <https://learning.oreilly.com/library/view/python-cookbook-3rd/9781449357337/ch09.html#propertyclosures>`_
from the book
`O'Reilly Python Cookbook, 3rd Edition  <https://learning.oreilly.com/library/view/python-cookbook-3rd/9781449357337/>`_.

We implemented this instead of using `dataclass <https://docs.python.org/3/library/dataclasses.html>`_
due to the limitations in ``dataclass`` for strong type checking, internal storage type-casting, etc.

A class definition using ``TypedProperty`` might look like:

.. code-block:: python
  :linenos:

  class MyClass(object):
      section_root  = typed_property("section_root", (str), default=None)
      raw_option    = typed_property("raw_option", tuple, default=(None,None), validator=value_len_eq_2)


.. automodule:: configparserenhanced.TypedProperty
   :members:
   :undoc-members:
   :show-inheritance:
