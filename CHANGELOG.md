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
### Security
-->


## [Unreleased]
- ConfigParserEnhanced is currently _alpha_ and has many changes occurring.
- Deprecating `setup.py` for `pyproject.toml`
- Moved `__version__` string to a new file, `version.py`

### Added
### Changed
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


