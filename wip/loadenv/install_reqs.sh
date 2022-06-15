#!/bin/bash
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

pushd $PWD

cd ${script_dir}
rm -rf deps > /dev/null 2>&1; mkdir deps; cd deps
git clone git@internal.gitlab.server:trilinos-devops-consolidation/code/ConfigParserEnhanced.git
git clone git@internal.gitlab.server:trilinos-devops-consolidation/code/SetEnvironment.git
git clone git@internal.gitlab.server:trilinos-devops-consolidation/code/DetermineSystem.git
git clone git@internal.gitlab.server:trilinos-devops-consolidation/code/KeywordParser.git
cd -

# snapshot dependencies in
ln -sf deps/SetEnvironment/src/setenvironment/ .
ln -sf deps/ConfigParserEnhanced/src/configparserenhanced/ .
ln -sf deps/DetermineSystem/determinesystem/ .
ln -sf deps/KeywordParser/keywordparser/ .

# Point to some example ini files
cd ${script_dir}/ini_files
ln -sf ../examples/atdm/environment-specs.ini
ln -sf ../examples/atdm/supported-envs.ini
ln -sf ../examples/atdm/supported-systems.ini
cd -

popd
