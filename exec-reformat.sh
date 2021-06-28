#!/usr/bin/env bash

# Source the common helpers script
source scripts/common.bash

printf "${yellow}"
print_banner "Reformatting - Started"
printf "${normal}\n"

execute_command "yapf -vv -i -p -r -e venv- -e .git -e doc -e deps -e __pycache__ ."

printf "${yellow}"
print_banner "Reformatting - Done"
printf "${normal}\n"

