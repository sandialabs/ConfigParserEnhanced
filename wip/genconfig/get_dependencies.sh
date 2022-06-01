#!/bin/bash
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

pushd $PWD

cd ${script_dir}
git submodule update --init --remote || true
cd -

popd
