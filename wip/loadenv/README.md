[![pipeline status](https://internal.gitlab.server/trilinos-devops-consolidation/code/loadenv/badges/master/pipeline.svg)](https://internal.gitlab.server/trilinos-devops-consolidation/code/loadenv/-/commits/master)
[![coverage report](https://internal.gitlab.server/trilinos-devops-consolidation/code/loadenv/badges/master/coverage.svg)](http://10.202.35.89:8080/LoadEnv/coverage/index.html)
[![Generic badge](https://img.shields.io/badge/docs-latest-green.svg)](http://10.202.35.89:8080/LoadEnv/doc/index.html)

# LoadEnv

> **Note:**  The following README contents are just a placeholder until this
> tool is more polished.

`LoadEnv` is a tool to allow you to consistently load reproducible
environments.

## Getting Started

1. Ensure your proxy environment variables are set appropriately:
   ```bash
   export HTTP_PROXY=http://user:nopass@proxy.sandia.gov:80
   export http_proxy=$HTTP_PROXY
   export HTTPS_PROXY=$HTTP_PROXY
   export https_proxy=$HTTPS_PROXY
   # ensure NO_PROXY and no_proxy contain .sandia.gov
   ```

2. Ensure your public ssh key is added to your gitlab-ex account:
   ```bash
   cat ~/.ssh/id_rsa.pub
   ```
   Copy the public key and add it to
   https://internal.gitlab.server/-/profile/keys via your browser.

3. Clone the repository:
   ```bash
   git clone git@internal.gitlab.server:trilinos-devops-consolidation/code/loadenv
   ```

4. Get a Python 3.6+ in your path:
   *  ASCIC/Chama/Eclipse/Stria:  `module load sparc-tools/python/3.7.9`
   *  Mutrino:  `module load cray-python/3.8.2.1`
   *  Vortex:  `module load anaconda3/4.8.2-python-3.7.6`

5. Install the requirements:
   ```bash
    cd loadenv
   ./install_reqs.sh
   ```

6. Use the script:
   ```bash
   source load-env.sh --help
   source load-env.sh --list-envs
   source load-env.sh <build-name>
   source load-env.sh Project-Name-build-Trilinos-rhel7-clang-openmp-opt-static # e.g.
   #                                                    ^__________^___ environment alias
   ```

> **Note:**  The first run of `load-env.sh` may take some time as Python
> generates byte-code for the requirements.

> **Note:**  You may have to repeat step 4 above after running `source
> load-env.sh` since `load-env.sh` may run `module purge`.
