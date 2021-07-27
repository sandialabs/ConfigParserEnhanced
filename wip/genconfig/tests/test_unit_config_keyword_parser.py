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
    ckp = ConfigKeywordParser("machine-type-3",
                              "test-supported-config-flags.ini")
    assert ckp.selected_options == expected_options


@pytest.mark.parametrize("data", [
    {
        "build_name": "machine-type-5",
        "expected_selected_options_str": "_mpi_serial_none",
    },
    {
        "build_name": "machine-type-5_openmp_muelu_sparc_no-mpi",
        "expected_selected_options_str": "_no-mpi_openmp_muelu_sparc",
        # Order here is dependent --------^________________________^
        # on the order within
        # supported-config-flags.ini
    },
])
def test_selected_options_str_generated_consistently(data):
    ckp = ConfigKeywordParser(data["build_name"],
                              "test-supported-config-flags.ini")
    assert ckp.selected_options_str == data["expected_selected_options_str"]


####################
#  Error Checking  #
####################
@pytest.mark.parametrize("data", [
    {"build_name": "machine-type-5_mpi_no-mpi_serial_empire", "flag": "use-mpi"},
    {"build_name": "machine-type-5_mpi_serial_openmp_empire", "flag": "node-type"},
])
def test_multiple_options_for_select_one_flag_in_build_name_raises(data):
    ckp = ConfigKeywordParser(data["build_name"],
                              "test-supported-config-flags.ini")

    match_str = ("Multiple options found in build name for SELECT_ONE flag "
                 f"'{data['flag']}':")
    with pytest.raises(ValueError, match=match_str):
        ckp.selected_options


def test_flag_without_type_in_config_ini_raises():
    bad_ini = (
        "[configure-flags]\n"
        "use-mpi:  # No type specified here\n"
        "    mpi\n"
        "    no-mpi\n"
        "node-type:  SELECT_ONE\n"
        "    serial\n"
        "    openmp\n"
    )
    bad_ini_filename = "test_flag_without_type_in_config_ini_raises.ini"
    with open(bad_ini_filename, "w") as F:
        F.write(bad_ini)

    msg_expected = textwrap.dedent(
        """
        |   ERROR:  The options for the 'use-mpi' flag must begin with either
        |           'SELECT_ONE' or 'SELECT_MANY'.  For example:
        |
        |       use-mpi:  SELECT_ONE
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


@pytest.mark.parametrize("multiple", [False, True])
def test_options_are_unique_for_all_flags(multiple):
    bad_ini = (
        "[configure-flags]\n"
        "kokkos-arch:  SELECT_MANY\n"
        "    none\n"
        "    KNC\n"
        "    KNL\n"
        "package-enables:  SELECT_MANY\n"
        "    none\n"
        "    empire\n"
        "    sparc\n" +
        ("    KNC" if multiple else "")
    )
    bad_ini_filename = "test_options_are_unique_for_all_flags.ini"
    with open(bad_ini_filename, "w") as F:
        F.write(bad_ini)

    msg_expected = textwrap.dedent(
        """
        |   ERROR:  The following options appear for multiple flags in
        |           'test_options_are_unique_for_all_flags.ini':
        |     - none
        """
    ).strip()
    msg_expected += (
        textwrap.dedent(
            """
            |     - KNC
            |
            |   Please change these to be named something unique for each flag
            |   in which they appear.
            """
        ).strip()
        if multiple else textwrap.dedent(
            """
            |
            |   Please change this to be named something unique for each flag
            |   in which it appears.
            """
        ).strip()
    )
    ckp = ConfigKeywordParser("machine-type-5", bad_ini_filename)
    with pytest.raises(SystemExit):
        ckp.selected_options_str


##########
#  Misc  #
##########
def test_supported_flags_shown_correctly():
    test_ini = (
        "[configure-flags]\n"
        "use-mpi:  SELECT_ONE\n"
        "    mpi\n"
        "    no-mpi\n"
        "node-type:  SELECT_ONE\n"
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
        |       * Options (SELECT_ONE):
        |         - mpi (default)
        |         - no-mpi
        |     - node-type
        |       * Options (SELECT_ONE):
        |         - serial (default)
        |         - openmp
        """
    ).strip()

    assert msg_expected in msg
    assert ("|   See test_supported_flags_shown_correctly.ini for details."
            in msg)


def test_config_keyword_parser_can_be_reused_for_multiple_build_names():
    data_1 = {
        "build_name": "machine-type-5",
        "expected_selected_options_str": "_mpi_serial_none",
        "expected_selected_options": {
            "use-mpi": "mpi",
            "node-type": "serial",
            "package-enables": "none",
        },
    }
    ckp = ConfigKeywordParser(data_1["build_name"],
                              "test-supported-config-flags.ini")
    assert ckp.selected_options == data_1["expected_selected_options"]
    assert ckp.selected_options_str == data_1["expected_selected_options_str"]


    data_2 = {
        "build_name": "machine-type-5_openmp_muelu_empire_sparc",
        "expected_selected_options_str": "_mpi_openmp_empire_muelu_sparc",
        "expected_selected_options": {
            "use-mpi": "mpi",
            "node-type": "openmp",
            "package-enables": ["empire", "muelu", "sparc"],
        },
    }
    # Setting build_name should be enough to clear old properties.
    ckp.build_name = data_2["build_name"]
    assert ckp.selected_options == data_2["expected_selected_options"]
    assert ckp.selected_options_str == data_2["expected_selected_options_str"]
