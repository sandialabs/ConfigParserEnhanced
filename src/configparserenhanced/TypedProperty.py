#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
"""
import copy
import typing



class SENTINEL:
    pass



def typed_property(
    name: str,
    expected_type=(int, str),
    default=SENTINEL,
    default_factory=lambda: None,
    req_assign_before_use=False,
    internal_type=None,
    validator=None,
    transform=None
):
    """
    Implements a typed property in a class using the pattern
    `"9.21 Avoiding Repetitive Property Methods" from the O'Reilly
    Python Cookbook, 3rd Edition <https://learning.oreilly.com/library/view/python-cookbook-3rd/9781449357337/>`_.

    Args:
        name (str): The name of the property to create.
        expected_type (type,tuple): The *type* or a *tuple of types* enumerating allowable
            types to be assigned to the property. Default is ``(int,str)``
        default: A default value to be assigned to the tuple. Default is ``None``.
            This will be assigned without type checking.
        default_factory: Default factory method. This must be callable but is used
            when we need a complex type that can't use ``deepcopy``. Default: ``lambda: None``.
        req_assign_before_use (bool): If ``True`` then raise an exception if the value is
            used before assigned. Otherwise, the *default* value is used. Default: ``False``
        internal_type (<type>): Sets the ``<type>`` that the value is stored as (via typecast)
            internally. This is done during *assignment*.
        validator (func): A special validation function that can be called during assignment
            to provide additional checks such as list size, allowable values, etc.
            If the validator's return value is *truthy* the check suceeds, otherwise
            the check has failed and a ``ValueError`` will be raised.
            Default=None (i.e., no extra validation).
        transform (func): A function that can be used to transform the value before assignment.

    Raises:
        TypeError: if the assigned value is of the wrong type on assigmment.
        ValueError: if a *validator* is provided and the check fails (is Falsy).
        UnboundLocalError: If ``req_assign_before_use`` is True and an attempt to read
            the property is made before it's been assigned.

    """
    varname = "_" + name
    varname_set = varname + "_is_set"
    expected_type = expected_type
    validator = validator

    @property
    def prop(self):
        if not hasattr(self, varname_set):
            setattr(self, varname_set, False)
        if req_assign_before_use is True and getattr(self, varname_set) is False:
            raise UnboundLocalError("Property {} referenced before assigned.".format(name))
        if not hasattr(self, varname):
            if default is not SENTINEL:
                setattr(self, varname, copy.deepcopy(default))
            else:
                if not callable(default_factory):
                    raise TypeError(
                        "default_factory `{}` in `{}` must be callable.".format(default_factory, name)
                    )
                setattr(self, varname, default_factory())
        return getattr(self, varname)

    @prop.setter
    def prop(self, value):
        _expected_type = copy.deepcopy(expected_type)
        if not isinstance(_expected_type, typing.Iterable):
            _expected_type = (_expected_type, )
        for expected_type_i in _expected_type:
            if isinstance(value, expected_type_i):
                break
        else:
            type_names = [i.__name__ for i in _expected_type]
            raise TypeError("'{}' must be in ({})".format(name, ",".join(type_names)))

        if internal_type is not None:
            value = internal_type(value)

        if transform is not None:
            if callable(transform):
                value = transform(value)
                if internal_type is not None:
                    value = internal_type(value)
            else:
                raise TypeError(f"transform '{transform}' for property '{name}' is not callable.")

        if validator is not None:
            if callable(validator):
                if not validator(value):
                    raise ValueError(
                        f"Assignment of `{value}` to property `{name}` " +
                        f"failed validation check in `{validator}`"
                    )
            else:
                raise TypeError(f"Validator '{validator}' for property '{name}' is not callable.")

        # Assign the value to the property
        setattr(self, varname, value)

        # Save that we've assigned the value to something
        setattr(self, varname_set, True)

    @prop.deleter
    def prop(self):
        if hasattr(self, varname):
            delattr(self, varname)
        if hasattr(self, varname_set):
            delattr(self, varname_set)

    return prop
