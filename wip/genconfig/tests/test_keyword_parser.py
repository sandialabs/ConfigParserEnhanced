from pathlib import Path
import pytest
import sys

root_dir = (Path.cwd()/".."
            if (Path.cwd()/"conftest.py").exists()
            else Path.cwd())
sys.path.append(str(root_dir))
from src.keyword_parser import KeywordParser


def test_config_ini_is_read_correctly():
    kp = KeywordParser("test_supported_envs.ini")
    assert kp.config is not None

    # Structure Checks
    """
    e.g.
        [machine-type-5]
        intel-18.0.5-mpich-7.7.6:   << kp.config["machine-type-5"].keys()
            intel-18             <-|
            intel                  |-< kp.config["machine-type-5"].values()
            default-env          <-|
        intel-19.0.4-mpich-7.7.6:   << kp.config["machine-type-5"].keys()
            intel-19                << kp.config["machine-type-5"].values()
    """
    assert [_ for _ in kp.config.keys()] != ["DEFAULT"]
    assert [_ for _ in kp.config["machine-type-5"].keys()] != []
    assert "default-env-hsw" in kp.get_values_for_section_key(
        "machine-type-5", "intel-19.0.4-mpich-7.7.15-hsw-openmp"
    )


def test_invalid_supported_envs_filename_raises():
    with pytest.raises(IOError) as excinfo:
        kp = KeywordParser("invalid_filename_here.ini")
        kp.config["machine-type-5"]
    exception_message = excinfo.value.args[0]
    assert ("ERROR: Unable to load configuration .ini file" in
            exception_message)


@pytest.mark.parametrize("multiple_values", [True, False])
def test_values_do_not_contain_machine-name-4space(multiple_values):
    bad_config = (
        "[machine-type-5]\n"
        "intel-18.0.5-mpich-7.7.15: # Comment here\n"
        "    intel 18              # Space in this value\n" +
        ("    intel default\n" if multiple_values is True else "") +
        "    intel                 # Comment here too\n"
    )
    filename = "bad_config.ini"
    with open(filename, "w") as f:
        f.write(bad_config)

    with pytest.raises(SystemExit) as excinfo:
        kp = KeywordParser(filename)
        for key in kp.config["machine-type-5"].keys():
            kp.get_values_for_section_key("machine-type-5", key)
    exc_msg = excinfo.value.args[0]

    es = "es" if multiple_values is True else "e"
    s = "" if multiple_values is True else "s"
    assert f"The following valu{es} contain{s} machine-name-4space:" in exc_msg
    assert "- intel 18\n" in exc_msg
    if multiple_values is True:
        assert "- intel default\n" in exc_msg


def test_values_are_unique():
    bad_config = (
        "[machine-type-5]\n"
        "intel-18.0.5-mpich-7.7.15: # Comment here\n"
        "    intel-18               # Space in this value\n"
        "    intel-default\n"
        "    intel-18               # Oops, a duplicate\n"
    )
    filename = "bad_config.ini"
    with open(filename, "w") as f:
        f.write(bad_config)

    with pytest.raises(SystemExit) as excinfo:
        kp = KeywordParser(filename)
        for key in kp.config["machine-type-5"].keys():
            kp.get_values_for_section_key("machine-type-5", key)
    exc_msg = excinfo.value.args[0]

    assert ("Values for 'bad_config.ini'['machine-type-5']['intel-18.0.5-mpich-7.7.15'] "
            "contains duplicates: ") in exc_msg
    assert "- intel-18" in exc_msg


@pytest.mark.parametrize("general_section_order", ["first", "last"])
def test_general_value_matches_correct_key(general_section_order):
    general_section = (
        "intel-18.0.5-mpich-7.7.15: # Comment here\n"
        "    intel-18              # Comment here\n"
        "    intel                 # This is the general value\n"
        "    default-env           # It's the default"
    )
    other_section = (
        "intel-19.0.4-mpich-7.7.15:\n"
        "    intel-19"
    )
    config = "\n".join([
        "[machine-type-5]",
        general_section if general_section_order == "first" else other_section,
        other_section if general_section_order == "first" else general_section,
    ])

    filename = "test_general_value_config.ini"
    with open(filename, "w") as f:
        f.write(config)

    kp = KeywordParser(filename)
    matched_key = kp.get_key_for_section_value("machine-type-5", "intel")
    assert matched_key == "intel-18.0.5-mpich-7.7.15"


def test_matched_value_not_in_config_section_raises():
    kp = KeywordParser("test_supported_envs.ini")

    with pytest.raises(SystemExit) as excinfo:
        kp.get_key_for_section_value("machine-type-5", "bad_value")
    exc_msg = excinfo.value.args[0]

    assert ("ERROR:  Unable to find value 'bad_value' in values for "
            "'machine-type-5'") in exc_msg
