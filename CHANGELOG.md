# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
## [X.Y.Z] - YYYY-MM-DD or [Unreleased]
### Added
### Changed
### Deprecated
### Removed
### Fixed
### Internal
### Security
-->

## [0.4.1] - YYYY-MM-DD or [Unreleased]
### Added
- ConfigParserEnhanced property: `configparser_delimiters` which exposes the ability to
  modify the delimiters in the underlying `ConfigParser` parser for .ini files. Default
  value is `('=',':')` and it allows assignment as a list, tuple, or str but gets converted
  to a tuple internally.
- Internal helper method `_locate_class_method(method_name)` which finds a class method
  if it is defined.
### Changed
### Deprecated
### Removed
### Fixed
### Internal
### Security


## [0.4.0] - 2021-03-30
Removed the regular expression based splitting method for keys into tokens
for the use of `shlex.split`, which looks to do a better job of extracting
tokens in the manner we would like without requiring a complex REGEX.

HandlerParameters was also changed to remove `op_params` in favor of two new
properties: `op` and `params`, where `op` is a string and `params` is a list
of strings.

### Added
- HandlerParams property: `HandlerParams.op`
- HandlerParams property: `HandlerParams.params`
### Changed
### Deprecated
### Removed
- ConfigParserEnhanced method: `ConfigParserEnhanced._regex_splitter()`
- ConfigParserEnhanced method: `ConfigParserEnhanced._regex_op_matcher()`
- ConfigParserEnhanced method: `ConfigParserEnhanced._get_op1_from_regex_match()`
- ConfigParserEnhanced method: `ConfigParserEnhanced._get_op2_from_regex_match()`
- HandlerParameters property : `HandlerParams.op_params`
### Fixed
### Internal
### Security



## [0.3.1] - 2021-03-24
### Added
### Changed
### Deprecated
### Removed
### Fixed
- Issue #10: Bugfix: dots `.` in section names confused the `use` command.
### Internal
- Add `_validate_parameter` internal function to wrap the parameter
  check operation that we do around the code. This simplifies some
  of the coverage issues and also makes it easier to put more type
  checks around parameters.
### Security



## [0.3.0] - 2021-03-22
### Added
- `ConfigParserEnhanced.parse_all_sections()` added as a shortcut to kick off
  a full parse of ALL sections in the .ini file.
### Changed
- Changed `ConfigParserEnhancedData.data` property to include an empty "DEFAULT"
  section if none is provided by the .ini file. This is to maintain compatibility
  with `ConfigParser`.
- Changed `ConfigParserEnhancedData.get(section, option)` to
  `ConfigParserEnhancedData::get(section, option=None)`. Now `option` can be
  an optional parameter and will return a `dict` containing the section's
  keys if only a `section` is provided.
### Deprecated
### Removed
### Fixed
### Security


## [0.2.1] - 2021-03-15
### Added
- New private method: `_loginfo_reset`. This removes the `_loginfo` attribute.
- New internal method `_apply_transformation_to_operation()`.
  Applies any needed transformations to the raw `<operation>` strings.
  Currently this just replaces occurrences of `-` with `_` to operations.
- New internal method `_apply_transformation_to_parameter()`.
  Applies any needed transformations to the raw `<parameter>` strings.
  Currently this is just a pass-through, added now to pair with
  `_apply_transformation_to_operation()`.
### Changed
- Add parameter `parse` to `ConfigParserEnhancedData.sections` which can be
  either `True`, `False`, or `"force"`.
    - If `False` then requesting `configparserenhanceddata.sections()` will give
      the list of sections in the .ini file without parseing them.
    - If `True` then requesting `configparserenhanceddata.sections()` will give
      the list of sections in the .ini file but it will also kick off the parser
      to parse (and cache) them.
    - If `"force"` then requesting `configparserenhanceddata.sections()` will
      FORCE a (re)parse of the sections in the .ini file.
- Add parameter `force_parse` to `ConfigParserEnhancedData._parse_owner_sections()`
  in support of new `parse` parameter to `ConfigParserEnhancedData.sections`.
- `operations` have added processing to do some normalization. Currently
  this is just a replacement of any `-` with `_`. For example, an
  operation such as `foo-bar-baz` will be converted to `foo_bar_baz`
  internally.
### Deprecated
### Removed
### Fixed
- Fix a bug in the indexing in the `ExceptionControl` module to print out the
  correct stack entry showing where `exception_control_event` was called that
  triggered the event in the traceback when `exception_control_compact_warnings`
  is enabled.
### Security



## [0.2.0] - 2021-03-10
### Added
### Changed
- `ExceptionControl`
    - Add property `_exception_control_map_event_to_level_req` to `ExceptionControl`
      which maps the exception control levels to the type names.
    - Add new class of `exception_control_event`: "CATASTROPHIC" which indicates
      errors that will _always_ raise the exception and cannot be overridden.
- Added property `exception_control_silent_warnings` to `ExceptionControl`
  to enable silencing events that would only print out a warning message.
- Added property `exception_control_compact_warnings` to `ExceptionControl`
  to enable _compact_ one-line warning messages instead of the full message and
  stack trace that is normally generated.
- Renamed `generic_handler` to `_generic_option_handler` because that name
  could inadvertantly cause a `.ini` file option such as
  `generic command: should not invoke a handler` to invoke the `generic_handler`
  but it would go through the _handled operation_ code path and not the true _generic_
  command code path.
### Deprecated
### Removed
### Fixed
### Security



## [0.1.4] - 2021-03-04
### Added
- New *property* to `ConfigParserEnhanced`: `parse_section_last_result`.
  This property gives access to the results from the _last_ call to
  `parse_section()`.
### Changed
- `ConfigParserEnhanced.__init__` signature changed. The `filename` parameter
  is now optional at construction time. It can be still be set via the `inifilepath`
  property.
- Parses of sections kicked off via the inner class `ConfigParserEnhancedData`
  such as `parser.configparserenhanceddata[section]` will no longer
  tell `parse_section` to skip calling `handler_initialize` and `handler_finalize`.
  The output of this call won't change, but this will affect the state of
  `handler_parameters.data_shared`,  and what is returned by `parse_section_last_result`.
### Deprecated
### Removed
### Fixed
### Security



## [0.1.3] - 2021-03-01
- ConfigParserEnhanced is currently _alpha_ and has many changes occurring.

### Added
- Added `enter_handler()` method to `ConfigParserEnhanced`.
  This should be called immediately upon entry to a handler to provide
  logging information that can be useful when debugging.
  This is in the public api -- not that we encourage a subclass to modify
  it much but we encourage subclasses to use it in their custom handlers.
- Added `exit_handler()` method to `ConfigParserEnhanced`
  This should be called just before a handler exits to provide
  logging and information that can be useful when debugging.
  This is in the public api -- not that we encourage a subclass to modify
  it much but we encourage subclasses to use it in their custom handlers.
- Added `_launch_handler_generic` method to `ConfigParserEnhanced` which
  is a wrapper to launching `handler_generic`. This handles launching
  the generic handler and updating the `configparserenhanceddata` structure.
  - This was also useful because we launch the generic handler from two
    places in the parser.


### Changed
- Moved `__version__` string to a new file, `version.py`
- Replaced `setup.py` with `pyproject.toml`
  - Generated using the *poetry* package (`python3 -m pip install --user poetry`).
- Updated `ConfigParserEnahanced._new_handler_parameters` to create a 'new'
  `HandlerParameters` object when called that copies in the `data_shared` and
  `data_internal` references from the caller but creates new entries for the
  other pieces. This fixed a bug in recursion of `use <section>` entries where
  the handler that is called would overwrite parts of `handler_parameters` which,
  as a side effect, would change the state to the caller in the recursion.
  - Modified the API to `_new_handler_parameters`
  - Added

### Deprecated

### Removed



## [0.1.2] - 2021-02-24
### Changed
- Fixed issue in the formatting of the `ExceptionControl` method `exception_control_event`
  where events are printed to the console rather than raising an exception. The message
  now properly prints out the _call stack_ to the location where `exception_control_event`
  was called from. The warning message formatting was changed slightly as well to add
  the characters `!! ` as a prefix to all the lines in the message.



## [0.1.1] - 2021-02-23
### Changed
- Brought handling of a `key:value` pair where there is no separator character (`:`, `=`)
  in line with how `configparser` handles these.  If they key has a separator but no value
  then the _value_ field will get an empty string, but if there is no separator then _value_
  will be set to `None`.  Prior to this, ConfigParserEnhanced converted _value_ to a string
  which would cause `None` to be converted to a string: `"None"`.



## [0.1.0] - 2021-02-23
### Removed
- Removed `SetEnvironment` into its own repository.
- Cleaned up `setup.py` and added new helper scripts.



## [0.0.1] - 2021-02-22
- `0.0.1` added to help SetEnvironment have a version to pull via Pip.


