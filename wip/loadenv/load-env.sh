#!/bin/bash


#### BEGIN runnable checks ####

# Ensure that this script is sourced.
if [ "${BASH_SOURCE[0]}" == "${0}" ] ; then
  echo "This script must be sourced."
  exit 1
fi

if [ ! -z $LOAD_ENV_INTERACTIVE_MODE ]; then
  echo "+==============================================================================+"
  echo "|   ERROR:  An environment is already loaded."
  echo "|           Type \"exit\" before loading another environment."
  echo "+==============================================================================+"

  return 1
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
   [ ! -z ${env_file} ]          && rm -f ${env_file} 2>/dev/null; rm -f ${env_file::-2}rc 2>/dev/null

   unset python_too_old script_dir ci_mode cleanup env_file
   return 0
}

#### END helper functions ####



#### BEGIN environment setup ####

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

# Get the location to the Python script.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

# Ensure that an argument is supplied.
if [ $# -eq 0 ]; then
  cd ${script_dir} >/dev/null; python3 -E -s -m loadenv --help; cd - >/dev/null
  cleanup; return 1
fi

# Check for Continuous Integration mode.
ci_mode=0
if [[ "$1" == "--ci_mode" ]]; then
    ci_mode=1
    echo "+==============================================================================+"
    echo "|   WARNING:  ci mode is enabled."
    echo "|             Your current environment will be overwritten."
    echo "+==============================================================================+"
    shift
fi

# Pass the input on to LoadEnv.py to do the real work.
cd ${script_dir} >/dev/null; python3 -E -s -m loadenv $@; cd - >/dev/null
if [[ $? -ne 0 ]]; then
  cleanup; return $?
fi

# Source the generated script to pull the environment into the current shell.
if [ -f .load_matching_env_loc ]; then
  env_file=$(cat .load_matching_env_loc)

  if [ -f ${env_file} ]; then
    echo "source ${env_file}"                                                                          > ${env_file::-2}rc
    echo "echo; echo; echo"                                                                           >> ${env_file::-2}rc
    echo "echo \"********************************************************************************\""  >> ${env_file::-2}rc
    echo "echo \"           E N V I R O N M E N T  L O A D E D  S U C E S S F U L L Y\""              >> ${env_file::-2}rc
    echo "echo \"********************************************************************************\""  >> ${env_file::-2}rc

    # Enter subshell and set prompt by default
    if [[ $ci_mode -eq 0 ]]; then
      echo "echo; echo; echo"                                                                           >> ${env_file::-2}rc
      echo "echo \"********************************************************************************\""  >> ${env_file::-2}rc
      echo "echo \"          T Y P E  \"exit\"  T O  L E A V E  T H E  E N V I R O N M E N T\""         >> ${env_file::-2}rc
      echo "echo \"********************************************************************************\""  >> ${env_file::-2}rc
      echo "export PS1=\"(\$LOADED_ENV_NAME) $ \""                                                      >> ${env_file::-2}rc
      echo "export LOAD_ENV_INTERACTIVE_MODE=\"True\""                                                  >> ${env_file::-2}rc
      /bin/bash --init-file ${env_file::-2}rc -i
    else
      # Intentionally do no invoke cleanup() if this exits such that artifacts in /tmp/$USER are preserved.
      source ${env_file::-2}rc
    fi

  else
    echo "load_env.py failed to generate ${env_file}."
    echo "Unable to load the environment."
    cleanup; return 1
  fi
fi

cleanup

#### END environment setup ####
