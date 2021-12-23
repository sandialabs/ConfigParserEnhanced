#!/usr/bin/env bash

# Source the common helpers script
source scripts/common.bash

printf "${yellow}"
print_banner "Build Distribution - Started"
printf "${normal}\n"

execute_command "rm -rf dist"
execute_command_checked "python3 -m build"

# Upload to TEST PyPi
options=( No Yes )
message_std ""
message_std "${yellow}Upload distribution to ${red}test pypi${normal}:"
upload_to_test_pypi=$(select_with_default "${options[@]}")
if [[ ${upload_to_test_pypi:?} == "Yes" ]]; then
    message_std "${cyan}Yes${normal}"
    execute_command_checked "python3 -m twine upload --repository testpypi dist/*"
else
    message_std "${cyan}No${normal}"
fi

# Upload to production PyPi
message_std ""
message_std "${yellow}Upload distribution to ${red}production pypi${normal}:"
upload_to_prod_pypi=$(select_with_default "${options[@]}")
if [[ ${upload_to_prod_pypi:?} == "Yes" ]]; then
    message_std "${cyan}Yes${normal}"
    execute_command_checked "python3 -m twine upload dist/*"
else
    message_std "${cyan}No${normal}"
fi

printf "${yellow}"
print_banner "Make Distribution - Done"
printf "${normal}\n"
