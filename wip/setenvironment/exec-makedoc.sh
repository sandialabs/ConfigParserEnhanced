#!/usr/bin/env bash

cd doc
./make_html_docs.sh
err=$?
exit $err

