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
        "build_name": "machine-type-3_no-mpi_openmp_sparc_empire",
        "expected_options": {
            "use-mpi": "no-mpi",
            "node-type": "openmp",
            "package-enables": ["empire", "sparc"],
        },
    },
    {
        "build_name": "machine-type-3_openmp",
        "expected_options": {
            "use-mpi": "mpi",
            "node-type": "openmp",
            "package-enables": "none",
        },
    },
])
def test_keyword_parser_matches_correctly(data):
    ckp = ConfigKeywordParser(data["build_name"],
                              "test-supported-config-flags.ini")
    assert ckp.selected_options == data["expected_options"]


# TODO: Implement this if we decide to go this route.
# def test_parser_is_case_sensitive(capsys):
#     build_name = "machine-type-5_MPI_serial_eMpIrE"

#     ckp = ConfigKeywordParser(build_name, "test-supported-config-flags.ini")
#     ckp.selected_options

#     out, err = capsys.readouterr()
#     msg_expected = textwrap.dedent(
#         """
#         |   WARNING:
#         """
#     ).strip()


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


@pytest.mark.parametrize("data", [
    {
        "build_name": "machine-type-5_mpi_serial_none",
        "expected_selected_by_default_dict": {
            "use-mpi": False,
            "node-type": False,
            "package-enables": False,
        },
    },
    {
        "build_name": "machine-type-3",
        "expected_selected_by_default_dict": {
            "use-mpi": True,
            "node-type": True,
            "package-enables": True,
        },
    },
    {
        "build_name": "machine-type-3_openmp",
        "expected_selected_by_default_dict": {
            "use-mpi": True,
            "node-type": False,
            "package-enables": True,
        },
    },
])
def test_parser_correctly_stores_whether_options_were_selected_by_default(
    data
):
    ckp = ConfigKeywordParser(data["build_name"],
                              "test-supported-config-flags.ini")
    assert (ckp.flags_selected_by_default ==
            data["expected_selected_by_default_dict"])


###################
#  Error Checing  #
###################
@pytest.mark.parametrize("data", [
    {"build_name": "machine-type-5_mpi_no-mpi_serial_empire", "flag": "use-mpi"},
    {"build_name": "machine-type-5_mpi_serial_openmp_empire", "flag": "node-type"},
])
def test_multiple_options_for_select_one_flag_in_build_name_raises(data):
    ckp = ConfigKeywordParser(data["build_name"],
                              "test-supported-config-flags.ini")

    match_str = ("Multiple options found in build name for SELECT-ONE flag "
                 f"'{data['flag']}':")
    with pytest.raises(ValueError, match=match_str):
        ckp.selected_options


def test_flag_without_type_in_config_ini_raises():
    bad_ini = (
        "[configure-flags]\n"
        "use-mpi:  # No type specified here\n"
        "    mpi\n"
        "    no-mpi\n"
        "node-type:  SELECT-ONE\n"
        "    serial\n"
        "    openmp\n"
    )
    bad_ini_filename = "test_flag_without_type_in_config_ini_raises.ini"
    with open(bad_ini_filename, "w") as F:
        F.write(bad_ini)

    msg_expected = textwrap.dedent(
        """
        |   ERROR:  The options for the 'use-mpi' flag must begin with either
        |           'SELECT-ONE' or 'SELECT-MANY'.  For example:
        |
        |       use-mpi:  SELECT-ONE
        |         option_1
        |         option_2
        |
        |   Please modify your config file accordingly:
        |     'test_flag_without_type_in_config_ini_raises.ini'
        """
    ).strip()

    ckp = ConfigKeywordParser("machine-type-5", bad_ini_filename)
    with pytest.raises(ValueError, match=msg_expected):
        ckp.get_msg_showing_supported_flags("Message here.")


##########
#  Misc  #
##########
def test_supported_flags_shown_correctly():
    test_ini = (
        "[configure-flags]\n"
        "use-mpi:  SELECT-ONE\n"
        "    mpi\n"
        "    no-mpi\n"
        "node-type:  SELECT-ONE\n"
        "    serial\n"
        "    openmp\n"
    )
    test_ini_filename = "test_supported_flags_shown_correctly.ini"
    with open(test_ini_filename, "w") as F:
        F.write(test_ini)

    ckp = ConfigKeywordParser("machine-type-5", test_ini_filename)
    msg = ckp.get_msg_showing_supported_flags("Message here.")

    msg_expected = textwrap.dedent(
        """
        |   ERROR:  Message here.
        |
        |   - Supported Flags Are:
        |     - use-mpi
        |       * Options (SELECT-ONE):
        |         - mpi (default)
        |         - no-mpi
        |     - node-type
        |       * Options (SELECT-ONE):
        |         - serial (default)
        |         - openmp
        """
    ).strip()

    assert msg_expected in msg
    assert ("|   See test_supported_flags_shown_correctly.ini for details."
            in msg)
