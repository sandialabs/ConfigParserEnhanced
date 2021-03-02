#!/usr/bin/env bash

./exec-reqs-install.sh

cd doc
./make_html_docs.sh
err=$?
exit $err

