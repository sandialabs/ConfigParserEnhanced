from configparserenhanced import ConfigParserEnhanced
import getpass
from pathlib import Path
import pytest
import sys
import textwrap
from unittest.mock import patch

root_dir = (Path.cwd()/".."
            if (Path.cwd()/"conftest.py").exists()
            else Path.cwd())

sys.path.append(str(root_dir))
from gen_config import GenConfig
import gen_config


###############################################################################
########################     Functionality     ################################
###############################################################################
@pytest.mark.parametrize("sys_name", ["machine-type-5", "machine-type-4"])
def test_list_configs_shows_correct_sections(sys_name, capsys):
    config_specs = ConfigParserEnhanced("test-config-specs.ini").configparserenhanceddata
    expected_configs = [_ for _ in config_specs.sections() if _.startswith(sys_name)]

    with pytest.raises(SystemExit) as excinfo:
        gen_config.main([
            "--config-specs", "test-config-specs.ini",
            "--supported-config-flags", "test-supported-config-flags.ini",
            "--supported-systems", "test-supported-systems.ini",
            "--supported-envs", "test-supported-envs.ini",
            "--environment-specs", "test-environment-specs.ini",
            "--list-configs",
            "--force", sys_name
        ])
    exc_msg, stderr = capsys.readouterr();

    for config in expected_configs:
        assert f"- {config}" in exc_msg


@pytest.mark.parametrize("data", [
    {
        "build_name": "machine-type-5_intel-hsw",
        "expected_complete_config":
        "machine-type-5 where INTEL-19.0.4-MPICH-7.7.15-HSW-OPENMP and MPI and SERIAL and NO-PACKAGE-ENABLES"
    }
])
def test_complete_config_generated_correctly(data):
    gc = GenConfig([
        "--config-specs", "test-config-specs.ini",
        "--supported-config-flags", "test-supported-config-flags.ini",
        "--supported-systems", "test-supported-systems.ini",
        "--supported-envs", "test-supported-envs.ini",
        "--environment-specs", "test-environment-specs.ini",
        "--force",
        data["build_name"]
    ])

    assert gc.complete_config == data["expected_complete_config"]


@pytest.mark.parametrize("data", [
    {
        "build_name": "machine-type-5_intel-hsw",
        "expected_args_str": "-DMPI_EXEC_NUMPROCS_FLAG:STRING=-p"
    },
    {
        "build_name": "machine-type-5_intel-hsw_sparc",
        "expected_args_str": ("-DMPI_EXEC_NUMPROCS_FLAG:STRING=-p \\\n"
                     "    -DTPL_ENABLE_MPI:BOOL=ON")
    },
    {
        "build_name": "machine-type-5_intel-hsw_empire_sparc",
        "expected_args_str": ("-DMPI_EXEC_NUMPROCS_FLAG:STRING=-p \\\n"
                     "    -DTPL_ENABLE_MPI:BOOL=ON \\\n"
                     "    -DTrilinos_ENABLE_Panzer:BOOL=ON")
    },
])
def test_bash_cmake_flags_generated_correctly(data):
    gen_config.main([
        "--config-specs", "test-config-specs.ini",
        "--supported-config-flags", "test-supported-config-flags.ini",
        "--supported-systems", "test-supported-systems.ini",
        "--supported-envs", "test-supported-envs.ini",
        "--environment-specs", "test-environment-specs.ini",
        "--force",
        data["build_name"]
    ])

    user = getpass.getuser()
    loc_file = Path(f"/tmp/{user}/.bash_cmake_args_loc")
    assert loc_file.exists()
    with open(loc_file, "r") as F:
        bash_cmake_args_loc = Path(F.read())
    with open(bash_cmake_args_loc, "r") as F:
        bash_cmake_args = F.read()

    assert bash_cmake_args == data["expected_args_str"]

    loc_file.unlink()
    bash_cmake_args_loc.unlink()


@pytest.mark.parametrize("data", [
    {
        "build_name": "machine-type-5_intel-hsw",
        "expected_fragment_contents": 'set(MPI_EXEC_NUMPROCS_FLAG -p CACHE STRING "from .ini configuration")'
    },
    {
        "build_name": "machine-type-5_intel-hsw_sparc",
        "expected_fragment_contents": (
            'set(MPI_EXEC_NUMPROCS_FLAG -p CACHE STRING "from .ini configuration")\n'
            'set(TPL_ENABLE_MPI ON CACHE BOOL "from .ini configuration")'
        )
    },
    {
        "build_name": "machine-type-5_intel-hsw_empire_sparc",
        "expected_fragment_contents": (
            'set(MPI_EXEC_NUMPROCS_FLAG -p CACHE STRING "from .ini configuration")\n'
            'set(TPL_ENABLE_MPI ON CACHE BOOL "from .ini configuration")\n'
            'set(Trilinos_ENABLE_Panzer ON CACHE BOOL "from .ini configuration")'
        )
    },
])
def test_cmake_fragment_file_stored_correctly(data):
    gen_config.main([
        "--config-specs", "test-config-specs.ini",
        "--supported-config-flags", "test-supported-config-flags.ini",
        "--supported-systems", "test-supported-systems.ini",
        "--supported-envs", "test-supported-envs.ini",
        "--environment-specs", "test-environment-specs.ini",
        "--cmake-fragment", "test_fragment.cmake",
        "--force",
        data["build_name"]
    ])
    with open("test_fragment.cmake", "r") as F:
        test_fragment_contents = F.read()

    assert test_fragment_contents == data["expected_fragment_contents"]


@pytest.mark.parametrize("data", [
    {"--yes flag": False, "should_exit": False, "user_input": ["Y"]},
    {"--yes flag": False, "should_exit": False, "user_input": ["8", "y"]},
    {"--yes flag": True, "should_exit": False, "user_input": []},
    {"--yes flag": False, "should_exit": True, "user_input": ["N"]},
    {"--yes flag": False, "should_exit": True, "user_input": ["8", "n"]},
])
@patch("gen_config.input")
def test_existing_cmake_fragment_file_asks_user_for_overwrite(mock_input, data):
    argv = [
        "--config-specs", "test-config-specs.ini",
        "--supported-config-flags", "test-supported-config-flags.ini",
        "--supported-systems", "test-supported-systems.ini",
        "--supported-envs", "test-supported-envs.ini",
        "--environment-specs", "test-environment-specs.ini",
        "--cmake-fragment", "test_fragment.cmake",
        "--force",
        "machine-type-5_intel-hsw"
    ]
    if data["--yes flag"]:
        argv.insert(-1, "--yes")

    expected_fragment_contents = (
        'set(MPI_EXEC_NUMPROCS_FLAG -p CACHE STRING "from .ini configuration")'
    )
    Path("test_fragment.cmake").touch()

    mock_input.side_effect = data["user_input"]
    if data["should_exit"]:
        with pytest.raises(SystemExit):
            gen_config.main(argv)
    else:
        gen_config.main(argv)
        with open("test_fragment.cmake", "r") as F:
            test_fragment_contents = F.read()

        assert test_fragment_contents == expected_fragment_contents

    if not data["--yes flag"]:
        script_input_text = mock_input.call_args[0][0]
        if data["user_input"][0].lower() not in ["y", "n"]:
            assert "not recognized" in script_input_text
        else:
            assert "not recognized" not in script_input_text


###############################################################################
##########################     Validation     #################################
###############################################################################
def get_expected_exc_msg(section_names, test_ini_filename):
    formatted_section_name = "machine-type-5 where INTEL-19.0.4-MPICH-7.7.15-HSW-OPENMP and MPI and SERIAL and SPARC"
    msg_expected = textwrap.dedent(
        f"""
        |   ERROR:  The following section(s) in your config-specs.ini file
        |           should be formatted in the following manner to include only valid
        |           options and to match the order of supported flags/options in
        |           'test-supported-config-flags.ini':
        |
        |           -  {{current_section_name}}
        |           -> {{formatted_section_name}}
        |
        """
    ).strip()
    msg_expected += "\n"

    if type(section_names) == list:
        for section_name in section_names:
            msg_expected += (
                f"|           -  {section_name}\n"
                f"|           -> {formatted_section_name}\n|\n"
            )
    else:
        msg_expected += (
            f"|           -  {section_names}\n"
            f"|           -> {formatted_section_name}\n|\n"
        )

    msg_expected += f"|   Please correct these sections in '{test_ini_filename}'."

    return msg_expected


def run_common_validation_test(test_ini_filename, section_names, should_raise):
    gc = GenConfig([
        "--config-specs", test_ini_filename,
        "--supported-config-flags", "test-supported-config-flags.ini",
        "--supported-systems", "test-supported-systems.ini",
        "--supported-envs", "test-supported-envs.ini",
        "--environment-specs", "test-environment-specs.ini",
        "--force",
        "machine-type-5_any_build_name"
    ])


    if should_raise:
        with pytest.raises(ValueError) as excinfo:
            gc.validate_config_specs_ini()

        exc_msg = excinfo.value.args[0]
        msg_expected = get_expected_exc_msg(section_names, test_ini_filename)
        assert msg_expected in exc_msg


@pytest.mark.parametrize("data", [
    {
        "section_name":
        "machine-type-5 where INTEL-19.0.4-MPICH-7.7.15-HSW-OPENMP and MPI and SERIAL and SPARC",
        "should_raise": False
    },
    {
        "section_name":
        "machine-type-5 where INTEL-19.0.4-MPICH-7.7.15-HSW-OPENMP and SERIAL and SPARC",
        "should_raise": True
    },
    {
        "section_name":
        "machine-type-5 where INTEL-19.0.4-MPICH-7.7.15-HSW-OPENMP and SPARC",
        "should_raise": True
    },
])
def test_section_without_options_specified_for_all_flags_raises(data):
    bad_config_specs = (
        f"[{data['section_name']}]\n"
        "opt-set-cmake-var CMAKE_BUILD_TYPE STRING : DEBUG\n"
    )
    test_ini_filename = "test_bad_config_specs_section_incorrect_order.ini"
    with open(test_ini_filename, "w") as F:
        F.write(bad_config_specs)

    run_common_validation_test(test_ini_filename, data["section_name"], data["should_raise"])


@pytest.mark.parametrize("data", [
    {
        "section_name":
        "machine-type-5 where INTEL-19.0.4-MPICH-7.7.15-HSW-OPENMP and MPI and SERIAL and SPARC",
        "should_raise": False
    },
    {
        "section_name":
        "machine-type-5 where INTEL-19.0.4-MPICH-7.7.15-HSW-OPENMP and SERIAL and MPI and SPARC",
        "should_raise": True
    },
    {
        "section_name":
        "machine-type-5 where INTEL-19.0.4-MPICH-7.7.15-HSW-OPENMP and SPARC and SERIAL and MPI",
        "should_raise": True
    },
])
def test_section_with_incorrect_flag_order_raises(data):
    bad_config_specs = (
        f"[{data['section_name']}]\n"
        "opt-set-cmake-var CMAKE_BUILD_TYPE STRING : DEBUG\n"
    )
    test_ini_filename = "test_bad_config_specs_section_incorrect_order.ini"
    with open(test_ini_filename, "w") as F:
        F.write(bad_config_specs)

    run_common_validation_test(test_ini_filename, data["section_name"], data["should_raise"])


@pytest.mark.parametrize("data", [
    {
        "section_name":
        "machine-type-5 where INTEL-19.0.4-MPICH-7.7.15-HSW-OPENMP and MPI and SERIAL and SPARC",
        "should_raise": False
    },
    {
        "section_name":
        ("machine-type-5 where INTEL-19.0.4-MPICH-7.7.15-HSW-OPENMP and MPI and SERIAL and SPARC"
         " and NOT-AN-OPTION"),
        "should_raise": True
    },
])
def test_items_in_config_specs_sections_that_arent_options_raises(data):
    """
    Something like the folliwing in `config-specs.ini` should raise an
    exception::

        # config-specs.ini
        [machine-type-5 where INTEL-19.0.4-MPICH-7.7.15-HSW-OPENMP and NOT-AN-OPTION and SPARC]
        #                                         invalid ---^___________^
    """
    bad_config_specs = (
        f"[{data['section_name']}]\n"
        "opt-set-cmake-var CMAKE_BUILD_TYPE STRING : DEBUG\n"
    )
    test_ini_filename = "test_bad_config_specs_section_item_not_an_option.ini"
    with open(test_ini_filename, "w") as F:
        F.write(bad_config_specs)

    run_common_validation_test(test_ini_filename, data["section_name"], data["should_raise"])


def test_multiple_invalid_config_specs_sections_are_shown_in_one_err_msg():
    bad_section_names = [
        "machine-type-5 where INTEL-19.0.4-MPICH-7.7.15-HSW-OPENMP and SERIAL and SPARC",
        "machine-type-5 where INTEL-19.0.4-MPICH-7.7.15-HSW-OPENMP and MPI and SPARC and SERIAL",
        "machine-type-5 where INTEL-19.0.4-MPICH-7.7.15-HSW-OPENMP and MPI and SERIAL and SPARC and NOT-AN-OPTION"
    ]
    bad_config_specs = ""
    for sec_name in bad_section_names:
        bad_config_specs += (
            f"[{sec_name}]\n"
            "opt-set-cmake-var CMAKE_BUILD_TYPE STRING : DEBUG\n\n"
        )

    test_ini_filename = "test_config_specs_multiple_invalid_sections.ini"
    with open(test_ini_filename, "w") as F:
        F.write(bad_config_specs)

    should_raise = True
    run_common_validation_test(test_ini_filename, bad_section_names, should_raise)
