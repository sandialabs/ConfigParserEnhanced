#!/usr/bin/env bash

opt_venv='--user'
if [ ! -z ${VIRTUAL_ENV} ]; then
    opt_venv=''
fi


if [ -e html ]; then
    rm -rf html
fi

sphinx-build -b html source/ html/ -W

err=$?
if [ ${err} -ne 0 ]; then
    echo -e "${red}<<<FAILED>>>${normal}"
    exit $err
fi

echo -e "\nIf you ran this on your local machine, you can open them with\n"
echo -e "  open html/index.html\n"
