from configparserenhanced import ConfigParserEnhanced
from pathlib import Path
import pytest
import sys
from unittest import mock
from unittest.mock import patch

root_dir = (Path.cwd()/".."
            if (Path.cwd()/"conftest.py").exists()
            else Path.cwd())

sys.path.append(str(root_dir))
from load_env import LoadEnv



@pytest.mark.parametrize("system_name", ["machine-type-1", "test-system"])
def test_list_envs(system_name):
    le = LoadEnv([
        "--supported-systems", "test_supported_systems.ini",
        "--supported-envs", "test_supported_envs.ini",
        "--force",
        "--list-envs",
        system_name
    ])
    with pytest.raises(SystemExit) as excinfo:
        le.list_envs()
    exc_msg = excinfo.value.args[0]
    if system_name == "machine-type-1":
        for line in ["Supported Environments for 'machine-type-1':",
                     "intel-19.0.4-mpich-7.7.15-hsw-openmp",
                     "intel-hsw-openmp",
                     "intel-19.0.4-mpich-7.7.15-knl-openmp",
                     "default-env-knl"]:
            assert line in exc_msg
    elif system_name == "test-system":
        for line in ["Supported Environments for 'test-system':",
                     "env-name-aliases-empty-string",
                     "env-name-aliases-none",
                     "env-name-serial",
                     "env-name"]:
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
@pytest.mark.parametrize("data", [
    {
        "argv": [
            "--supported-systems", "non_default/supported-systems.ini",
            "keyword-str"
        ],
        "build_name_expected": "keyword-str",
        "supported_sys_expected": "non_default/supported-systems.ini",
        "supported_envs_expected": "default",
        "environment_specs_expected": "default",
    },
    {
        "argv": [
            "--supported-envs", "non_default/supported-envs.ini",
            "keyword-str"
        ],
        "build_name_expected": "keyword-str",
        "supported_sys_expected": "default",
        "supported_envs_expected": "non_default/supported-envs.ini",
        "environment_specs_expected": "default",
    },
    {
        "argv": [
            "--environment-specs", "non_default/environment-specs.ini",
            "keyword-str"
        ],
        "build_name_expected": "keyword-str",
        "supported_sys_expected": "default",
        "supported_envs_expected": "default",
        "environment_specs_expected": "non_default/environment-specs.ini",
    },
])
def test_argument_parser_functions_correctly(data):
    le = LoadEnv(data["argv"])
    assert le.args.build_name == data["build_name_expected"]
    assert le.args.supported_systems_file == Path(
        le.load_env_config_data["load-env"]["supported-systems"]
        if data["supported_sys_expected"] == "default" else
        data["supported_sys_expected"]
    ).resolve()
    assert le.args.supported_envs_file == Path(
        le.load_env_config_data["load-env"]["supported-envs"]
        if data["supported_envs_expected"] == "default" else
        data["supported_envs_expected"]
    ).resolve()
    assert le.args.environment_specs_file == Path(
        le.load_env_config_data["load-env"]["environment-specs"]
        if data["environment_specs_expected"] == "default" else
        data["environment_specs_expected"]
    ).resolve()


def test_load_env_ini_file_used_if_nothing_else_explicitly_specified():
    le = LoadEnv(["build_name"])
    assert le.args.supported_systems_file == Path(
        le.load_env_config_data["load-env"]["supported-systems"]
    ).resolve()
    assert le.args.supported_envs_file == Path(
        le.load_env_config_data["load-env"]["supported-envs"]
    ).resolve()
    assert le.args.environment_specs_file == Path(
        le.load_env_config_data["load-env"]["environment-specs"]
    ).resolve()


@pytest.mark.parametrize("data", [
    {
        "section_name": "invalid_section_name",
        "key1": "supported-systems",
        "key2": "supported-envs",
        "key3": "environment-specs",
        "value1": "test_supported_systems.ini",
        "err_msg": "'bad_load_env.ini' must contain a 'load-env' section.",
    },
    {
        "section_name": "load-env",
        "key1": "bad-key",
        "key2": "supported-envs",
        "key3": "environment-specs",
        "value1": "test_supported_systems.ini",
        "err_msg": ("'bad_load_env.ini' must contain the following in the "
                    "'load-env' section:"),
    },
    {
        "section_name": "load-env",
        "key1": "supported-systems",
        "key2": "supported-envs",
        "key3": "environment-specs",
        "value1": "",
        "err_msg": ("The path specified for 'supported-systems' in "
                    "'bad_load_env.ini' must be non-empty"),
    },
])
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


######################################################################
#  EnvKeywordParser (ekp) Basic Interaction (not integration tests)  #
######################################################################
@patch("load_env.EnvKeywordParser")
@patch("load_env.DetermineSystem")
def test_correct_arguments_are_passed_to_ekp_object(mock_ds, mock_ekp):
    mock_ds_obj = mock.Mock()
    mock_ds_obj.system_name = "machine-type-1"
    mock_ds.return_value = mock_ds_obj

    le = LoadEnv(argv=["build_name"])
    le.parsed_env_name

    mock_ekp.assert_called_once_with(le.args.build_name, le.system_name,
                                     le.args.supported_envs_file)


@patch("load_env.EnvKeywordParser")
@patch("load_env.DetermineSystem")
def test_ekp_qualified_env_name_gets_set_as_parsed_env_name(
    mock_ds, mock_ekp
):
    mock_ds_obj = mock.Mock()
    mock_ds_obj.system_name = "machine-type-1"
    mock_ds.return_value = mock_ds_obj

    qualified_env_name = "machine-type-1-intel-18.0.5-mpich-7.7.6"
    mock_ekp_obj = mock.Mock()
    mock_ekp_obj.qualified_env_name = qualified_env_name
    mock_ekp.return_value = mock_ekp_obj

    le = LoadEnv(argv=["intel"])
    assert le.parsed_env_name == qualified_env_name


###############################################################
#  DetermineSystem Basic Interaction (not integration tests)  #
###############################################################
@patch("load_env.DetermineSystem")
def test_correct_arguments_are_passed_to_determine_system_object(mock_ds):
    le = LoadEnv(argv=["build_name"])
    le.system_name

    mock_ds.assert_called_once_with(le.args.build_name,
                                    le.args.supported_systems_file,
                                    force_build_name=le.args.force)


@patch("load_env.DetermineSystem")
def test_determined_system_n_gets_set_as_system_name(mock_ds):
    mock_ds_obj = mock.Mock()
    mock_ds_obj.system_name = "machine-type-1"
    mock_ds.return_value = mock_ds_obj

    le = LoadEnv(argv=["intel"])
    assert le.system_name == "machine-type-1"


########################################################
#  SetEnvironment Interaction (not integration tests)  #
########################################################
@patch("load_env.EnvKeywordParser")
@patch("load_env.SetEnvironment")
@patch("load_env.DetermineSystem")
def test_correct_arguments_are_passed_to_set_environment_object(
    mock_ds, mock_se, mock_ekp
):
    mock_ds_obj = mock.Mock()
    mock_ds_obj.system_name = "machine-type-1"
    mock_ds.return_value = mock_ds_obj
    qualified_env_name = "machine-type-1-intel-18.0.5-mpich-7.7.6"
    mock_ekp_obj = mock.Mock()
    mock_ekp_obj.qualified_env_name = qualified_env_name
    mock_ekp.return_value = mock_ekp_obj

    mock_se_obj = mock.Mock()
    mock_se.return_value = mock_se_obj

    le = LoadEnv(argv=["build_name"])
    le.write_load_matching_env()

    mock_se.assert_called_once_with(filename=le.args.environment_specs_file)
    mock_se_obj.write_actions_to_file.assert_called_once_with(
        Path("/tmp/load_matching_env.sh").resolve(), qualified_env_name,
        include_header=True, interpreter="bash"
    )


@pytest.mark.parametrize("output",
                         [None, "test_dir/load_matching_env.sh"])
@patch("load_env.EnvKeywordParser")
@patch("load_env.SetEnvironment")
@patch("load_env.DetermineSystem")
def test_load_matching_env_is_set_correctly_and_directories_are_created(
    mock_ds, mock_se, mock_ekp, output
):
    if output is not None:
        assert Path(output).exists() is False

    mock_ds_obj = mock.Mock()
    mock_ds_obj.system_name = "machine-type-1"
    mock_ds.return_value = mock_ds_obj

    mock_se_obj = mock.Mock()
    mock_se.return_value = mock_se_obj

    argv = (["build_name"]
            if output is None
            else ["build_name", "--output", output])
    le = LoadEnv(argv=argv)
    load_matching_env = le.write_load_matching_env()

    expected_file = (Path("/tmp/load_matching_env.sh")
                     if output is None else Path(output)).resolve()
    assert expected_file.parent.exists()
    assert load_matching_env == expected_file
