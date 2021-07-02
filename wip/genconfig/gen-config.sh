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
  cleanup; return 1
fi

if [[ "${python_too_old}" == "True" ]]; then
  echo "This script requires Python 3.6+."
  echo "Your current python3 is only $(python3 --version)."
  cleanup; return 1
fi

#### END runnable checks ####



#### BEGIN helper functions ####

################################################################################
# cleanup function
#
# This function should be called anytime this script returns control to the
# caller.
################################################################################
function cleanup()
{
   [ -f .load_matching_env_loc ] && rm -f .load_matching_env_loc 2>/dev/null
   [ -f .ci_mode ] && rm -f .ci_mode 2>/dev/null
   [ ! -z ${env_file} ] && rm -f ${env_file} 2>/dev/null; rm -f ${env_file::-2}rc 2>/dev/null
   [ -f .bash_cmake_flags_from_gen_config ] && rm -f .bash_cmake_flags_from_gen_config 2>/dev/null

   unset python_too_old script_dir ci_mode cleanup env_file gen_config_py_call_args
   unset path_to_src load_env_call_args cmake_call full_load_env_args
   return 0
}

#### END helper functions ####



# Get the location to the Python script.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

if [ $# -eq 0 ]; then
  cd ${script_dir} >/dev/null; python3 -E -s -m gen_config --help; cd - >/dev/null
  # cleanup; return 1
  return 1
fi

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
cd - >/dev/null
load_env_call_args=$(cat .load_env_args)
rm .load_env_args


#### BEGIN environment setup ####
echo "********************************************************************************"
echo "                B E G I N  L O A D I N G  E N V I R O N M E N T"
echo "********************************************************************************"

if [ ! -z $LOAD_ENV_INTERACTIVE_MODE ]; then
  echo "* Environment already loaded in interactive mode. Skipping..."
else
    full_load_env_args="--ci-mode $load_env_call_args"
    echo "*** Running LoadEnv Command: ***"
    echo -e "\$ source ${script_dir}/deps/LoadEnv/load-env.sh \\ \n    $(echo $full_load_env_args | sed 's/ / \\ \\n    /g')\n"
    source ${script_dir}/deps/LoadEnv/load-env.sh "$full_load_env_args"
fi
#### END environment setup ####



#### BEGIN configuration ####
echo -e "\n\n********************************************************************************"
echo "                      B E G I N  C O N F I G U R A T I O N"
echo "********************************************************************************"

# Get the location to the Python script.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

cd ${script_dir} >/dev/null; python3 -E -s -m gen_config $gen_config_py_call_args; cd - >/dev/null

if [[ -f .bash_cmake_flags_from_gen_config && $path_to_src != "" ]]; then
  echo
  echo "*** Running CMake Command: ***"
  echo "\$ cmake $(cat .bash_cmake_flags_from_gen_config) \\" > .cmake_call
  echo "    $path_to_src" >> .cmake_call

  # Print cmake call
  cmake_call=$(cat .cmake_call)
  rm .cmake_call
  echo $cmake_call
  echo

  # Execute cmake call
  eval $cmake_call
fi
