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



#### BEGIN environment setup ####
echo "********************************************************************************"
echo "                B E G I N  L O A D I N G  E N V I R O N M E N T"
echo "********************************************************************************"

source ${script_dir}/load-env.sh --ci-mode $@
#### END environment setup ####



#### BEGIN configuration ####
echo -e "\n\n********************************************************************************"
echo "                      B E G I N  C O N F I G U R A T I O N"
echo "********************************************************************************"

# Get the location to the Python script.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

if [[ $@ == *"--cmake-fragment"* ]]; then
  cd ${script_dir} >/dev/null; python3 -E -s -m gen_config $@; cd - >/dev/null
else
  cd ${script_dir} >/dev/null
  cmake $(python3 -E -s -m gen_config $@)
  cd - >/dev/null
fi
