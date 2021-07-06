#!/bin/bash

#### BEGIN runnable checks ####

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

#### END runnable checks ####



#### BEGIN helper functions ####

################################################################################
# cleanup function
#
# This function should be called anytime this script returns control to the
# caller.
################################################################################
function cleanup_gc()
{
   [ -f .bash_cmake_flags_from_gen_config ] && rm -f .bash_cmake_flags_from_gen_config 2>/dev/null
   [ -f ${script_dir}/.pwd ] && rm -f ${script_dir}/.pwd 2>/dev/null

   unset python_too_old script_dir cleanup_gc gen_config_py_call_args gen_config_helper
   unset gc_working_dir path_to_src load_env_call_args cmake_call full_load_env_args
   return 0
}

#### END helper functions ####



# Get the location to the Python script.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

if [ $# -eq 0 ]; then
  cd ${script_dir} >/dev/null; python3 -E -s -m gen_config --help; cd - >/dev/null
  # cleanup_gc; return 1
  return 1
fi

#### BEGIN configuration ####

# Get proper call args to pass to GenConfig python module. This DOES NOT include
# the /path/to/src that is specified as the last positional argument when
# --cmake-fragment is not specified. For example:
#
# $ source gen_config.sh \
#     --cmake-fragment foo.cmake \  <-|-- gen_config_py_call_args=$@
#     build_name_here               <-|                (all args)
#
# $ source gen_config.sh \
#     build_name_here \      <-|-- gen_config_py_call_args=${@: 1:$(expr $# - 1)}
#     --force \              <-|                (all but last)
#     /path/to/src
#
if [[ $@ != *"--cmake-fragment"* ]]; then
  if [ -d ${@: -1} ]; then
    gen_config_py_call_args=${@: 1:$(expr $# - 1)}
    path_to_src=${@: -1}
  else
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
    return 1
  fi
else
  gen_config_py_call_args=$@
fi


# Get proper call args to pass to LoadEnv, which ARE NOT the same as those we pass to GenConfig.
cd ${script_dir} >/dev/null
python3 -E -s -m gen_config $gen_config_py_call_args --save-load-env-args .load_env_args
if [[ $? -ne 0 ]]; then
  cleanup_gc; return $?
fi
load_env_call_args=$(cat .load_env_args)
rm -f .load_env_args 2>/dev/null
cd - >/dev/null


python3 -E -s ${script_dir}/gen_config.py $gen_config_py_call_args
if [[ $? -ne 0 ]]; then
  cleanup_gc; return $?
fi

# Export these for load-env.sh
export gc_working_dir=$PWD
export path_to_src
export gc_working_dir
export cmake_args

function gen_config_helper()
{
    echo -e "\n\n********************************************************************************"
    echo "                      B E G I N  C O N F I G U R A T I O N"
    echo "********************************************************************************"

    sleep 2s

    if [[ -f $gc_working_dir/.bash_cmake_flags_from_gen_config && $path_to_src != "" ]]; then
	echo
	echo "*** Running CMake Command: ***"
	cmake_args="$(cat $gc_working_dir/.bash_cmake_flags_from_gen_config) \\ \n    $path_to_src"

	# Print cmake call
	echo -e "\$ cmake $cmake_args"
	echo

	sleep 2s

	# Execute cmake call
	cmake $cmake_args
    fi
}
declare -x -f gen_config_helper

source ${script_dir}/load-env.sh ${load_env_call_args}
#### END configuration ####

cleanup_gc
