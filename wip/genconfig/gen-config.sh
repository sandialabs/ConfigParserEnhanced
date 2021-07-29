#!/bin/bash

####### BEGIN runnable checks #######
# Ensure that this script is sourced.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]] ; then
    echo "This script must be sourced."
    exit 1
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
    [ -f /tmp/$USER/.bash_cmake_args_loc ] && rm -f /tmp/$USER/.bash_cmake_args_loc 2>/dev/null
    [ -f /tmp/$USER/.load_env_args ] && rm -f /tmp/$USER/.load_env_args 2>/dev/null

    unset python_too_old script_dir cleanup_gc gen_config_py_call_args gen_config_helper
    unset path_to_src load_env_call_args cmake_args_file
    trap -  SIGHUP SIGINT SIGTERM
    return 0
}
trap "cleanup_gc; return 1" SIGHUP SIGINT SIGTERM
####### END helper functions #######



# Get the location to the Python script in a subshell. cd does not change the previous
# working directory of the caller since this is run in a subshell.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

# If no command line args were provided, show the --help
if [[ $# -eq 0 || "$@" == *"--help"* ]]; then
    python3 -E -s ${script_dir}/gen_config.py --help
    cleanup_gc; return 1
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
    if [[ $@ != *"--cmake-fragment"* ]]; then
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
python3 -E -s ${script_dir}/gen_config.py $gen_config_py_call_args; ret=$?
if [[ $ret -ne 0 ]]; then
    cleanup_gc; return $ret
fi
### ========================== ###


### Run LoadEnv and CMake ###
# Export these for load-env.sh
export cmake_args_file=$([ -f /tmp/$USER/.bash_cmake_args_loc ] && cat /tmp/$USER/.bash_cmake_args_loc)
rm -f /tmp/$USER/.bash_cmake_args_loc 2>/dev/null
export path_to_src

# This function gets called from WITHIN load-env.sh, either in the current shell
# when --ci-mode is enabled, or from within the sub-shell created by load-env.sh.
function gen_config_helper()
{
    echo -e "\n\n********************************************************************************"
    echo "                      B E G I N  C O N F I G U R A T I O N"
    echo "********************************************************************************"

    if [[ -f $cmake_args_file && $path_to_src != "" ]]; then
        sleep 2s

        echo
        echo "*** Running CMake Command: ***"
        cmake_args="$(cat $cmake_args_file | envsubst)"

        # Print cmake call
        echo -e "cmake $cmake_args \\\n    $path_to_src" | sed 's/;/\\;/g' | tee ./do-configure.sh
        echo

        sleep 2s

        # Execute cmake call
	source ./do-configure.sh
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

# Get proper call args to pass to LoadEnv, which ARE NOT the same as those we pass to GenConfig.
python3 -E -s ${script_dir}/gen_config.py $gen_config_py_call_args --save-load-env-args /tmp/$USER/.load_env_args; ret=$?
if [[ $ret -ne 0 ]]; then
    cleanup_gc; return $ret
fi
load_env_call_args=$(cat /tmp/$USER/.load_env_args)

# Actually run LoadEnv:
source ${script_dir}/LoadEnv/load-env.sh ${load_env_call_args}
### ========================== ###

####### END configuration #######

cleanup_gc
