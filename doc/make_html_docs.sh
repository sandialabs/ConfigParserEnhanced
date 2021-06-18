#!/usr/bin/env bash

# detect virtual env, can't install into --user within a venv.
opt_venv='--user'
if [ ! -z ${VIRTUAL_ENV} ]; then
    opt_venv=''
fi

python3 -m pip install ${opt_venv} -r requirements.txt

sphinx-build -b html source/ html/ -W

err=$?

echo -e "\nIf you ran this on your local machine, you can open them with\n"
echo -e "  open html/index.html\n"

if [ ${err} -ne 0 ]; then
    echo -e "${red}<<<FAILED>>>${normal}"
    exit $err
fi

