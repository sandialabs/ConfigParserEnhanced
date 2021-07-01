from configparserenhanced import ConfigParserEnhanced
from pathlib import Path
import pytest
import sys
from unittest import mock
from unittest.mock import patch


root_dir = Path.cwd() / ".." if (Path.cwd() / "conftest.py").exists() else Path.cwd()

sys.path.append(str(root_dir))
from loadenv import LoadEnv



@pytest.mark.parametrize("system_name", ["machine-type-1", "test-system"])
def test_list_envs(system_name):
    le = LoadEnv(
        [
            "--supported-systems",
            "test_supported_systems.ini",
            "--supported-envs",
            "test_supported_envs.ini",
            "--force",
            "--list-envs",
            system_name,
            ]
        )
    with pytest.raises(SystemExit) as excinfo:
        le.list_envs()
    exc_msg = excinfo.value.args[0]
    if system_name == "machine-type-1":
        for line in [
            "Supported Environments for 'machine-type-1':",
            "intel-19.0.4-mpich-7.7.15-hsw-openmp",
            "intel-hsw-openmp",
            "intel-19.0.4-mpich-7.7.15-knl-openmp",
            "default-env-knl",
            ]:
            assert line in exc_msg
    elif system_name == "test-system":
        for line in [
            "Supported Environments for 'test-system':",
            "env-name-aliases-empty-string",
            "env-name-aliases-none",
            "env-name-serial",
            "env-name",
            ]:
            assert line in exc_msg



@pytest.mark.parametrize("data", ["string", ("tu", "ple"), None])
def test_argv_non_list_raises(data):
    with pytest.raises(TypeError) as excinfo:
        LoadEnv(data)
    exc_msg = excinfo.value.args[0]
    assert "must be instantiated with a list" in exc_msg



######################
#  Argument Parsing  #
######################



@pytest.mark.parametrize(
    "data",
    [
        {
            "argv": [
                "--supported-systems",
                "non_default/supported-systems.ini",
                "keyword-str",
                ],
            "build_name_expected": "keyword-str",
            "supported_sys_expected": "non_default/supported-systems.ini",
            "supported_envs_expected": "default",
            "environment_specs_expected": "default",
            },
        {
            "argv": [
                "--supported-envs",
                "non_default/supported-envs.ini",
                "keyword-str",
                ],
            "build_name_expected": "keyword-str",
            "supported_sys_expected": "default",
            "supported_envs_expected": "non_default/supported-envs.ini",
            "environment_specs_expected": "default",
            },
        {
            "argv": [
                "--environment-specs",
                "non_default/environment-specs.ini",
                "keyword-str",
                ],
            "build_name_expected": "keyword-str",
            "supported_sys_expected": "default",
            "supported_envs_expected": "default",
            "environment_specs_expected": "non_default/environment-specs.ini",
            },
        {
            "argv": [
                # argv has two args in one string. LoadEnv should split this.
                "--environment-specs non_default/environment-specs.ini",
                "keyword-str",
                ],
            "build_name_expected": "keyword-str",
            "supported_sys_expected": "default",
            "supported_envs_expected": "default",
            "environment_specs_expected": "non_default/environment-specs.ini",
            },
        ],
    )
def test_argument_parser_functions_correctly(data):
    le = LoadEnv(data["argv"])
    assert le.args.build_name == data["build_name_expected"]
    assert (
        le.args.supported_systems_file == Path(
            le.load_env_config_data["load-env"]["supported-systems"]
            if data["supported_sys_expected"] == "default" else data["supported_sys_expected"]
            ).resolve()
        )
    assert (
        le.args.supported_envs_file == Path(
            le.load_env_config_data["load-env"]["supported-envs"]
            if data["supported_envs_expected"] == "default" else data["supported_envs_expected"]
            ).resolve()
        )
    assert (
        le.args.environment_specs_file == Path(
            le.load_env_config_data["load-env"]["environment-specs"] if
            data["environment_specs_expected"] == "default" else data["environment_specs_expected"]
            ).resolve()
        )



def test_load_env_ini_file_used_if_nothing_else_explicitly_specified():
    le = LoadEnv(["build_name"])
    assert (
        le.args.supported_systems_file == Path(
            le.load_env_config_data["load-env"]["supported-systems"]
            ).resolve()
        )
    assert (
        le.args.supported_envs_file == Path(le.load_env_config_data["load-env"]["supported-envs"]
                                           ).resolve()
        )
    assert (
        le.args.environment_specs_file == Path(
            le.load_env_config_data["load-env"]["environment-specs"]
            ).resolve()
        )



@pytest.mark.parametrize(
    "data",
    [
        {
            "section_name": "invalid_section_name",
            "key1": "supported-systems",
            "key2": "supported-envs",
            "key3": "environment-specs",
            "value1": "test_supported_systems.ini",
            "err_msg": "'bad_load_env.ini' must contain a 'load-env' section.",
            },
        {
            "section_name":
                "load-env",
            "key1":
                "bad-key",
            "key2":
                "supported-envs",
            "key3":
                "environment-specs",
            "value1":
                "test_supported_systems.ini",
            "err_msg":
                ("'bad_load_env.ini' must contain the following in the "
                 "'load-env' section:"),
            },
        {
            "section_name":
                "load-env",
            "key1":
                "supported-systems",
            "key2":
                "supported-envs",
            "key3":
                "environment-specs",
            "value1":
                "",
            "err_msg":
                (
                    "The path specified for 'supported-systems' in "
                    "'bad_load_env.ini' must be non-empty"
                    ),
            },
        ],
    )
def test_invalid_load_env_file_raises(data):
    bad_load_env_ini = (
        f"[{data['section_name']}]\n"
        f"{data['key1']} : {data['value1']}\n"
        f"{data['key2']} : test_supported_envs.ini\n"
        f"{data['key3']} : test_environment_specs.ini\n"
        )
    filename = "bad_load_env.ini"
    with open(filename, "w") as f:
        f.write(bad_load_env_ini)

    with pytest.raises(ValueError, match=data["err_msg"]):
        LoadEnv(["build_name"], load_env_ini_file=filename)
