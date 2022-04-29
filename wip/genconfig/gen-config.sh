#!/bin/bash

####### BEGIN runnable checks #######
# Ensure that this script is sourced.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "This script must be sourced."
    exit 1
fi

# Ensure that this script is not run in a subshell.
# This check was added due to bug: TRILFRAME-290.
if [[ ! "$BASH_SUBSHELL" == "0" ]]; then
    if [[ -z $GENCONFIG_CI_BYPASS_SUBSHELL_CHECK ]]; then
	echo "This script cannot be run in a subshell since it modifies your shells environment."
	exit 1
    fi
fi

# Ensure python3 is in PATH and that the version is high enough.
if [[ ! -z $(which python3 2>/dev/null) ]]; then
    python_too_old=$(python3 -c 'import sys; print(sys.version_info < (3, 6))')
else
    echo "This script requires Python 3.6+."
    echo "Please load Python 3.6+ into your path."
    unset python_too_old; return 1
fi

if [[ "${python_too_old}" == "True" ]]; then
    echo "This script requires Python 3.6+."
    echo "Your current python3 is only $(python3 --version)."
    unset python_too_old; return 1
fi
####### END runnable checks #######



####### BEGIN helper functions #######
################################################################################
# cleanup function
#
# This function should be called anytime this script returns control to the
# caller.
################################################################################
function cleanup_gc()
{
    local ret_val=$ret
    [ -f /tmp/$USER/.bash_cmake_args_loc ] && rm -f /tmp/$USER/.bash_cmake_args_loc 2>/dev/null
    [ -f /tmp/$USER/.load_env_args ] && rm -f /tmp/$USER/.load_env_args 2>/dev/null

    unset python_too_old script_dir cleanup_gc gen_config_py_call_args gen_config_helper
    unset gc_random config_prefix path_to_src load_env_args cmake_args_file ret have_cmake_fragment
    trap -  SIGHUP SIGINT SIGTERM
    return $ret_val
}
trap "cleanup_gc; return 1" SIGHUP SIGINT SIGTERM
####### END helper functions #######



# Get the location to the Python script in a subshell. cd does not change the previous
# working directory of the caller since this is run in a subshell.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

# If no command line args were provided, show the --help
if [[ $# -eq 0 || "$@" == *"--help"* || "$@" == "-h"* || "$@" == *" -h" ]]; then
    python3 -E -s ${script_dir}/gen_config.py --help; ret=$?
    cleanup_gc; return $?
fi

# Terminate early for list options, bypass positional arg error without
# enforcing users to supply path_to_src when listing options
if [[ "$@" == *"--list-configs"* || "$@" == *"--list-config-flags"* ]]; then
    if [ -d ${@: -1} ]; then
        python3 -E -s ${script_dir}/gen_config.py ${@: 1:$(expr $# - 1)}; ret=$?
    else
        python3 -E -s ${script_dir}/gen_config.py $@; ret=$?
    fi
    cleanup_gc; return $?
fi



####### BEGIN configuration #######
# Get proper call args to pass to GenConfig python module. This DOES NOT include
# the /path/to/src that is specified as the last positional argument when
# --cmake-fragment is not specified. For example:
#
# $ source gen_config.sh \
#     --cmake-fragment foo.cmake \  <-|-- gen_config_py_call_args=$@
#     build_name_here               <-|                           (all args)
#
# $ source gen_config.sh \
#     build_name_here \      <-|-- gen_config_py_call_args=${@: 1:$(expr $# - 1)}
#     --force \              <-|                           (all but last arg)
#     /path/to/src
#

# If the last command line argument is a directory...
if [ -d ${@: -1} ]; then
    gen_config_py_call_args=${@: 1:$(expr $# - 1)}  # All but last arg (/path/to/src)
    path_to_src=${@: -1}  # Last arg
else
    if [[ "$@" != *"--cmake-fragment"* ]]; then
        echo "+==============================================================================+"
        echo "|   ERROR:  A valid path to source was not specified as the last positional"
        echo "|           argument. Please correct this like:"
        echo "|"
        echo "|           $ source gen-config.sh \\"
        while [[ $# -gt 0 ]]; do
            echo "|               $1 \\"
            shift
        done
        echo "|               /path/to/src"
        echo "|"
        echo "+==============================================================================+"
        cleanup_gc; return 1
    fi

    gen_config_py_call_args=$@
fi


### Generate the configuration ###
gc_random=$RANDOM
bash_cmake_args_loc=.bash_cmake_args.$gc_random
python3 -E -s ${script_dir}/gen_config.py --bash-cmake-args-location ${bash_cmake_args_loc} $gen_config_py_call_args; ret=$?
if [[ $ret -ne 0 ]]; then
    cleanup_gc; return $?
fi
### ========================== ###


### Run LoadEnv and CMake ###
# Export these for load-env.sh
export cmake_args=$([ -f ${bash_cmake_args_loc} ] && cat ${bash_cmake_args_loc} )
if [[ "$gen_config_py_call_args" == *"--cmake-fragment"* ]]; then
    export have_cmake_fragment="true"
fi
export path_to_src=$(realpath ${path_to_src})
export config_prefix=.do-configure.$gc_random

# This function gets called from WITHIN load-env.sh, either in the current shell
# when --ci-mode is enabled, or from within the sub-shell created by load-env.sh.
function gen_config_helper()
{
    echo -e "\n\n********************************************************************************"
    echo "                      B E G I N  C O N F I G U R A T I O N"
    echo "********************************************************************************"

    if [[ $have_cmake_fragment != "true" ]]; then
        sleep 2s

        echo
        echo "*** Running CMake Command: ***"

        # Print cmake call - use single quotes to defer variable expansion until environment
        #                            is loaded in load-env.sh
        echo -e 'cmake $cmake_args \\\n    $path_to_src 2>&1 | tee ./${config_prefix}.log' | envsubst | tee ./${config_prefix}.sh
        echo

        sleep 2s

        # Execute cmake call
        source ./${config_prefix}.sh
    else
        echo; echo
        echo "Please run:"
        echo
        echo "  $ cmake -C /path/to/fragment.cmake /path/to/src"
        echo
        echo "where \"/path/to/fragment.cmake\" is replaced with your generated cmake fragment file"
        echo "and \"/path/to/src\" is replaced with your build source."
        echo
    fi
}
declare -x -f gen_config_helper

load_env_args=$(python3 -E -s ${script_dir}/gen_config.py --output-load-env-args-only $gen_config_py_call_args); ret=$?
if [[ $ret -ne 0 ]]; then
    cleanup_gc; return $?
fi

# Actually run LoadEnv:
source ${script_dir}/LoadEnv/load-env.sh ${load_env_args}; ret=$?
### ========================== ###

####### END configuration #######

cleanup_gc; return $?
