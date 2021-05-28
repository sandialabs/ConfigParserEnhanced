from pathlib import Path
import pytest
import sys

root_dir = (Path.cwd()/".."
            if (Path.cwd()/"conftest.py").exists()
            else Path.cwd())

sys.path.append(str(root_dir))
from gen_config import GenConfig



def test_list_config_flags():
    le = GenConfig([
        "--supported-config-flags", "test-supported-config-flags.ini",
        "--list-config-flags",
    ])
    with pytest.raises(SystemExit) as excinfo:
        le.list_config_flags()
    exc_msg = excinfo.value.args[0]
    for line in ["Supported Flags Are:",
                 "use-mpi",
                 "mpi (default)",
                 "no-mpi",
                 "node-type",
                 "serial (default)",
                 "openmp"]:
        assert line in exc_msg

@pytest.mark.parametrize("data", ["string", ("tu", "ple"), None])
def test_argv_non_list_raises(data):
    with pytest.raises(TypeError) as excinfo:
        GenConfig(data)
    exc_msg = excinfo.value.args[0]
    assert "must be instantiated with a list" in exc_msg



######################
#  Argument Parsing  #
######################
@pytest.mark.parametrize("data", [
    {
        "argv": [
            "--supported-config-flags",
            "non_default/supported-config-flags.ini",
            "build_name"
        ],
        "build_name_expected": "build_name",
        "supported_config_flags_expected":
        "non_default/supported-config-flags.ini",
        "config_specs_expected": "default",
        "supported_sys_expected": "default",
        "supported_envs_expected": "default",
        "environment_specs_expected": "default",
    },
    {
        "argv": [
            "--config-specs", "non_default/config-specs.ini",
            "build_name"
        ],
        "build_name_expected": "build_name",
        "supported_config_flags_expected": "default",
        "config_specs_expected": "non_default/config-specs.ini",
        "supported_sys_expected": "default",
        "supported_envs_expected": "default",
        "environment_specs_expected": "default",
    },
    {
        "argv": [
            "--supported-systems", "non_default/supported-systems.ini",
            "build_name"
        ],
        "build_name_expected": "build_name",
        "supported_config_flags_expected": "default",
        "config_specs_expected": "default",
        "supported_sys_expected": "non_default/supported-systems.ini",
        "supported_envs_expected": "default",
        "environment_specs_expected": "default",
    },
    {
        "argv": [
            "--supported-systems", "non_default/supported-systems.ini",
            "build_name"
        ],
        "build_name_expected": "build_name",
        "supported_config_flags_expected": "default",
        "config_specs_expected": "default",
        "supported_sys_expected": "non_default/supported-systems.ini",
        "supported_envs_expected": "default",
        "environment_specs_expected": "default",
    },
    {
        "argv": [
            "--supported-envs", "non_default/supported-envs.ini",
            "build_name"
        ],
        "build_name_expected": "build_name",
        "supported_config_flags_expected": "default",
        "config_specs_expected": "default",
        "supported_sys_expected": "default",
        "supported_envs_expected": "non_default/supported-envs.ini",
        "environment_specs_expected": "default",
    },
    {
        "argv": [
            "--environment-specs", "non_default/environment-specs.ini",
            "build_name"
        ],
        "build_name_expected": "build_name",
        "supported_config_flags_expected": "default",
        "config_specs_expected": "default",
        "supported_sys_expected": "default",
        "supported_envs_expected": "default",
        "environment_specs_expected": "non_default/environment-specs.ini",
    },
])
def test_argument_parser_functions_correctly(data):
    gc = GenConfig(data["argv"])
    assert gc.args.build_name == data["build_name_expected"]
    assert gc.args.supported_config_flags_file == Path(
        gc.gen_config_config_data["gen-config"]["supported-config-flags"]
        if data["supported_config_flags_expected"] == "default" else
        data["supported_config_flags_expected"]
    ).resolve()
    assert gc.args.config_specs_file == Path(
        gc.gen_config_config_data["gen-config"]["config-specs"]
        if data["config_specs_expected"] == "default" else
        data["config_specs_expected"]
    ).resolve()
    assert gc.args.supported_systems_file == Path(
        gc.gen_config_config_data["load-env"]["supported-systems"]
        if data["supported_sys_expected"] == "default" else
        data["supported_sys_expected"]
    ).resolve()
    assert gc.args.supported_envs_file == Path(
        gc.gen_config_config_data["load-env"]["supported-envs"]
        if data["supported_envs_expected"] == "default" else
        data["supported_envs_expected"]
    ).resolve()
    assert gc.args.environment_specs_file == Path(
        gc.gen_config_config_data["load-env"]["environment-specs"]
        if data["environment_specs_expected"] == "default" else
        data["environment_specs_expected"]
    ).resolve()


def test_gen_config_ini_file_used_if_nothing_else_explicitly_specified():
    gc = GenConfig(["build_name"])
    assert gc.args.supported_config_flags_file == Path(
        gc.gen_config_config_data["gen-config"]["supported-config-flags"]
    ).resolve()
    assert gc.args.config_specs_file == Path(
        gc.gen_config_config_data["gen-config"]["config-specs"]
    ).resolve()
    assert gc.args.supported_systems_file == Path(
        gc.gen_config_config_data["load-env"]["supported-systems"]
    ).resolve()
    assert gc.args.supported_systems_file == Path(
        gc.gen_config_config_data["load-env"]["supported-systems"]
    ).resolve()
    assert gc.args.supported_envs_file == Path(
        gc.gen_config_config_data["load-env"]["supported-envs"]
    ).resolve()
    assert gc.args.environment_specs_file == Path(
        gc.gen_config_config_data["load-env"]["environment-specs"]
    ).resolve()


@pytest.mark.parametrize("data", [
    {
        "gen_config_section_name": "invalid_section_name",
        "load_env_section_name": "load-env",
        "key1": "supported-config-flags",
        "value1": "test_supported_config_flags.ini",
        "key2": "supported-systems",
        "value2": "test_supported_systems.ini",
        "err_msg": "'bad_gen_config.ini' must contain a 'gen-config' section.",
    },
    {
        "gen_config_section_name": "gen-config",
        "load_env_section_name": "invalid_section_name",
        "key1": "supported-config-flags",
        "value1": "test_supported_config_flags.ini",
        "key2": "supported-systems",
        "value2": "test_supported_systems.ini",
        "err_msg": "'bad_gen_config.ini' must contain a 'load-env' section.",
    },
    {
        "gen_config_section_name": "gen-config",
        "load_env_section_name": "load-env",
        "key1": "bad-key",
        "value1": "test_supported_config_flags.ini",
        "key2": "supported-systems",
        "value2": "test_supported_systems.ini",
        "err_msg": ("'bad_gen_config.ini' must contain the following in the "
                    "'gen-config' section:"),
    },
    {
        "gen_config_section_name": "gen-config",
        "load_env_section_name": "load-env",
        "key1": "supported-config-flags",
        "value1": "test_supported_config_flags.ini",
        "key2": "bad-key",
        "value2": "test_supported_systems.ini",
        "err_msg": ("'bad_gen_config.ini' must contain the following in the "
                    "'load-env' section:"),
    },
    {
        "gen_config_section_name": "gen-config",
        "load_env_section_name": "load-env",
        "key1": "supported-config-flags",
        "value1": "",
        "key2": "supported-systems",
        "value2": "test_supported_systems.ini",
        "err_msg": ("The path specified for 'supported-config-flags' in "
                    "'bad_gen_config.ini' must be non-empty"),
    },
    {
        "gen_config_section_name": "gen-config",
        "load_env_section_name": "load-env",
        "key1": "supported-config-flags",
        "value1": "test_supported_config_flags.ini",
        "key2": "supported-systems",
        "value2": "",
        "err_msg": ("The path specified for 'supported-systems' in "
                    "'bad_gen_config.ini' must be non-empty"),
    },
])
def test_invalid_gen_config_file_raises(data):
    bad_gen_config_ini = (
        f"[{data['gen_config_section_name']}]\n"
        f"{data['key1']} : {data['value1']}\n"
        f"config-specs : test_config_specs.ini\n"
        "\n"
        f"[{data['load_env_section_name']}]\n"
        f"{data['key2']} : {data['value2']}\n"
        f"supported-envs : test_supported_envs.ini\n"
        f"environment-specs : test_environment_specs.ini\n"
    )
    filename = "bad_gen_config.ini"
    with open(filename, "w") as f:
        f.write(bad_gen_config_ini)

    with pytest.raises(ValueError, match=data["err_msg"]):
        GenConfig(["build_name"], gen_config_ini_file=filename)
