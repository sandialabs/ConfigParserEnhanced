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



#### BEGIN environment setup ####
# Get the location to the Python script.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
echo $script_dir

source $script_dir/deps/LoadEnv/load-env.sh
