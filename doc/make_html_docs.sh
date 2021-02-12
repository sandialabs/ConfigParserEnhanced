#!/usr/bin/env bash

sphinx-build -b html source/ html/

err=$?

echo -e "\nIf you ran this on your local machine, you can open them with\n"
echo -e "  open html/index.html\n"

if [ ${err} -ne 0 ]; then
    echo -e "${red}<<<FAILED>>>${normal}"
    exit $err
fi

