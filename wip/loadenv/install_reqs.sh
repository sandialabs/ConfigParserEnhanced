#!/bin/bash
export HTTPS_PROXY=http://user:nopass@proxy.sandia.gov:80
pip_args="--trusted-host=pypi.org --trusted-host=files.pythonhosted.org --trusted-host=pypi.python.org install --user -U"

rm -rf deps > /dev/null 2>&1; mkdir deps; cd deps
git clone git@internal.gitlab.server:trilinos-devops-consolidation/code/ConfigParserEnhanced.git
git clone git@internal.gitlab.server:trilinos-devops-consolidation/code/SetEnvironment.git
git clone git@internal.gitlab.server:trilinos-devops-consolidation/code/DetermineSystem.git
cd -

# deps
python3 -m pip $pip_args pip pytest pytest-cov

# no-deps
python3 -m pip $pip_args --no-deps ./deps/*
