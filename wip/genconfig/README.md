[![pipeline status](https://internal.gitlab.server/trilinos-devops-consolidation/code/GenConfig/badges/master/pipeline.svg)](https://internal.gitlab.server/trilinos-devops-consolidation/code/GenConfig/-/commits/master)
[![coverage report](https://internal.gitlab.server/trilinos-devops-consolidation/code/GenConfig/badges/master/coverage.svg)](http://10.202.35.89:8080/GenConfig/coverage/index.html)
[![Generic badge](https://img.shields.io/badge/docs-latest-green.svg)](http://10.202.35.89:8080/GenConfig/doc/index.html)

# GenConfig

A tool for generating the options to pass to CMake when configuring your code.


## Getting Started

1. Ensure your public ssh key is added to your GitLab-ex account:
```bash
$ cat ~/.ssh/id_rsa.pub
```
Copy the public key and add it to https://internal.gitlab.server/-/profile/keys via your browser.

2. Clone the repository:
```bash
$ git clone git@internal.gitlab.server:trilinos-devops-consolidation/code/GenConfig.git
```

3. Get Python 3.6+ in your path.

4. Install the requirements:
```bash
$ cd GenConfig
$ ./install-reqs.sh
```

5. Use the script:
```bash
$ source gen-config.sh --help

# Lists the supported configurations from 'config-specs.ini'.
# Any of these can be used as the <build-name> when running GenConfig.
$ source gen-config.sh --list-configs /path/to/src

# Loads the environment into a subshell and runs CMake with the
# flags defined in 'config-specs.ini'.
$ source gen-config.sh <build-name> /path/to/src

# Same as the last command, except the current environment
# is overwritten by LoadEnv.
$ source gen-config.sh --ci-mode <build-name> /path/to/src

# Save a CMake fragment file to be used with CMake:
$ source gen-config.sh --cmake-fragment foo.cmake <build-name>
$ cmake -C foo.cmake /path/to/src
```

## Specifying the `<build-name>`
While it is easiest to copy-paste a configuration returned by
`source gen-config.sh --list-configs /path/to/src` to use as the `<build-name>`,
this rigid syntax is not a requirement. For example, say one of the
configurations returned by `--list-configs` is:
```
  machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_debug_static
# ^__^ ^__________________________________^ ^__________^
# sys            environment name            config flag options
```
Based on documentation from [LoadEnv](https://internal.gitlab.server/trilinos-devops-consolidation/code/loadenv/-/blob/master/README.md),
if `intel` were an alias for `intel-19.0.4-mpich-7.7.15-hsw-openmp`, you
could use the following as your build name and get the same result:
```
machine-type-5_intel_debug_static
#    ^___^
#    alias
```
Furthermore, if you were to run `source gen-config.sh --list-config-flags /path/to/src`
and see the following:
```bash
$ source gen-config.sh --list-config-flags /path/to/src

+==============================================================================+
|   INFO:  Please select one of the following.
|
|   - Supported Flags Are:
|     - build-type
|       * Options (SELECT_ONE):
|         - debug (default)
|         - release
|         - release-debug
|     - lib-type
|       * Options (SELECT_ONE):
|         - static (default)
|         - shared
...
```
you could omit `debug` and `static` from the `<build-name>` because they are the
defaults for `build-type` and `lib-type` respectively. So, an equivalent `<build-name>`
to would simply be:
```
machine-type-5_intel
```
For ultimate simplicity, if the developer were running this command on an `machine-type-5` machine,
`GenConfig` could detect this without it having to be specified in the `<build-name>`
(see [DetermineSystem](https://internal.gitlab.server/trilinos-devops-consolidation/code/determinesystem)).
So, with environment aliases, default config flag options, and an automatically detected
system name, the fully simplified build name could just be:
```
intel
```
> **NOTE:** In practice, this is not the way you should specify build names within a CI script -
> it is best to be verbose in those scenarios since default config options may change over time.
> However, this syntax *does* afford convenience to the developer running `GenConfig` from the comand line.

Lastly, you may want to include relevant information in your `<build-name>` that does not conflict
with any options in `supported-config-flags.ini`. In case such information is present, `GenConfig`
will simply ignore it. For example:
```
  Project-Name-build-Trilinos-machine-type-5_intel_debug_static
#                             ^_____________________^
#        GenConfig only cares about this information
```

## GenConfig API

### Installing requirements
You will need to follow the [Getting Started](https://internal.gitlab.server/trilinos-devops-consolidation/code/GenConfig#getting-started)
instructions up through step 4. before attempting to load the GenConfig module.

### GenConfig API Documentation
Please click the 'docs' badge at the top of this file or navigate [here](http://10.202.35.89:8080/GenConfig/doc/index.html)
 with your browser for the GenConfig API documentation.

> **Note:** when using LoadEnv in your python code, the environment will only
exist in the python process you've run `import LoadEnv` from, not the shell which that
python process was run from.
