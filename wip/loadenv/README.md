[![pipeline status](https://internal.gitlab.server/trilinos-devops-consolidation/code/loadenv/badges/master/pipeline.svg)](https://internal.gitlab.server/trilinos-devops-consolidation/code/loadenv/-/commits/master)
[![coverage report](https://internal.gitlab.server/trilinos-devops-consolidation/code/loadenv/badges/master/coverage.svg)](http://10.202.35.89:8080/LoadEnv/coverage/index.html)
[![Generic badge](https://img.shields.io/badge/docs-latest-green.svg)](http://10.202.35.89:8080/LoadEnv/doc/index.html)

# LoadEnv

> **Note:**  The following README contents are just a placeholder until this
> tool is more polished.

`LoadEnv` is a tool to allow you to consistently load reproducible
environments.

## Getting Started

1. Ensure your public ssh key is added to your gitlab-ex account:
   ```bash
   cat ~/.ssh/id_rsa.pub
   ```
   Copy the public key and add it to
   https://internal.gitlab.server/-/profile/keys via your browser.

2. Clone the repository:
   ```bash
   git clone git@internal.gitlab.server:trilinos-devops-consolidation/code/loadenv
   ```

3. Get a Python 3.6+ in your path, the following have been verified to work:
   *  ASCIC/Chama/Eclipse/Stria:  `module load sparc-tools/python/3.7.9`
   *  Mutrino:  `module load cray-python/3.8.2.1`
   *  Vortex:  `module load anaconda3/4.8.2-python-3.7.6`

4. Install the requirements:
   ```bash
    cd loadenv
   ./install_reqs.sh
   ```

5. Use the script:
   ```bash
   source load-env.sh --help
   source load-env.sh --list-envs
   source load-env.sh <build-name>
   source load-env.sh Project-Name-build-Trilinos-rhel7-clang-openmp-opt-static # e.g.
   #                                                    ^__________^___ environment alias
   exit
   ```

> **Note:**  The first run of `load-env.sh` may take some time as Python
> generates byte-code for the requirements.

### Interactive mode
```bash
source load-env.sh <build-name>
```

By default, `load-env.sh` runs in interactive mode. In this mode, `load-env.sh` drops the user
to a subshell where the environment is loaded. In this way, when the user is done, they can
return to their previous environment by typing `exit`. This mode is often useful in development
environments when user's are creating new environments by modifying ini files.

### CI mode
```bash
source load-env.sh --ci-mode <build-name>
```

When passing the `--ci-mode` flag to `load-env.sh`, your current shell's environment will be
overwritten by `load-env.sh`. This mode is often useful in production environments when running
`load-env.sh` from a CI driver script.


## Using LoadEnv in your python code

### Installing requirements
You will need to follow the [Getting Started](https://internal.gitlab.server/trilinos-devops-consolidation/code/loadenv#getting-started)
instructions up through step 4. before attempting to load the LoadEnv module.

### LoadEnv API Documentation
Please click the 'docs' badge at the top of this file or navigate [here](https://internal.gitlab.server/trilinos-devops-consolidation/code/loadenv#getting-started)
 with your browser for the LoadEnv API documentation.

> **Note:** when using LoadEnv in your python code, the environment will only
exist in the python process you've run `import LoadEnv` from, not the shell which that
python process was run from.
