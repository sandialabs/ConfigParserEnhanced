import getpass
from importlib import import_module
from pathlib import Path
import pytest
import sys
from unittest import mock
from unittest.mock import patch, Mock
import uuid


if (Path.cwd() / "conftest.py").exists():
    root_dir = (Path.cwd()/"../..").resolve()
elif (Path.cwd() / "unittests/conftest.py").exists():
    root_dir = (Path.cwd()/"..").resolve()
else:
    root_dir = Path.cwd()

sys.path.append(str(root_dir))
from configparserenhanced import ConfigParserEnhanced
from load_env import LoadEnv
import load_env


@pytest.mark.parametrize("system_name", ["machine-type-1", "test-system"])
def test_list_envs(system_name, capsys):
    with pytest.raises(SystemExit) as excinfo:
        load_env.main([
            "--supported-systems",
            "test_supported_systems.ini",
            "--supported-envs",
            "test_supported_envs.ini",
            "--force",
            "--list-envs",
            system_name,
        ])
    exc_msg, stderr = capsys.readouterr();
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


@patch("socket.gethostname")
@patch("load_env.SetEnvironment")
def test_load_matching_env_location_flag_creates_load_matching_env_location_file(mock_set_environment, mock_gethostname):
    # ci_mode file should exist in /tmp/{user}/.ci_mode
    mock_gethostname.return_value = "stria"
    # 'unsafe=True' allows methods to be called on the mock object that start
    # with 'assert'. For SetEnvironment, this includes
    # 'assert_file_all_sections_handled'.
    mock_se = Mock(unsafe=True)
    mock_se.apply.return_value = 0
    mock_set_environment.return_value = mock_se

    load_env.main(["arm", "--output", "test_out.sh", "--load-matching-env-location", ".load_matching_env_loc.test"])

    file = Path(f".load_matching_env_loc.test")
    assert file.exists()
    file.unlink()  # Cleanup
    assert not file.exists()


@pytest.mark.parametrize("data", ["string", ("tu", "ple"), None])
def test_argv_non_list_raises(data):
    with pytest.raises(TypeError) as excinfo:
        LoadEnv(data, load_env_ini_file="test_load_env.ini")
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
        ],
    )
def test_argument_parser_functions_correctly(data):
    le = LoadEnv(data["argv"], load_env_ini_file="test_load_env.ini")
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


#################
#  load_env.ini #
#################
def test_load_env_ini_file_used_if_nothing_else_explicitly_specified():
    le = LoadEnv(["build_name"], load_env_ini_file="test_load_env.ini")
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


@pytest.mark.parametrize("already_resolved", [True, False])
def test_relative_path_resolves_to_absolute_path(already_resolved):
    supported_systems = Path('test_supported_systems.ini')
    supported_envs = Path('test_supported_envs.ini')
    environment_specs = Path('test_environment_specs.ini')

    if already_resolved:
        supported_systems = supported_systems.resolve()
        supported_envs = supported_envs.resolve()
        environment_specs = environment_specs.resolve()

    load_env_ini = (
        "[load-env]\n"
        f"supported-systems : {supported_systems}\n"
        f"supported-envs : {supported_envs}\n"
        f"environment-specs : {environment_specs}\n"
    )
    filename = "test_generated_load_env.ini"
    with open(filename, "w") as f:
        f.write(load_env_ini)

    le = LoadEnv(["build_name"], load_env_ini_file=filename)

    if already_resolved:
        assert le.args.supported_systems_file == supported_systems
        assert le.args.supported_envs_file == supported_envs
        assert le.args.environment_specs_file == environment_specs
    else:
        assert le.args.supported_systems_file != supported_systems
        assert le.args.supported_envs_file != supported_envs
        assert le.args.environment_specs_file != environment_specs

    assert "/" in str(le.args.supported_systems_file)
    assert "/" in str(le.args.supported_envs_file)
    assert "/" in str(le.args.environment_specs_file)
