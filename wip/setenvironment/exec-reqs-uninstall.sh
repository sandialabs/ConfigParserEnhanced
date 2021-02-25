#!/usr/bin/env bash
#
# Uninstall requirements and this project (if it's installed)
#



# Source the common helpers script.
source scripts/common.bash

python_exe="python3"
projectname="setenvironment"

options=(
    -m pip
    uninstall
    -y
    -r requirements.txt
)

cmd="${python_exe} ${options[@]} ${projectname}"
execute_command_checked "${cmd}"

