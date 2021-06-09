from pathlib import Path
import pytest
import sys
import textwrap

root_dir = (Path.cwd()/".."
            if (Path.cwd()/"conftest.py").exists()
            else Path.cwd())
sys.path.append(str(root_dir))
from loadenv.EnvKeywordParser import EnvKeywordParser


#####################
#  Keyword Parsing  #
#####################
@pytest.mark.parametrize("keyword", [
    {
        "str": "machine-type-1_intel-19.0.4-mpich-7.7.15-hsw-openmp_static_dbg",
        "qualified_env_name": "machine-type-1_intel-19.0.4-mpich-7.7.15-hsw-openmp",
        "system_name": "machine-type-1",
    },
    {
        "str": "default-env-knl",
        "qualified_env_name": "machine-type-1_intel-19.0.4-mpich-7.7.15-knl-openmp",
        "system_name": "machine-type-1",
    },
    {
        "str": "intel_hsw",
        "qualified_env_name": "machine-type-1_intel-19.0.4-mpich-7.7.15-hsw-openmp",
        "system_name": "machine-type-1",
    },
    {
        "str": "machine-type-4_arm-20.1",
        "qualified_env_name": "machine-type-4_arm-20.1-openmpi-4.0.3-openmp",
        "system_name": "machine-type-4",
    },
    {
        "str": "arm-serial",
        "qualified_env_name": "machine-type-4_arm-20.0-openmpi-4.0.2-serial",
        "system_name": "machine-type-4",
    },
])
def test_env_keyword_parser_matches_correctly(keyword):
    ekp = EnvKeywordParser(keyword["str"], keyword["system_name"],
                           "test_supported_envs.ini")
    assert ekp.qualified_env_name == keyword["qualified_env_name"]


def test_nonexistent_env_name_or_alias_raises():
    ekp = EnvKeywordParser("bad-kw-str", "machine-type-1", "test_supported_envs.ini")

    with pytest.raises(SystemExit) as excinfo:
        ekp.qualified_env_name
    exc_msg = excinfo.value.args[0]

    assert ("ERROR:  Unable to find alias or environment name for system "
            "'machine-type-1' in") in exc_msg
    assert "build name 'bad-kw-str'" in exc_msg


@pytest.mark.parametrize("inputs", [
    {"system_name": "machine-type-1", "build_name": "intel-20",
     "unsupported_components": ["intel-20"]},
    {"system_name": "machine-type-1", "build_name": "intel-19-mpich-7.2",
     "unsupported_components": ["intel-19", "mpich-7.2"]},
    {"system_name": "machine-type-4", "build_name": "arm-20.2",
     "unsupported_components": ["arm-20.2"]},
    {"system_name": "machine-type-4", "build_name": "arm-20.1-openmpi-4.0.2",
     "unsupported_components": ["arm-20.1", "openmpi-4.0.2"]},
    {"system_name": "machine-type-1",
     "build_name": "intel-20.0.4-mpich-8.7.15-hsw-1.2.3-openmp-4.5.6",
     "unsupported_components": ["intel-20.0.4", "mpich-8.7.15", "hsw-1.2.3",
                                "openmp-4.5.6"]}
])
def test_unsupported_versions_are_rejected(inputs):
    ekp = EnvKeywordParser(inputs["build_name"], inputs["system_name"],
                           "test_supported_envs.ini")

    with pytest.raises(SystemExit) as excinfo:
        ekp.qualified_env_name
    exc_msg = excinfo.value.args[0]

    if inputs["system_name"] == "machine-type-1":
        assert "intel-19.0.4-mpich-7.7.15-hsw-openmp" in exc_msg
        assert "- intel-hsw-openmp\n" in exc_msg
        assert "- intel-hsw\n" in exc_msg
        assert "- intel-openmp\n" in exc_msg
        assert "- intel\n" in exc_msg
        assert "- default-env-hsw\n" in exc_msg
        assert "intel-19.0.4-mpich-7.7.15-knl-openmp" in exc_msg
        assert "- intel-knl-openmp\n" in exc_msg
        assert "- intel-knl\n" in exc_msg
        assert "- default-env-knl\n" in exc_msg
    else:
        assert "arm-20.0-openmpi-4.0.2-openmp" in exc_msg
        assert "arm-20.0-openmpi-4.0.2-serial" in exc_msg
        assert "arm-20.1-openmpi-4.0.3-openmp" in exc_msg
        assert "arm-20.1-openmpi-4.0.3-serial" in exc_msg


@pytest.mark.parametrize("inputs", [
    {"system_name": "machine-type-1", "build_name": "intel-hsw-serial",
     "unsupported_component": "serial"},
    {"system_name": "machine-type-1", "build_name": "intel-serial",
     "unsupported_component": "serial"},
    {"system_name": "test-system", "build_name": "env-name-openmp",
     "unsupported_component": "openmp"},
    {"system_name": "ride", "build_name": "cuda-serial",
     "unsupported_component": "static"},
    {"system_name": "ride", "build_name": "cuda-10-openmp",
     "unsupported_component": "openmp"},
])
def test_unsupported_node_types_are_rejected(inputs):
    ekp = EnvKeywordParser(inputs["build_name"], inputs["system_name"],
                           "test_supported_envs.ini")

    with pytest.raises(SystemExit) as excinfo:
        ekp.qualified_env_name
    exc_msg = excinfo.value.args[0]

    if inputs["system_name"] == "machine-type-1":
        assert "intel-19.0.4-mpich-7.7.15-hsw-openmp" in exc_msg
        assert "- intel-hsw-openmp\n" in exc_msg
        assert "- intel-hsw\n" in exc_msg
        assert "- intel-openmp\n" in exc_msg
        assert "- intel\n" in exc_msg
        assert "- default-env-hsw\n" in exc_msg
        assert "intel-19.0.4-mpich-7.7.15-knl-openmp" in exc_msg
        assert "- intel-knl-openmp\n" in exc_msg
        assert "- intel-knl\n" in exc_msg
        assert "- default-env-knl\n" in exc_msg
    elif inputs["system_name"] == "ride":
        assert "cuda-9.2-gnu-7.2.0-openmpi-2.1.2" in exc_msg
        assert "- cuda-9" in exc_msg
        assert "- cuda" in exc_msg
    elif inputs["system_name"] == "machine-type-4":
        assert "env-name-serial" in exc_msg
        assert "- env-name" in exc_msg


#############
#  Aliases  #
#############
@pytest.mark.parametrize("bad_alias", [
    {
        "alias": "intel",
        "err_msg": "ERROR:  Aliases for 'machine-type-1' contains duplicates:",
    },
    {
        "alias": "intel-18.0.5-mpich-7.7.15",
        "err_msg": ("ERROR:  Alias found for 'machine-type-1' that matches an "
                    "environment name:"),
    },
    {
        "alias": "intel-19.0.4-mpich-7.7.15",
        "err_msg": ("ERROR:  Alias found for 'machine-type-1' that matches an "
                    "environment name:"),
    },
])
def test_alias_values_are_unique(bad_alias):
    bad_supported_envs = (
        "[machine-type-1]\n"
        "intel-18.0.5-mpich-7.7.15: # Comment here\n"
        "    intel-18              # Comment here\n"
        "    intel                 # Comment here too\n"
        "    default-env           # It's the default\n"
        "intel-19.0.4-mpich-7.7.15:\n"
        "    intel-19\n"
        f"    {bad_alias['alias']}\n"
    )
    filename = "bad_supported_envs.ini"
    with open(filename, "w") as f:
        f.write(bad_supported_envs)

    with pytest.raises(SystemExit) as excinfo:
        EnvKeywordParser("default-env", "machine-type-1", filename)
    exc_msg = excinfo.value.args[0]

    assert bad_alias["err_msg"] in exc_msg
    assert f"- {bad_alias['alias']}\n" in exc_msg


def test_env_name_without_alias_okay():
    ekp = EnvKeywordParser("build-name", "test-system",
                           "test_supported_envs.ini")
    msg = ekp.get_msg_showing_supported_environments(
        "Ensuring environment names without aliases don't cause problems.",
        kind="TEST"
    )
    msg_expected = textwrap.dedent("""
            |   - Supported Environments for 'test-system':
            |     - another-env
            |       * Aliases:
            |         - with-an-alias
            |     - env-name-aliases-empty-string
            |     - env-name-aliases-none
            |     - env-name-serial
            |       * Aliases:
            |         - env-name
        """).strip()

    assert msg_expected in msg
    assert ("|   See test_supported_envs.ini for details."
            in msg)
