#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
"""
from __future__ import print_function

import sys
import traceback



# ===========================================================
#   H E L P E R   F U N C T I O N S   A N D   C L A S S E S
# ===========================================================



# ===============================
#   M A I N   C L A S S
# ===============================


class ExceptionControl(object):
    """
    The :class:`~configparserenhanced.ExceptionControl` class is intended as a helper class that would be inherited as a
    superclass to some other class to give it the capability to implement conditional
    exception handling options.

    This allows developers to create *conditional exceptions* in their class which can
    do nothing, print a warning, or raise an exception based on the severity of the issue
    and the threshold level setting, which is set via a property.

    There are six 'types' of events that can be created:

    * **WARNING:** The lowest severity. These are mostly informative, they
      might not indicate an *error* but we might want them to make note
      of something that isn't quite right.
    * **SILENT:** Shares the same severity level as "WARNING" but these events
      will *never* print a warning out. They will trigger the exception
      if the ``exception_control_level`` is set to 5, which is the same
      level that will trigger WARNING events to raise their exceptions.
      These are useful if you wish to keep output relatively clean but still
      want the event to be there.
    * **MINOR:** This is more severe than a WARNING type and indicates that an
      actual error probably happened but not a major one. This might
      be somethig that needs to be noted but doesn't always warrant
      halting execution.
    * **SERIOUS:** Second highest level of severity. This indicates something serious
      happened. We would definitely want to handle this and call out that
      a problem happened. The likelihood that this kind of event should
      halt execution and/or throw an exception rather than print out a message
      is high.
    * **CRITICAL:** The highest severity of event that might not be raised depending
      on the value of ``exception_control_level``. This would generally indicate something
      went seriously wrong and we should definitely raise the exception
      and halt execution.
    * **CATASTROPHIC:** This kind of event is the highest level of severity
      and will **always** raise the associated exception. These cannot be
      opted out of.

    When events are raised, we will set them to the appropriate type and the behaviour can
    be determined based on the ``exception_control_level`` property on the class. This property
    determines how an event is handled. The values allowed for this are 0 through 5, where:

    0. **No Exceptions!:**
       Events do not print out anything nor do they raise an exception.
    1. **Warnings Only:**
       A warning message is printed out for all events. No exceptions get raised.
    2. **Raise critical events:**
       CRITICAL events will cause the exception to be raised.
       Lower severity events will print out a warning message.
    3. **Raise serious or critical events:**
       CRITICAL and SERIOUS events will raise the associated exception.
       Lower severity events will print out a warning message.
    4. **Raise minor, serious and critical events:**
       CRITICAL, SERIOUS and MINOR events will raise their associated
       exception.
       Lower severity events will print out a warning message.
    5. **Always Raise:**
       All events trigger their associated exception, even WARNING and SILENT
       events.
    """


    @property
    def _exception_control_map_event_to_level_req(self):
        """
        A map of the Exception Control event classes to the
        minimum level of ``exception_control_level`` required to
        trigger an event of each class to be raised vs. print a warning.

        Values for each class can range from 0 to 5. An event class of 0
        indicates that the event will *always* raise an exception and a
        level of 5 would only be raised at the highest ``exception_control_level``.
        """
        output = {
            "SILENT"       : 5,
            "WARNING"      : 5,
            "MINOR"        : 4,
            "SERIOUS"      : 3,
            "CRITICAL"     : 2,
            "CATASTROPHIC" : 0
        }
        return output


    @property
    def exception_control_silent_warnings(self) -> bool:
        """A flag that toggles silencing of warnings.

        This ``boolean`` property toggles whether or not
        ``exception_control_event`` should silence events that
        don't *raise* their associated exception.

        Returns:
            bool: ``True`` to cause events that don't raise their exception
                to suppress their associated exception message. ``False``
                if we do not wish to suppress warning messages.
        """
        if not hasattr(self, '_exception_control_silent_warnings'):
            self._exception_control_silent_warnings = False
        return self._exception_control_silent_warnings


    @exception_control_silent_warnings.setter
    def exception_control_silent_warnings(self, value) -> bool:
        if not isinstance(value, (bool)):
            raise TypeError("Value must be a `bool` type in assignment.")
        self._exception_control_silent_warnings = value
        return self._exception_control_silent_warnings


    @property
    def exception_control_compact_warnings(self) -> bool:
        """A flag that toggles compact warnings.

        This ``boolean`` property toggles the use of compact warnings.

        Returns:
            bool: ``True`` will set warnings to be compact in nature
                and print out just a short warning rather than the
                full warning.
        """
        if not hasattr(self, '_exception_control_compact_warnings'):
            self._exception_control_compact_warnings = False
        return self._exception_control_compact_warnings


    @exception_control_compact_warnings.setter
    def exception_control_compact_warnings(self, value) -> bool:
        if not isinstance(value, (bool)):
            raise TypeError("Value must be a `bool` type in assignment.")
        self._exception_control_compact_warnings = value
        return self._exception_control_compact_warnings


    @property
    def exception_control_level(self):
        """Get the value of the ``exception_control_level`` property.

        The parameter must be convertable to an integer and must be
        between 0 and 5. Values below 0 will be set to 0 and values
        greater than 5 will be set to 5.

        The default value is set to 4 (CRITICAL, SERIOUS, and MINOR
        events will raise an exception; WARNING events will only warn).

        Returns:
            int: The ``exception_control_level`` value.
        """
        if not hasattr(self, '_exception_control_level'):
            self._exception_control_level = 4
        return self._exception_control_level


    @exception_control_level.setter
    def exception_control_level(self, value):
        value = int(value)
        value = max(0, value)
        value = min(5, value)
        self._exception_control_level = value
        return self._exception_control_level


    def exception_control_event(self, event_type, exception_type, message=None):
        """An event that conditinally raises an exception.

        Triggers an event that will be handled based on the rules given
        by the current ``exception_control_level`` value and the severity
        class of this event.

        Args:
            event_type (str): Sets the *type* of exception this is. Valid
                entries are ["SILENT"," WARNING", "MINOR", "SERIOUS",
                "CRITICAL", "CATASTROPHIC"].
            exception_type (object): An :class:`Exception` type that would be raised
                if the ``exception_control_level`` threshold is high enough to
                make this exception get raised. This must be an :class:`Exception`
                (or a derivitive) type.
            message (str): If the exception gets triggered, what message
                should we pass along when it gets raised?
        """

        def _is_raisable(exception):
            """Helper function: determine if an object is 'raiseable'.

            To determine if an object is something that can be raised via ``raise``,
            you must do something more than just check if something inherits from
            :class:`Exception`.

            This function determines if an object *can be raised*.

            Args:
                exception (object): An object we wish to test if it can be **raised**.

            Returns:
                bool: True if ``exception`` can be raised via ``raise exception(message)``.
            """
            try:
                raise exception
            except:
                exc_type, exc = sys.exc_info()[:2]

                if exc is exception or exc_type is exception:
                    return True
                elif exc_type is TypeError:
                    return False                                                                    # pragma: no cover
                else:
                    # Re-raise other exceptions such as KeyboardInterrupt, etc.
                    raise                                                                           # pragma: no cover

        event_type = str(event_type).upper()

        if not _is_raisable(exception_type):
            raise TypeError("The exception type must be some kind of `Exception`.")

        req_exception_control_level = self._exception_control_map_event_to_level_req[event_type]
        if self.exception_control_level >= req_exception_control_level:
            if message == None:
                raise exception_type
            else:
                raise exception_type(message)
        elif self.exception_control_level > 0:
            try:
                raise exception_type
            except exception_type as exc:

                if (not self.exception_control_silent_warnings) and (event_type != "SILENT"):

                    if self.exception_control_compact_warnings:
                        tb_last = str(traceback.format_stack()[-2])
                        tb_last = tb_last.splitlines()[0]
                        tb_last = tb_last.strip()
                        print("!! EXCEPTION SKIPPED ({} : {}) @ {}".format(
                            event_type, exception_type.__name__, tb_last))
                    else:
                        print("!! " + "="*80)
                        print("!! EXCEPTION SKIPPED")
                        print("!! Event Type : {}".format(event_type))
                        print("!! Exception  : {}".format(exception_type.__name__))
                        if message != None:
                            message = message.replace("\n", "\n!!            : ")
                            print("!! Message    : {}".format(message))

                        print("!!")
                        print("!! Call Stack:")
                        # Ignore the last entry from the call stack since that is _this_ method.
                        # and it's the _caller_ that we care about for the call stack in reporting.
                        for line in traceback.format_stack()[:-1]:
                            line = line.strip()
                            line = line.replace("\n", "\n!! ")
                            print("!! {}".format(line.strip()))

                        print("!!")
                        print("!! Increase `exception_control_level` to {} to raise this exception.".format(req_exception_control_level))
                        print("!! " + "="*80)

                    sys.stdout.flush()

        return