#!/usr/bin/env bash

# Source the common helpers script
source scripts/common.bash

printf "${yellow}"
print_banner "Cleanup - Started"
printf "${normal}\n"


execute_command "find . -name '*.py?' -exec rm {} \;"
execute_command "find . -name '__pycache__' -exec rm -rf {} \;"
execute_command "find . -name '.DS_Store' -exec rm {} \;"
execute_command "find . -name '._.DS_Store' -exec rm {} \;"
execute_command "find . -maxdepth 2 -name '_test-*.log' -exec rm {} \;"
execute_command "find . -maxdepth 1 -name '___*.ini' -exec rm {} \;"

execute_command "rm -rf build          > /dev/null 2>&1"
execute_command "rm -rf tests/htmlcov  > /dev/null 2>&1"
execute_command "rm -rf doc/html       > /dev/null 2>&1"
execute_command "rm -rf dist           > /dev/null 2>&1"
execute_command "rm -rf tests          > /dev/null 2>&1"
execute_command "rm -rf .pytest_cache  > /dev/null 2>&1"
execute_command "rm .coverage          > /dev/null 2>&1"

printf "${yellow}"
print_banner "Cleanup - Done"
printf "${normal}\n"
