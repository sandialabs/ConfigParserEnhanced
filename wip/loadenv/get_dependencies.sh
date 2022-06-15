#!/bin/bash
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

pushd $PWD

# snapshot dependencies in 
cd ${script_dir}
git submodule update --init --remote || true
cd -

# Point to some example ini files
cd ${script_dir}/ini_files
ln -sf ../examples/atdm/environment-specs.ini
ln -sf ../examples/atdm/supported-envs.ini
ln -sf ../examples/atdm/supported-systems.ini
cd -

popd
