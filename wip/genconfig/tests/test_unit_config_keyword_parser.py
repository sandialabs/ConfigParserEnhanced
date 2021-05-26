from pathlib import Path
import pytest
import sys
import textwrap

root_dir = (Path.cwd()/".."
            if (Path.cwd()/"conftest.py").exists()
            else Path.cwd())
sys.path.append(str(root_dir))
from src.config_keyword_parser import ConfigKeywordParser


#####################
#  Keyword Parsing  #
#####################
@pytest.mark.parametrize("data", [
    {
        "build_name": "machine-type-5_mpi_serial_empire",
        "expected_options": {
            "use-mpi": "mpi",
            "node-type": "serial",
            "package-enables": "empire",
        },
    },
    {
        "build_name": "machine-type-3_no-mpi_openmp_sparc",
        "expected_options": {
            "use-mpi": "no-mpi",
            "node-type": "openmp",
            "package-enables": "sparc",
        },
    },
])
def test_keyword_parser_matches_correctly(data):
    ckp = ConfigKeywordParser(data["build_name"],
                              "test-supported-config-flags.ini")
    assert ckp.selected_options == data["expected_options"]


def test_parser_is_case_insensitive():
    build_name = "machine-type-5_MPI_serial_eMpIrE"
    expected_options = {
        "use-mpi": "mpi",
        "node-type": "serial",
        "package-enables": "empire",
    }

    ckp = ConfigKeywordParser(build_name, "test-supported-config-flags.ini")
    assert ckp.selected_options == expected_options


def test_parser_uses_correct_defaults():
    """
    The 'correct' defaults are defined as the first values in the list of
    options for a flag in the 'supported-config-flags.ini' file.
    """
    expected_options = {
        "use-mpi": "mpi",
        "node-type": "serial",
        "package-enables": "none",
    }
    ckp = ConfigKeywordParser("machine-type-3", "test-supported-config-flags.ini")
    assert ckp.selected_options == expected_options


###################
#  Error Checing  #
###################
@pytest.mark.parametrize("data", [
    {"build_name": "machine-type-5_mpi_no-mpi_serial_empire", "flag": "use-mpi"},
    {"build_name": "machine-type-5_mpi_serial_openmp_empire", "flag": "node-type"},
    {"build_name": "machine-type-5_mpi_serial_empire_sparc", "flag": "package-enables"},
])
def test_multiple_options_for_same_flag_in_build_name_raises(data):
    ckp = ConfigKeywordParser(data["build_name"],
                              "test-supported-config-flags.ini")

    match_str = f"Multiple options for '{data['flag']}' found in build name"
    with pytest.raises(ValueError, match=match_str):
        ckp.selected_options


##########
#  Misc  #
##########
def test_supported_flags_shown_correctly():
    test_ini = (
        "[DEFAULT]\n"
        "use-mpi:\n"
        "    mpi\n"
        "    no-mpi\n"
        "node-type:\n"
        "    serial\n"
        "    openmp\n"
    )
    with open("test_supported_flags_shown_correctly.ini", "w") as F:
        F.write(test_ini)

    ckp = ConfigKeywordParser("machine-type-5",
                              "test_supported_flags_shown_correctly.ini")
    msg = ckp.get_msg_showing_supported_flags("Message here.")

    msg_expected = textwrap.dedent(
        """
        |   ERROR:  Message here.
        |
        |   - Supported Flags Are:
        |     - use-mpi
        |       * Options:
        |         - mpi (default)
        |         - no-mpi
        |     - node-type
        |       * Options:
        |         - serial (default)
        |         - openmp
        """
    ).strip()

    assert msg_expected in msg
    assert ("|   See test_supported_flags_shown_correctly.ini for details."
            in msg)
