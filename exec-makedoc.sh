#!/usr/bin/env bash

# Source the common helpers script
source scripts/common.bash

printf "${yellow}"
print_banner "Make Documentation - Started"
printf "${normal}\n"

execute_command "python3 -m pip uninstall -y configparserenhanced > _test-uninstall-cpe.log 2>&1"

cd doc
execute_command_checked "./make_html_docs.sh"

printf "${yellow}"
print_banner "Make Documentation - Done"
printf "${normal}\n"
