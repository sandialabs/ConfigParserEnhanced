#!/usr/bin/env bash

# Source the common helpers script.
source scripts/common.bash

options=(
    -m pip
    uninstall
    -y
    -r requirements.txt
)

cmd="python3 ${options[@]}"
execute_command_checked "${cmd}"


