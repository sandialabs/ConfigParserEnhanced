from pathlib import Path
import pytest
import sys

root_dir = (Path.cwd()/".."
            if (Path.cwd()/"conftest.py").exists()
            else Path.cwd())
sys.path.append(str(root_dir))
from src.env_keyword_parser import EnvKeywordParser


def test_supported_envs_ini_is_read_correctly():
    ekp = EnvKeywordParser("default-env", "machine-type-1", "test_supported_envs.ini")
    se = ekp.supported_envs
    assert se is not None

    # Structure Checks
    """
    e.g.
        [machine-type-1]
        intel-18.0.5-mpich-7.7.6:   << se["machine-type-1"].keys()
            intel-18             <-|
            intel                  |-< se["machine-type-1"].values()
            default-env          <-|
        intel-19.0.4-mpich-7.7.6:   << se["machine-type-1"].keys()
            intel-19                << se["machine-type-1"].values()
    """
    assert [_ for _ in se.keys()] != ["DEFAULT"]
    assert [_ for _ in se["machine-type-1"].keys()] != []
    assert "default-env" in "\n".join([_ for _ in se["machine-type-1"].values()])


def test_invalid_supported_envs_filename_raises():
    with pytest.raises(IOError) as excinfo:
        ekp = EnvKeywordParser("", "machine-type-1", "invalid_filename_here.ini")
        ekp.supported_envs
    exception_message = excinfo.value.args[0]
    assert ("ERROR: Unable to load configuration .ini file" in
            exception_message)


#####################
#  Keyword Parsing  #
#####################
@pytest.mark.parametrize("keyword", [
    {
        "str": "machine-type-1-hsw_intel-19.0.4_mpich-7.7.6_openmp_static_dbg",
        "qualified_env_name": "machine-type-1-intel-19.0.4-mpich-7.7.6",
        "system_name": "machine-type-1",
    },
    {
        "str": "default-env",
        "qualified_env_name": "machine-type-1-intel-18.0.5-mpich-7.7.6",
        "system_name": "machine-type-1",
    },
    {
        "str": "intel-18",
        "qualified_env_name": "machine-type-1-intel-18.0.5-mpich-7.7.6",
        "system_name": "machine-type-1",
    },
    {
        "str": "machine-type-4-arm-20.1",
        "qualified_env_name": "machine-type-4-arm-20.1-openmpi-4.0.3",
        "system_name": "machine-type-4",
    },
])
def test_keyword_parser_matches_correctly(keyword):
    ekp = EnvKeywordParser(keyword["str"], keyword["system_name"],
                           "test_supported_envs.ini")
    assert ekp.qualified_env_name == keyword["qualified_env_name"]


@pytest.mark.parametrize("kw_str", ["intel-19.0.4-mpich-7.7.6",
                                    "intel_19.0.4_mpich_7.7.6"])
def test_underscores_hyphens_dont_matter_for_kw_str(kw_str):
    ekp = EnvKeywordParser(kw_str, "machine-type-1", "test_supported_envs.ini")
    assert ekp.qualified_env_name == "machine-type-1-intel-19.0.4-mpich-7.7.6"


def test_nonexistent_env_name_or_alias_raises():
    ekp = EnvKeywordParser("bad_kw_str", "machine-type-1", "test_supported_envs.ini")

    with pytest.raises(SystemExit) as excinfo:
        ekp.qualified_env_name
    exc_msg = excinfo.value.args[0]

    assert ("ERROR:  Unable to find alias or environment name for system "
            "'machine-type-1' in") in exc_msg
    assert "keyword string 'bad-kw-str'" in exc_msg


@pytest.mark.parametrize("inputs", [
    {"system_name": "machine-type-1", "build_name": "intel-20",
     "unsupported_component": "intel-20"},
    {"system_name": "machine-type-1", "build_name": "intel-19-mpich-7.2",
     "unsupported_component": "mpich-7.2"},
    {"system_name": "machine-type-4", "build_name": "arm-20.2",
     "unsupported_component": "arm-20.2"},
    {"system_name": "machine-type-4", "build_name": "arm-20.1-openmpi-4.0.2",
     "unsupported_component": "arm-20.1-openmpi-4.0.2"},
])
def test_unsupported_versions_are_rejected(inputs):
    ekp = EnvKeywordParser(inputs["build_name"], inputs["system_name"],
                           "test_supported_envs.ini")

    with pytest.raises(SystemExit) as excinfo:
        ekp.qualified_env_name
    exc_msg = excinfo.value.args[0]

    assert (f"ERROR:  '{inputs['unsupported_component']}' is not a supported "
            "version") in exc_msg

    if inputs["system_name"] == "machine-type-1":
        assert "intel-18.0.5-mpich-7.7.6" in exc_msg
        assert "- intel-18\n" in exc_msg
        assert "- intel\n" in exc_msg
        assert "- default-env\n" in exc_msg
        assert "intel-19.0.4-mpich-7.7.6" in exc_msg
        assert "- intel-19\n" in exc_msg
    else:
        assert "arm-20.0-openmpi-4.0.2" in exc_msg
        assert "arm-20.1-openmpi-4.0.3" in exc_msg


#############
#  Aliases  #
#############
def test_underscores_hyphens_dont_matter_for_aliases():
    # "intel-18" and "intel_default" are aliases for "machine-type-1"
    ekp = EnvKeywordParser("intel-18", "machine-type-1", "test_supported_envs.ini")
    aliases = ekp.get_aliases()
    assert "intel-18" in aliases
    assert "intel-default" in aliases
    assert "intel_default" not in aliases  # Even though this is how it's
    #                                        defined in the .ini


@pytest.mark.parametrize("bad_alias", [
    {
        "alias": "intel",
        "err_msg": "ERROR:  Aliases for 'machine-type-1' contains duplicates:",
    },
    {
        "alias": "intel-18.0.5-mpich-7.7.6",
        "err_msg": ("ERROR:  Alias found for 'machine-type-1' that matches an environment"
                    " name:"),
    },
    {
        "alias": "intel-19.0.4-mpich-7.7.6",
        "err_msg": ("ERROR:  Alias found for 'machine-type-1' that matches an environment"
                    " name:"),
    },
])
def test_alias_values_are_unique(bad_alias):
    bad_supported_envs = (
        "[machine-type-1]\n"
        "intel-18.0.5-mpich-7.7.6: # Comment here\n"
        "    intel-18              # Comment here\n"
        "    intel                 # Comment here too\n"
        "    default-env           # It's the default\n"
        "intel-19.0.4-mpich-7.7.6:\n"
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


@pytest.mark.parametrize("multiple_aliases", [True, False])
def test_alias_values_do_not_contain_whitespace(multiple_aliases):
    bad_supported_envs = (
        "[machine-type-1]\n"
        "intel-18.0.5-mpich-7.7.6: # Comment here\n"
        "    intel 18              # Space in this alias\n" +
        ("    intel default\n" if multiple_aliases is True else "") +
        "    intel                 # Comment here too\n"
    )
    filename = "bad_supported_envs.ini"
    with open(filename, "w") as f:
        f.write(bad_supported_envs)

    with pytest.raises(SystemExit) as excinfo:
        EnvKeywordParser("intel-18", "machine-type-1", filename)
    exc_msg = excinfo.value.args[0]

    es = "es" if multiple_aliases is True else ""
    s = "" if multiple_aliases is True else "s"
    assert f"The following alias{es} contain{s} whitespace:" in exc_msg
    assert "- intel 18\n" in exc_msg
    if multiple_aliases is True:
        assert "- intel default\n" in exc_msg


@pytest.mark.parametrize("general_section_order", ["first", "last"])
def test_general_alias_matches_correct_env_name(general_section_order):
    general_section = (
        "intel-18.0.5-mpich-7.7.6: # Comment here\n"
        "    intel-18              # Comment here\n"
        "    intel                 # This is the general alias\n"
        "    default-env           # It's the default"
    )
    other_section = (
        "intel-19.0.4-mpich-7.7.6:\n"
        "    intel-19"
    )
    supported_envs = "\n".join([
        "[machine-type-1]",
        general_section if general_section_order == "first" else other_section,
        other_section if general_section_order == "first" else general_section,
    ])

    filename = "test_general_alias_supported_envs.ini"
    with open(filename, "w") as f:
        f.write(supported_envs)

    ekp = EnvKeywordParser("intel", "machine-type-1", filename)
    assert ekp.get_env_name_for_alias("intel") == "intel-18.0.5-mpich-7.7.6"


def test_matched_alias_not_in_supported_envs_raises():
    ekp = EnvKeywordParser("intel", "machine-type-1", "test_supported_envs.ini")

    with pytest.raises(SystemExit) as excinfo:
        ekp.get_env_name_for_alias("bad_alias")
    exc_msg = excinfo.value.args[0]

    assert ("ERROR:  Unable to find alias 'bad_alias' in aliases for "
            "'machine-type-1'") in exc_msg
