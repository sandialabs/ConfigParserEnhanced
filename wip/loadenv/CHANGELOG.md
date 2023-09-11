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

## [0.0.2] [Unreleased]
#### Added
- .gitlab-ci.yml: base_python_only integration test.
#### Changed
- load-env.sh:
  - Now accepts a '--ci_mode' positional argument. The default behavior
    is to enter interactive mode and place the user in the environment
    Using a subprocess of bash run in interactive mode addresses two issues:
      1. Preserves the user's environment (#34)
      2. Ensures that sourcing 'exit' will not terminate the user's parent
	 shell
  - Prevents load-env.sh from being run within an existing interactive session
  - load-env.sh now cleans up all artifacts (bash variables and tmp files)
    unless an error is encountered when using --ci_mode
  - Now invokes LoadEnv.py via: `python3 -E -s -m loadenv`
    - This has 3 benefits: -E ignores PYTHON* envvars, -s ignores user-local site packages, -m adds
      the working directory to python's system path so loadenv can be run with depedencies snapshotted
      rather than pip-installed. This gives the user a more consistent python environment when using
      load-env.sh
  - Prints out pretty success messages.
  - Uses same error and warning message format as LoadEnv.py
- loadenv:
  - Can now be run as a module via 'python3 -m loadenv'
- LoadEnv.py:
  - Has a new usage message for both LoadEnv.py and load-env.sh
- Removed src and moved load-env.sh to the top-level directory
- install_reqs.sh
  - Can now be run from any working directory
  - Snapshots depdencies into top-level loadenv dir
  - No longer depends on python3 or pip
  - Added dependency on KeywordParser
#### Deprecated
#### Removed
#### Fixed
- Bug in LoadEnv.py that causes 1 (error) instead of 0 (success) to be returned when listing envs (#38)
- Bug in load-env.sh when sourced outside of loadenv dir (#43)
- Bug in tmp file location when multiple users run on the same system
- Bug in load-env.sh script when trying to use the help option
- Bug in load-env.sh script when python3 is not in PATH
- Bug in load-env.sh script when python3 version check is printed
- Bug in load-env.sh script when load-env.sh is run after an environment has already been loaded (#19)
   - Fixed by passing '-E' to python3
#### Security
#### Internal
#### Todo (for Unreleased)

## [0.0.1] - 2021-04-19
- `0.0.1` - Initial development version
