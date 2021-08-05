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
        "expected_complete_config": "machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_mpi_serial_none"
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
        "expected_args_str": '-DMPI_EXEC_NUMPROCS_FLAG:STRING="-p"'
    },
    {
        "build_name": "machine-type-5_intel-hsw_sparc",
        "expected_args_str": ('-DMPI_EXEC_NUMPROCS_FLAG:STRING="-p" \\\n'
                     '    -DTPL_ENABLE_MPI:BOOL=ON')
    },
    {
        "build_name": "machine-type-5_intel-hsw_empire_sparc",
        "expected_args_str": ('-DMPI_EXEC_NUMPROCS_FLAG:STRING="-p" \\\n'
                     '    -DTPL_ENABLE_MPI:BOOL=ON \\\n'
                     '    -DTrilinos_ENABLE_Panzer:BOOL=ON')
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

# Section Name Validation
# =======================
def get_expected_exc_msg(section_names, test_ini_filename):
    formatted_section_name = "machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_mpi_serial_sparc"
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
        "machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_mpi_serial_sparc",
        "should_raise": False
    },
    {
        "section_name":
        "machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_serial_sparc",
        "should_raise": True
    },
    {
        "section_name":
        "machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_sparc",
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
        "machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_mpi_serial_sparc",
        "should_raise": False
    },
    {
        "section_name":
        "machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_serial_mpi_sparc",
        "should_raise": True
    },
    {
        "section_name":
        "machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_sparc_serial_mpi",
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
        "machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_mpi_serial_sparc",
        "should_raise": False
    },
    {
        "section_name":
        ("machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_mpi_serial_sparc"
         "_not-an-option"),
        "should_raise": True
    },
])
def test_items_in_config_specs_sections_that_arent_options_raises(data):
    """
    Something like the folliwing in `config-specs.ini` should raise an
    exception::

        # config-specs.ini
        [machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_not-an-option_sparc]
        #                               invalid ---^___________^
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
        "machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_serial_sparc",
        "machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_mpi_sparc_serial",
        "machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_mpi_serial_sparc_not-an-option"
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

# Operation Validation
# ====================
@pytest.mark.parametrize("data", [
    {
        "operations": ["use"],
        "invalid": [],
        "should_raise": False
    },
    {
        "operations": ["use", "invalid-operation"],
        "invalid": ["invalid-operation"],
        "should_raise": True
    },
    {
        "operations": ["invalid-operation", "invalid-operation-2"],
        "invalid": ["invalid-operation", "invalid-operation-2"],
        "should_raise": True
    },
    {
        "operations": ["use", "invalidOperationNoDashes"],
        "invalid": ["invalidOperationNoDashes"],
        "should_raise": True
    },
])
def test_invalid_operations_raises(data):
    valid_section_name = "machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_mpi_serial_sparc"
    bad_config_specs = f"[{valid_section_name}]\n"
    for operation in data["operations"]:
        bad_config_specs += f"{operation} other info: here\n"

    test_ini_filename = "test_config_specs_invalid_operations.ini"
    with open(test_ini_filename, "w") as F:
        F.write(bad_config_specs)

    gc = GenConfig([
        "--config-specs", test_ini_filename,
        "--supported-config-flags", "test-supported-config-flags.ini",
        "--supported-systems", "test-supported-systems.ini",
        "--supported-envs", "test-supported-envs.ini",
        "--environment-specs", "test-environment-specs.ini",
        "--force",
        "machine-type-5_any_build_name"
    ])


    if data["should_raise"]:
        with pytest.raises(ValueError) as excinfo:
            gc.validate_config_specs_ini()

        exc_msg = excinfo.value.args[0]
        print(exc_msg)
        for invalid_op in data["invalid"]:
            assert f"- {invalid_op}" in exc_msg
    else:
        gc.validate_config_specs_ini()
