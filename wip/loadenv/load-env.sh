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

# Create a virtual environment for running the LoadEnv tool
if [[ ! -d "${script_dir}/virtual_env" ]]; then
  python3 -m venv ${script_dir}/virtual_env
fi

if [[ $? -eq 0 && -e ${script_dir}/virtual_env/bin/activate ]]; then
    source ${script_dir}/virtual_env/bin/activate
else
    echo "Error creating virtual_env directory"
    return 1
fi

# Ensure that an argument is supplied.
if [ $# -eq 0 ]; then
  cd ${script_dir} >/dev/null; python3 -E -s -m loadenv --help; cd - >/dev/null
  deactivate
  return 1
fi

ci_mode=0
# Pass the input on to LoadEnv.py to do the real work.
if [[ "$1" == "--ci_mode" ]]; then
    ci_mode=1
    echo "!!! Warning !!!"
    echo "ci mode is enabled. Your current environment will be overwritten."
    echo "!!! Warning !!!"
    shift
fi

cd ${script_dir} >/dev/null; python3 -E -s -m loadenv $@; cd - >/dev/null
if [[ $? -ne 0 ]]; then
  deactivate
  return $?
fi

# Get out of the virtual environment
deactivate

# Source the generated script to pull the environment into the current shell.
if [ -f .load_matching_env_loc ]; then
  env_file=$(cat .load_matching_env_loc)
  rm -f .load_matching_env_loc

  if [ -f ${env_file} ]; then
    echo "source ${env_file}" > ${script_dir}/virtual_env/.envrc
    echo "rm -f ${env_file}" >> ${script_dir}/virtual_env/.envrc
    echo "unset ci_mode python_too_old script_dir" >> ${script_dir}/virtual_env/.envrc
    echo "echo; echo; echo" >> ${script_dir}/virtual_env/.envrc
    echo "echo \"********************************************************************************\""  >> ${script_dir}/virtual_env/.envrc
    echo "echo \"           E N V I R O N M E N T  L O A D E D  S U C E S S F U L L Y\"" >> ${script_dir}/virtual_env/.envrc
    echo "echo \"********************************************************************************\""  >> ${script_dir}/virtual_env/.envrc

    # Enter subshell and set prompt by default
    if [[ $ci_mode -eq 0 ]]; then
      echo "echo; echo; echo" >> ${script_dir}/virtual_env/.envrc
      echo "echo \"********************************************************************************\""  >> ${script_dir}/virtual_env/.envrc
      echo "echo \"          T Y P E  \"exit\"  T O  L E A V E  T H E  E N V I R O N M E N T\"" >> ${script_dir}/virtual_env/.envrc
      echo "echo \"********************************************************************************\""  >> ${script_dir}/virtual_env/.envrc
      echo "export PS1=\"(${@: -1}) $ \"" >> ${script_dir}/virtual_env/.envrc
      /bin/bash --init-file ${script_dir}/virtual_env/.envrc -i
    else
      source ${script_dir}/virtual_env/.envrc
    fi

  else
    echo "load_env.py failed to generate ${env_file}."
    echo "Unable to load the environment."
    return 1
  fi
fi
