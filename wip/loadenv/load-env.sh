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

# Create a virtual environment for running the LoadEnv tool
if [[ ! -d "${script_dir}/virtual_env" ]]; then
	python3 -m venv --copies ${script_dir}/virtual_env
fi
source ${script_dir}/virtual_env/bin/activate
unset PYTHONPATH
if [[ $(python3 -c "import setenvironment" &> /dev/null; echo $?) -ne 0 ]]; then
	${script_dir}/install_reqs.sh
fi

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

# Get out of the virtual environment
deactivate

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
