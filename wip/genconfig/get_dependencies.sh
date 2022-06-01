#!/bin/bash
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

pushd $PWD

cd ${script_dir}
git sudmodule update --init --remote || true
cd -

popd
