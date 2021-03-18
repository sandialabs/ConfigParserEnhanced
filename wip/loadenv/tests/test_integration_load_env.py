from configparserenhanced import ConfigParserEnhanced
from pathlib import Path
import pytest
import sys
from unittest.mock import patch

root_dir = (Path.cwd()/".."
            if (Path.cwd()/"conftest.py").exists()
            else Path.cwd())

sys.path.append(str(root_dir))
from load_env import LoadEnv

load_env_ini_data = ConfigParserEnhanced(
    root_dir/"tests/supporting_files/test_load_env.ini"
).configparserenhanceddata["load-env"]


##################################
#  EnvKeywordParser Integration  #
##################################
@pytest.mark.parametrize("inputs", [
    {
        "build_name": "intel",
        "hostname": "mutrino",
        "expected_env": "machine-type-1-intel-18.0.5-mpich-7.7.6"
    },
    {
        "build_name": "arm",
        "hostname": "stria",
        "expected_env": "machine-type-4-arm-20.0-openmpi-4.0.2"
    }
])
@pytest.mark.parametrize("prog_cmd", ["prog", "cmd"])
@patch("load_env.socket")
def test_ekp_matches_correct_env_name(mock_socket, prog_cmd, inputs):
    ###########################################################################
    # **This will need to change later once we have a more sophisticated**
    # **system determination in place.**
    ###########################################################################
    mock_socket.gethostname.return_value = inputs["hostname"]

    if prog_cmd == "prog":
        le = LoadEnv(
            build_name=inputs["build_name"],
        )
    else:
        le = LoadEnv(argv=[
            inputs["build_name"],
        ])

    assert le.parsed_env_name == inputs["expected_env"]


###################################################
#  EnvKeywordParser + SetEnvironment Integration  #
###################################################
@pytest.mark.parametrize("inputs", [
    {
        "build_name": "intel",
        "hostname": "mutrino",
        "expected_env": "machine-type-1-intel-18.0.5-mpich-7.7.6",
        "expected_cmds": [
            "module load sparc-dev/intel-18.0.5_mpich-7.7.6",
            "envvar_op prepend PATH /projects/netpub/atdm/ninja-1.8.2/bin",
            "envvar_op set TEST_MATCHED_ENV machine-type-1-intel-18.0.5-mpich-7.7.6",
        ],
    },
    {
        "build_name": "arm",
        "hostname": "stria",
        "expected_env": "machine-type-4-arm-20.0-openmpi-4.0.2",
        "expected_cmds": [
            # "module load ninja",
            "module load cmake/3.17.1",
            # "module load devpack-arm",
            "module unload yaml-cpp",
            "module load python/3.6.8-arm",
            "module load arm/20.0",
            "module load openmpi4/4.0.2",
            "module load armpl/20.0.0",
            "module load git/2.19.2",
            "envvar_op set TEST_MATCHED_ENV machine-type-4-arm-20.0-openmpi-4.0.2",
        ]
    }
])
@pytest.mark.parametrize("prog_cmd", ["prog", "cmd"])
@patch("load_env.socket")
def test_correct_commands_are_saved(mock_socket, prog_cmd, inputs):
    ###########################################################################
    # **This will need to change later once we have a more sophisticated**
    # **system determination in place.**
    ###########################################################################
    mock_socket.gethostname.return_value = inputs["hostname"]

    if prog_cmd == "prog":
        le = LoadEnv(
            build_name=inputs["build_name"],
        )
    else:
        le = LoadEnv(argv=[
            inputs["build_name"],
        ])

    assert le.parsed_env_name == inputs["expected_env"]

    le.write_load_matching_env()
    load_matching_env_file = Path("/tmp/load_matching_env.sh")
    with open(load_matching_env_file, "r") as f:
        load_matching_env_contents = f.read()

    for expected_cmd in inputs["expected_cmds"]:
        assert expected_cmd in load_matching_env_contents
