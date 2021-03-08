Changelog
=========
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
## [X.Y.Z] - YYYY-MM-DD or [Unreleased]
#### Added
#### Changed
#### Deprecated
#### Removed
#### Fixed
#### Security
#### Todo (for Unreleased)
-->


## [Unreleased]
- ConfigParserEnhanced is currently _alpha_ and has many changes occurring.

#### Added
- `apply()` method now handles `envvar` and `module` commands properly.
- Added a sample 'modulefiles' dir under `unittests` for testing module
  command handling.
- Added `write_actions_to_file(filename,interpreter)`.
  This currently only supports `bash` output.

#### Changed
- Fairly major overhaul of the way we generate the commands to support
  the `write_actions_to_file()` operations. In python now we generate
  snippets of *python* code that get executed rather than just calling
  things like `os.environ[envvar] = value` directly within the `if-then-else`
  case statements. This was done to try and minimize the number of different
  places in the code we check the value of the _operation_ to decide what to
  do -- or to collect all of them for a given task such as `modules` or `envvars`
  into the same method. The general idea is to reduce the number of _different_
  places within the code one must add some new _case_ entry to the switch if
  we added some new envvar or module operation.

#### Deprecated
#### Removed
#### Todo Before Next Release
- Expand testing to fully test the new `apply()`
- Clean up `apply()`
  - Expand messaging & console logging for `apply()`
- Clean up Documentation
- Style & Consistency


## [0.0.1] - 2021-02-22
- `0.0.1` - Initial development version


