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

load_env_ini_data = ConfigParserEnhanced(
    root_dir/"tests/supporting_files/test_load_env.ini"
).configparserenhanceddata["load-env"]



@pytest.mark.parametrize("data", ["string", ("tu", "ple"), None])
def test_argv_non_list_raises(data):
    with pytest.raises(TypeError) as excinfo:
        le = LoadEnv(data)
    exc_msg = excinfo.value.args[0]
    assert "must be instantiated with a list" in exc_msg



######################
#  Argument Parsing  #
######################
@pytest.mark.parametrize("data", [
    {
        "argv": ["--supported-systems",
                 "non_default/supported-systems.ini", "keyword-str"],
        "build_name_expected": "keyword-str",
        "supported_sys_expected": "non_default/supported-systems.ini",
        "supported_envs_expected": load_env_ini_data["supported-envs"],
        "environment_specs_expected": load_env_ini_data["environment-specs"],
    },
    {
        "argv": [
            "--supported-systems",
            "non_default/supported-systems.ini",
            "--supported-envs",
            "non_default/supported-envs.ini",
            "--environment-specs",
            "non_default/environment_specs.ini",
            "keyword-str"
        ],
        "build_name_expected": "keyword-str",
        "supported_sys_expected": "non_default/supported-systems.ini",
        "supported_envs_expected": "non_default/supported-envs.ini",
        "environment_specs_expected": "non_default/environment_specs.ini",
    },
])
def test_argument_parser_functions_correctly(data):
    le = LoadEnv(data["argv"])
    assert le.build_name == data["build_name_expected"]
    assert le.supported_systems_file == Path(data["supported_sys_expected"])
    assert le.supported_envs_file == Path(data["supported_envs_expected"])
    assert le.environment_specs_file == Path(
        data["environment_specs_expected"]
    )


def test_args_overwrite_programmatic_file_assignments():
    le = LoadEnv(
        [
            "--supported-systems",
            "arg/supported-systems.ini",
            "--supported-envs",
            "arg/supported-envs.ini",
            "--environment-specs",
            "arg/environment_specs.ini",
            "--force",
            "keyword-str-arg"
        ],
        supported_systems_file="prog/supported-systems.ini",
        supported_envs_file="prog/supported-envs.ini",
        environment_specs_file="prog/environment_specs.ini",
        force=False,
    )
    assert le.build_name == "keyword-str-arg"
    assert le.supported_systems_file == Path("arg/supported-systems.ini")
    assert le.supported_envs_file == Path("arg/supported-envs.ini")
    assert le.environment_specs_file == Path("arg/environment_specs.ini")
    assert le.force is True


@pytest.mark.parametrize("blank_value", [
    "supported_systems_file", "supported_envs_file", "environment_specs_file"
])
@patch("load_env.ConfigParserEnhanced")
def test_empty_string_values_raise_ValueError(mock_cpe, blank_value):
    # load-env.ini also has blank values
    mock_cpe_obj = mock.Mock()
    mock_cpe.return_value = mock_cpe_obj
    mock_cpe_obj.configparserenhanceddata = {
        "load-env": {
            "supported-systems": "",
            "supported-envs": "",
            "environment-specs": "",
        }
    }

    data = {
        "build_name": "keyword-str-prog",
        "supported_systems_file": "prog/supported-systems.ini",
        "supported_envs_file": "prog/supported-envs.ini",
        "environment_specs_file": "prog/environment_specs.ini",
    }
    data[blank_value] = ""

    argv = []
    if blank_value == "supported_systems_file":
        argv += ["--supported-systems", data["supported_systems_file"]]
    if blank_value == "supported_envs_file":
        argv += ["--supported-envs", data["supported_envs_file"]]
    if blank_value == "environment_specs_file":
        argv += ["--environment-specs", data["environment_specs_file"]]
    argv += [data["build_name"]]
    le = LoadEnv(argv)

    with pytest.raises(ValueError) as excinfo:
        # Error is only raised when grabbing the property because they are
        # lazily evaluated (only when needed).
        le.build_name
        le.supported_systems_file
        le.supported_envs_file
        le.environment_specs_file
    exc_msg = excinfo.value.args[0]

    if blank_value != "build_name":
        assert "Path for" in exc_msg
        assert 'cannot be "".' in exc_msg
    else:
        assert 'Keyword string cannot be "".' in exc_msg


def test_load_env_ini_file_used_if_nothing_else_explicitly_specified():
    le = LoadEnv(["build_name"])
    assert le.supported_systems_file == Path(
        load_env_ini_data["supported-systems"]
    )
    assert le.supported_envs_file == Path(load_env_ini_data["supported-envs"])
    assert le.environment_specs_file == Path(
        load_env_ini_data["environment-specs"]
    )


###############################
#  System Name Determination  #
###############################
@pytest.mark.parametrize("data", [
    {"hostname": "mutrino", "sys_name": "machine-type-1"},
    {"hostname": "vortex", "sys_name": "machine-type-2"},
    {"hostname": "eclipse", "sys_name": "machine-type-3"},
    {"hostname": "cee-build007", "sys_name": "rhel7"},
    {"hostname": "cee-compute004", "sys_name": "rhel7"},
])
@patch("load_env.socket")
def test_system_name_determination_correct_for_hostname(mock_socket, data):
    mock_socket.gethostname.return_value = data["hostname"]
    le = LoadEnv(["build_name"])
    assert le.system_name == data["sys_name"]


@patch("load_env.socket")
def test_sys_name_in_build_name_not_matching_hostname_raises(mock_socket):
    mock_socket.gethostname.return_value = "stria"
    le = LoadEnv(["machine-type-1-build-name"])
    with pytest.raises(SystemExit) as excinfo:
        le.system_name
    exc_msg = excinfo.value.args[0]
    assert "Hostname 'stria' matched to system 'machine-type-4'" in exc_msg
    assert "but you specified 'machine-type-1' in the build name" in exc_msg
    assert "add the --force flag" in exc_msg


@patch("load_env.socket")
def tests_sys_name_in_build_name_overrides_hostname_match_when_forced(
    mock_socket
):
    mock_socket.gethostname.return_value = "stria"
    le = LoadEnv(["machine-type-1-build-name", "--force"])
    assert le.system_name == "machine-type-1"


@pytest.mark.parametrize("hostname", ["stria", "unsupported_hostname"])
@patch("load_env.socket")
def test_multiple_sys_names_in_build_name_raises_regardless_of_hostname_match(
    mock_socket, hostname
):
    mock_socket.gethostname.return_value = hostname
    le = LoadEnv(["machine-type-1-rhel7-build-name"])
    with pytest.raises(SystemExit) as excinfo:
        le.system_name
    exc_msg = excinfo.value.args[0]
    assert ("Cannot specify more than one system name in the build name"
            in exc_msg)
    assert "- machine-type-1" in exc_msg
    assert "- rhel7" in exc_msg


@pytest.mark.parametrize("data", [
    {"build_name": "no-system-here", "sys_name": None, "raises": True},
    {"build_name": "machine-type-1-build-name", "sys_name": "machine-type-1", "raises": False},
])
@patch("load_env.socket")
def test_unsupported_hostname_handled_correctly(mock_socket, data):
    mock_socket.gethostname.return_value = "unsupported_hostname"
    le = LoadEnv([data["build_name"]])
    if data["raises"]:
        with pytest.raises(SystemExit) as excinfo:
            le.system_name
        exc_msg = excinfo.value.args[0]

        assert ("Unable to find valid system name in the build name or for "
                "the hostname 'unsupported_hostname'" in exc_msg)
        assert str(le.supported_systems_file) in exc_msg
    else:
        assert le.system_name == data["sys_name"]


######################################################################
#  EnvKeywordParser (ekp) Basic Interaction (not integration tests)  #
######################################################################
@patch("load_env.EnvKeywordParser")
@patch("load_env.socket")
def test_correct_arguments_are_passed_to_ekp_object(mock_socket, mock_ekp):
    mock_socket.gethostname.return_value = "mutrino"
    le = LoadEnv(argv=["build_name"])
    le.parsed_env_name

    mock_ekp.assert_called_once_with(le.build_name, le.system_name,
                                     le.supported_envs_file)


@patch("load_env.EnvKeywordParser")
@patch("load_env.socket")
def test_ekp_qualified_env_name_gets_set_as_parsed_env_name(mock_socket,
                                                            mock_ekp):
    mock_socket.gethostname.return_value = "mutrino"
    qualified_env_name = "machine-type-1-intel-18.0.5-mpich-7.7.6"
    mock_ekp_obj = mock.Mock()
    mock_ekp_obj.qualified_env_name = qualified_env_name
    mock_ekp.return_value = mock_ekp_obj

    le = LoadEnv(argv=["intel"])
    assert le.parsed_env_name == qualified_env_name


########################################################
#  SetEnvironment Interaction (not integration tests)  #
########################################################
@patch("load_env.EnvKeywordParser")
@patch("load_env.SetEnvironment")
@patch("load_env.socket")
def test_correct_arguments_are_passed_to_set_environment_object(
    mock_socket, mock_se, mock_ekp
):
    mock_socket.gethostname.return_value = "mutrino"
    qualified_env_name = "machine-type-1-intel-18.0.5-mpich-7.7.6"
    mock_ekp_obj = mock.Mock()
    mock_ekp_obj.qualified_env_name = qualified_env_name
    mock_ekp.return_value = mock_ekp_obj

    mock_se_obj = mock.Mock()
    mock_se.return_value = mock_se_obj

    le = LoadEnv(argv=["build_name"])
    le.write_load_matching_env()

    mock_se.assert_called_once_with(filename=le.environment_specs_file)
    mock_se_obj.write_actions_to_file.assert_called_once_with(
        Path("/tmp/load_matching_env.sh").resolve(), qualified_env_name,
        include_header=True, interpreter="bash"
    )


@pytest.mark.parametrize("output",
                         [None, "test_dir/load_matching_env.sh"])
@patch("load_env.EnvKeywordParser")
@patch("load_env.SetEnvironment")
@patch("load_env.socket")
def test_load_matching_env_is_set_correctly_and_directories_are_created(
    mock_socket, mock_se, mock_ekp, output
):
    if output is not None:
        assert Path(output).exists() is False

    mock_socket.gethostname.return_value = "mutrino"
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
