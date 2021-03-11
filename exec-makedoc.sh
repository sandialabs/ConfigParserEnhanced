#!/usr/bin/env bash

python3 -m pip uninstall -y configparserenhanced

cd doc
./make_html_docs.sh
err=$?
exit $err

