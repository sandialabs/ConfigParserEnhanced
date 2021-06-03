from pathlib import Path
import pytest
import sys
import textwrap

root_dir = (Path.cwd()/".."
            if (Path.cwd()/"conftest.py").exists()
            else Path.cwd())

sys.path.append(str(root_dir))
from gen_config import GenConfig


def get_expected_exc_msg(section_name, test_ini_filename):
    formatted_section_name = (
        "machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_mpi_serial_sparc"
    )
    msg_expected = textwrap.dedent(
        f"""
        |   ERROR:  The following configuration section:
        |             - {section_name}
        |
        |           Should be formatted in the following manner to include only valid
        |           options and to match the order of supported flags/options in
        |           'test-supported-config-flags.ini':
        |             - {formatted_section_name}
        |
        |   Please correct this section in '{test_ini_filename}'.
        """
    ).strip()

    return msg_expected


def run_common_test(test_ini_filename, section_name, should_raise):
    gc = GenConfig([
        "--config-specs", test_ini_filename,
        "--supported-config-flags", "test-supported-config-flags.ini",
        "--supported-systems", "test-supported-systems.ini",
        "--supported-envs", "test-supported-envs.ini",
        "--environment-specs", "test-environment-specs.ini",
        "any_build_name"
    ])


    if should_raise:
        with pytest.raises(ValueError) as excinfo:
            gc.validate_config_specs_ini()

        exc_msg = excinfo.value.args[0]
        msg_expected = get_expected_exc_msg(section_name, test_ini_filename)
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

    run_common_test(test_ini_filename, data["section_name"], data["should_raise"])


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

    run_common_test(test_ini_filename, data["section_name"], data["should_raise"])


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

    run_common_test(test_ini_filename, data["section_name"], data["should_raise"])
