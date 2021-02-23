#!/usr/bin/env bash
#
# Install just the dependencies of this project (not the project itself)
# into the local user space.
#

python_exe="python3"

# Source the common helpers script.
source scripts/common.bash

options=(
    -m pip
    install
    --user
    -r requirements.txt
)

cmd="${python_exe} ${options[@]}"
execute_command_checked "${cmd}"

