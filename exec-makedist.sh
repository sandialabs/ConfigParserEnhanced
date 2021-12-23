#!/usr/bin/env bash

# Source the common helpers script
source scripts/common.bash

printf "${yellow}"
print_banner "Build Distribution - Started"
printf "${normal}\n"

execute_command "rm -rf dist"
execute_command_checked "python3 -m build"

# Upload to TEST PyPi
execute_command_checked "python3 -m twine upload --repository testpypi dist/*"

# Upload to production PyPi
# execute_command_checked "python3 -m twine upload dist/*"

printf "${yellow}"
print_banner "Make Distribution - Done"
printf "${normal}\n"
