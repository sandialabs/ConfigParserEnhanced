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
#### Internal
#### Todo (for Unreleased)
-->



## [0.3.0] - Unreleased
#### Added
- New envvar command: `envvar-assert-not-empty` as part of ISSUE #12
#### Changed
#### Deprecated
#### Removed
#### Fixed
#### Security
#### Internal
- Renamed handlers from *public* api to *private* api for consistency.
  Only `handler_initialize` and `handler_finalize` remain in the public
  API since `ConfigParserEnhanced` has them there and they're designed
  to be overridden.
#### Todo (for Unreleased)



## [0.2.0] - 2021-03-22
#### Added
- New free-function: `envvar_assign` - A helper that handles _assigning_ envvars.
  Adds option to raise an exception if the envvar value is an empty string or not.
  Default is to allow empty assignment, but having this toggle will allow us to
  tune this later on.
- Added a `handler_initialize` handler for the start of searches.
- Added a new **private** function: `_initialize_handler_parameters` which controls the
  _initialization_ of the `handler_parameters` that is passed around by the handlers
  when parsing a `.ini` file section. This replaced 3x snippets that did the same thing.
- New command: `envvar-remove-substr` - this will remove a substring
  from an existing envvar. Syntax: `envvar-remove-substr <envvar> : <substr>`.
- New command: `envvar-remove-path-entry` - this will remove a path entry
  from an existing path-type envvar. Syntax: `envvar-remove-path-entry <envvar>: <path>`.
- New command: `envvar-find-in-path` - This new function will locate an executable
  that is on the path. Syntax: `envvar-find-in-path <envvar>: <executable>`
#### Changed
- Changes the `actions` parameter to now be a _dictionary_ where each key is a
  _section name_ and the values are now _action lists_. This allows caching of
  action lists when parsing multiple sections instead of the previous behvaiour
  where the _last_ section parsed was what stored actions.  See Issue #13 for
  additional details on bugs this could create.
- Modify `write_actions_to_file()` to add new parameter(s):
    - `include_body = True`
    - `include_shebang = True`
  to allow customization of the generated output when generating output data for files.
- Rename `_gen_actions_script()` to `generate_actions_script()` to expose generation of
  script content to the public API.
- Free functions `envvar_assign` and `envvar_op` are now exposed to the package API in
  the `__init__.py` file.
- Updated to account for changes in `ConfigParserEnhanced` regarding
  operation normalization. This doesn't affect `.ini` file construction
  but internally we now need to use `_` instead of `-` characters in the
  operation matching.
  Operations in `.ini` files should actually be able to interchance `-` and `_`
  without changing any actual behaviour now.
#### Deprecated
#### Removed
#### Fixed
- Fixed Issue #13
  - Modified `apply()`, `pretty_print_actions()`, `generate_actions_script()` and
    `write_actions_to_file()` to take a required `sections` parameter to specify which
    section should be worked on.


#### Security
#### Todo (for Unreleased)



## [0.1.0] - 2021-03-10
- ConfigParserEnhanced is currently _alpha_ and has many changes occurring.

#### Added
- `apply()` method now handles `envvar` and `module` commands properly.
- Added a sample 'modulefiles' dir under `unittests` for testing module
  command handling.
- Added `write_actions_to_file(filename,interpreter)`.
  This currently only supports `bash` and `python` output.

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


