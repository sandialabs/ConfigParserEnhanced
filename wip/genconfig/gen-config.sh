#!/bin/bash

#### BEGIN runnable checks ####

# Ensure that this script is sourced.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]] ; then
  echo "This script must be sourced."
  exit 1
fi

#### END runnable checks ####



#### BEGIN helper functions ####

################################################################################
# cleanup function
#
# This function should be called anytime this script returns control to the
# caller.
################################################################################
# function cleanup()
# {
#    [ -f .load_matching_env_loc ] && rm -f .load_matching_env_loc 2>/dev/null
#    [ -f .ci_mode ] && rm -f .ci_mode 2>/dev/null
#    [ ! -z ${env_file} ]          && rm -f ${env_file} 2>/dev/null; rm -f ${env_file::-2}rc 2>/dev/null

#    unset python_too_old script_dir ci_mode cleanup env_file
#    return 0
# }

#### END helper functions ####



# Get the location to the Python script.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

if [ $# -eq 0 ]; then
  cd ${script_dir} >/dev/null; python3 -E -s -m gen_config --help; cd - >/dev/null
  # cleanup; return 1
  return 1
fi

# Get proper call args to pass to GenConfig python module. This does not include
# the /path/to/src that is specified as the last positional argument when
# --cmake-fragment is not specified. For example:
#
# $ source gen_config.sh \
#     build_name_here \      <-|-- py_call_args=${@:1:$#-1}
#     --force \              <-|                (all but last)
#     /path/to/src
#
# $ source gen_config.sh \
#     --cmake-fragment foo.cmake \  <-|-- py_call_args=$@
#     build_name_here               <-|
#
if [[ $@ != *"--cmake-fragment"* ]]; then
  if [ -d ${@: -1} ]; then
    py_call_args=${@:1:$#-1}
  else
    echo "+==============================================================================+"
    echo "|   ERROR:  A valid path to source was not specified as the last positional"
    echo "|           argument. Please correct this like:"
    echo "|"
    echo "|           source gen-config.sh $1 \\"
    shift
    while [[ $# -gt 0 ]]; do
      echo "|             $1 \\"
      shift
    done
    echo "|"
    echo "+==============================================================================+"
  fi
else
  py_call_args=$@
fi



#### BEGIN environment setup ####
echo "********************************************************************************"
echo "                B E G I N  L O A D I N G  E N V I R O N M E N T"
echo "********************************************************************************"

# Last call arg should be the /path/to/src, not used by load-env.sh
source ${script_dir}/load-env.sh --ci-mode $py_call_args
#### END environment setup ####



#### BEGIN configuration ####
echo -e "\n\n********************************************************************************"
echo "                      B E G I N  C O N F I G U R A T I O N"
echo "********************************************************************************"

# Get the location to the Python script.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

cd ${script_dir} >/dev/null; python3 -E -s -m gen_config $py_call_args; cd - >/dev/null

if [[ -f .bash_cmake_flags_from_gen_config ]]; then
  echo "cmake \\" > .cmake_call
  cat .bash_cmake_flags_from_gen_config >> .cmake_call
  echo ${@: -1} >> .cmake_call

  # Execute cmake
  cmake_call=$(cat .cmake_call)
  rm .cmake_call
  eval $cmake_call
fi
