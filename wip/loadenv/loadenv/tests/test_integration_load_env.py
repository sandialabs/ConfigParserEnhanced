from pathlib import Path
import pytest
import sys
from unittest.mock import patch

root_dir = (Path.cwd()/".."
            if (Path.cwd()/"conftest.py").exists()
            else Path.cwd())

sys.path.append(str(root_dir))
from loadenv.LoadEnv import LoadEnv


####################################################
#  DetermineSystem + EnvKeywordParser Integration  #
####################################################
@pytest.mark.parametrize("inputs", [
    {
        "build_name": "intel-hsw",
        "hostname": "mutrino",
        "expected_env": "machine-type-1_intel-19.0.4-mpich-7.7.15-hsw-openmp"
    },
    {
        "build_name": "arm",
        "hostname": "stria",
        "expected_env": "machine-type-4_arm-20.1-openmpi-4.0.5-openmp"
    }
])
@patch("socket.gethostname")
def test_ekp_matches_correct_env_name(mock_gethostname, inputs):
    ###########################################################################
    # **This will need to change later once we have a more sophisticated**
    # **system determination in place.**
    ###########################################################################
    mock_gethostname.return_value = inputs["hostname"]

    le = LoadEnv(argv=[inputs["build_name"]])
    assert le.parsed_env_name == inputs["expected_env"]


#####################################################################
#  DetermineSystem + EnvKeywordParser + SetEnvironment Integration  #
#####################################################################
@pytest.mark.parametrize("inputs", [
    {
        "build_name": "intel-hsw",
        "hostname": "mutrino",
        "expected_env": "machine-type-1_intel-19.0.4-mpich-7.7.15-hsw-openmp",
        "expected_cmds": [
            "module load sparc-dev/intel-19.0.4_mpich-7.7.15_hsw",
            "envvar_op set OMP_NUM_THREADS 2",
            "envvar_op unset OMP_PLACES",
            "envvar_op prepend PATH /projects/netpub/atdm/ninja-1.8.2/bin",
            "envvar_op set LDFLAGS \"-L/opt/gcc/8.3.0/snos/lib/gcc/x86_64-suse-linux/8.3.0/ -lpthread ${LDFLAGS}\"",
            "envvar_op set LDFLAGS \"-L${MPI_ROOT}/lib -lmpich -lrt ${ATP_INSTALL_DIR}/lib/libAtpSigHandler.a ${ATP_INSTALL_DIR}/lib/libbreakpad_client_nostdlib.a ${LDFLAGS}\"",
            "envvar_op find_in_path MPICXX CC",
            "envvar_op find_in_path MPICC cc",
            "envvar_op find_in_path MPIF90 ftn",
            "envvar_op set CXX ${MPICXX}",
            "envvar_op set CC ${MPICC}",
            "envvar_op set F77 ${MPIF90}",
            "envvar_op set FC ${MPIF90}",
            "envvar_op set F90 ${MPIF90}",
        ],
    },
    {
        "build_name": "arm",
        "hostname": "stria",
        "expected_env": "machine-type-4_arm-20.0-openmpi-4.0.2-openmp",
        "expected_cmds": [
            "module purge",
            "module load devpack-arm/1.2.3",
            "module unload yaml-cpp",
            "module load ninja",
            "module load cmake/3.17.1",
            "envvar_op set MPI_ROOT ${MPI_DIR}",
            "envvar_op set BLAS_ROOT ${ARMPL_DIR}",
            "envvar_op set HDF5_ROOT ${HDF5_DIR}",
            "envvar_op set NETCDF_ROOT ${NETCDF_DIR}",
            "envvar_op set PNETCDF_ROOT ${PNETCDF_DIR}",
            "envvar_op set ZLIB_ROOT ${ZLIB_DIR}",
            "envvar_op set CGNS_ROOT ${CGNS_DIR}",
            "envvar_op set BOOST_ROOT ${BOOST_DIR}",
            "envvar_op set METIS_ROOT ${METIS_DIR}",
            "envvar_op set PARMETIS_ROOT ${PARMETIS_DIR}",
            "envvar_op set SUPERLUDIST_ROOT ${SUPLERLU_DIST_DIR}",
            "envvar_op set BINUTILS_ROOT ${BINUTILS_DIR}",
            "envvar_op unset HWLOC_LIBS",
            "envvar_op set CC mpicc",
            "envvar_op set CXX mpicxx",
            "envvar_op set FC mpif77",
            "envvar_op set F90 mpif90",
            "envvar_op set FC mpif90",
            "envvar_op find_in_path MPICC mpicc",
            "envvar_op find_in_path MPICXX mpicxx",
            "envvar_op find_in_path MPIF90 mpif90",
            "envvar_op set OMP_NUM_THREADS 2",
        ]
    }
])
@patch("socket.gethostname")
def test_correct_commands_are_saved(mock_gethostname, inputs):
    ###########################################################################
    # **This will need to change later once we have a more sophisticated**
    # **system determination in place.**
    ###########################################################################
    mock_gethostname.return_value = inputs["hostname"]
    le = LoadEnv(argv=[
        "--supported-systems", "test_supported_systems.ini",
        "--supported-envs", "test_supported_envs.ini",
        "--environment-specs", "test_environment_specs.ini",
        inputs["build_name"],
    ])
    assert le.parsed_env_name == inputs["expected_env"]

    le.write_load_matching_env()
    with open(le.tmp_load_matching_env_file, "r") as f:
        load_matching_env_contents = f.read()

    for expected_cmd in inputs["expected_cmds"]:
        assert expected_cmd in load_matching_env_contents


@pytest.mark.parametrize("output",
                         [None, "test_dir/load_matching_env.sh"])
@patch("socket.gethostname")
def test_load_matching_env_is_set_correctly_and_directories_are_created(
    mock_gethostname, output
):
    if output is not None:
        assert Path(output).exists() is False

    mock_gethostname.return_value = "stria"
    argv = (["arm"]
            if output is None
            else ["arm", "--output", output])
    le = LoadEnv(argv=argv)
    load_matching_env = le.write_load_matching_env()

    expected_file = (le.tmp_load_matching_env_file
                     if output is None else Path(output)).resolve()
    assert expected_file.parent.exists()
    assert load_matching_env == expected_file
