#!/usr/bin/env bash
#
# Uninstall requirements and this project (if it's installed)
#

# Source the common helpers script.
source scripts/common.bash

python_exe="python3"
projectname="setconfiguration"

execute_command "which ${python_exe:?}"
execute_command "${python_exe:?} --version"

options=(
    -m pip
    uninstall
    -y
    -r requirements.txt
    -r requirements-test.txt
)

cmd="${python_exe} ${options[@]} ${projectname}"
execute_command_checked "${cmd} > _test-reqs-uninstall.log 2>&1"


