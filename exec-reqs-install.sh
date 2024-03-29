#!/usr/bin/env bash
#
# Install just the dependencies of this project (not the project itself)
# into the local user space.
#

# Source the common helpers script.
source scripts/common.bash

printf "${yellow}"
print_banner "INSTALL REQUIRED PACKAGES"
printf "${normal}"

python_exe="python3"

execute_command "which ${python_exe:?}"
execute_command "${python_exe:?} --version"

opt_venv='--user'
if [ ! -z ${VIRTUAL_ENV} ]; then
    opt_venv=''
fi

options=(
    -m pip
    install
    ${opt_venv}
    -r requirements.txt
    -r requirements-test.txt
    -r doc/requirements.txt
)

cmd="${python_exe} ${options[@]}"
execute_command_checked "${cmd} > _test-reqs-install.log 2>&1"

