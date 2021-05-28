from pathlib import Path
import pytest
import sys
import textwrap

root_dir = (Path.cwd()/".."
            if (Path.cwd()/"conftest.py").exists()
            else Path.cwd())

sys.path.append(str(root_dir))
from gen_config import GenConfig


def test_config_specs_with_multiple_sections_that_expand_equally_raises():
    """
    Suppose your `supported-config-flags.ini` looks like::

        # supported-config-flags.ini
        [configure-flags]
        use-mpi:  SELECT-ONE
            mpi
            no-mpi
        node-type:  SELECT-ONE
            serial
            openmp
        package-enables:  SELECT-MANY
            none
            empire
            sparc
            muelu
            jmgate

    Now, suppose your `config-specs.ini` has the following two sections::

        # config-specs.ini
        [machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_sparc]
        # set configure flags here

        [machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_serial_mpi_sparc]
        # set configure flags here

    These two sections are functionally equivalent since both will select:
        * use-mpi = mpi (default)
        * node-type = serial (default)
        * package-enables = sparc

    Since these are sections expand to the same full section name::

        [machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_mpi_serial_sparc]

    we should raise an exception for the duplicate sections.
    """
    gc = GenConfig([
        "--config-specs", "test-config-specs-duplicates.ini",
        "--supported-config-flags", "test-supported-config-flags.ini",
        "--supported-systems", "test-supported-systems.ini",
        "--supported-envs", "test-supported-envs.ini",
        "--environment-specs", "test-environment-specs.ini",
        "any_build_name"
    ])

    msg_expected = ("|   ERROR:  There are multiple sections in "
                    "'test-config-specs-duplicates.ini'\n")
    msg_expected += textwrap.dedent(
        """
        |           that specify the same configuration:
        |     - machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_sparc
        |     - machine-type-5_intel-19.0.4-mpich-7.7.15-hsw-openmp_serial_mpi_sparc
        |
        |   These both expand to use the following set of options:
        |     - use-mpi         = mpi    (default)
        |     - node-type       = serial (default)
        |     - package-enables = sparc
        |
        |   Please remove one of these duplicate sections.
        """
    ).strip()

    with pytest.raises(Exception) as excinfo:
        gc.validate_config_specs_ini()

    exc_msg = excinfo.value.args[0]
    assert msg_expected in exc_msg
