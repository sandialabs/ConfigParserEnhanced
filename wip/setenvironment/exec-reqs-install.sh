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

options=(
    -m pip
    install
    --user
    -r requirements.txt
)

cmd="${python_exe} ${options[@]}"
execute_command_checked "${cmd}"

