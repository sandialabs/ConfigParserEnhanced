#!/bin/bash

# Ensure that this script is sourced.
if [ "${BASH_SOURCE[0]}" == "${0}" ] ; then
  echo "This script must be sourced."
  exit 1
fi

# Ensure the python3 in the user's environment is high enough.
python_too_old=$(python3 -c 'import sys; print(sys.version_info < (3, 6))')
if [[ "${python_too_old}" == "True" ]]; then
  echo "This script requires Python 3.6+."
  echo "Your current `python3` is only $(python3 --version)."
  return 1
fi

# Get the location to the Python script.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
load_env_py=${script_dir}/loadenv/LoadEnv.py

# Ensure that an argument is supplied.
if [ $# -eq 0 ]; then
  ${load_env_py} --help                                                          # Might need to change this help text slightly.
  return 1
fi

# Pass the input on to LoadEnv.py to do the real work.
${load_env_py} $@
if [[ $? -ne 0 ]]; then
  return $?
fi

# Source the generated script to pull the environment into the current shell.
if [ -f .load_matching_env_loc ]; then
  env_file=$(cat .load_matching_env_loc)
  rm -f .load_matching_env_loc

  if [ -f ${env_file} ]; then
    source ${env_file}
    rm -f ${env_file}
    echo "Environment loaded successfully."
  else
    echo "load_env.py failed to generate ${env_file}."
    echo "Unable to load the environment."
    return 1
  fi
fi
