#!/bin/bash
export PATH=/ascldap/users/trilinos/.local/bin:$PATH

sphinx-build -W -b html source/ html/
if [ $? -eq 0 ]; then
    echo "\nIf you ran this on your local machine, you can open them with\n"
    echo "  open html/index.html\n"
else
    exit 1
fi
