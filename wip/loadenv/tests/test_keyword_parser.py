from pathlib import Path
import pytest
import sys

sys.path.append(str(Path.cwd())
                if (Path.cwd()/"keyword_parser.py").exists()
                else str(Path.cwd().parent))
from keyword_parser import KeywordParser


@pytest.mark.parametrize("keyword", [
    {
        "str": "machine-type-3-intel-19.0.4_openmpi-4.0.3_openmp_static_dbg",
        "system_name": "machine-type-3",
        "compiler": "intel-19.0.4",
        "kokkos_thread": "openmpi-4.0.3",
        "kokkos_arch": "",
        "complex": "no-complex",
        "shared_static": "static",
        "release_debug": "debug",
    },
    {
        "str": "sems-rhel7-cuda-9.2-Volta70-complex-shared-release-debug",
        "system_name": "sems-rhel7",
        "compiler": "cuda-9.2",
        "kokkos_thread": "serial",
        "kokkos_arch": "Volta70",
        "complex": "complex",
        "shared_static": "shared",
        "release_debug": "release-debug",
    },
    {
        "str": "machine-type-2-cuda-10.1.243-gnu-7.3.1-spmpi-rolling_complex_static_opt",
        "system_name": "machine-type-2",
        "compiler": "cuda-10.1.243-gnu-7.3.1",
        "kokkos_thread": "spmpi-rolling",
        "kokkos_arch": "",
        "complex": "complex",
        "shared_static": "static",
        "release_debug": "release",
    },
    # {
    #     "str": "Deploy-develop-ascic-clang-opt-serial-static",
    #     "system_name": "ascic",
    #     "compiler": "clang",
    #     "kokkos_thread": "serial",
    #     "kokkos_arch": "",
    #     "complex": "no-complex",
    #     "shared_static": "static",
    #     "release_debug": "release",
    # },
    # {
    #     "str": "Configure-Trilinos-intel-18-opt-serial-static",
    #     "system_name": "ascic",
    #     "compiler": "clang",
    #     "kokkos_thread": "serial",
    #     "kokkos_arch": "",
    #     "complex": "no-complex",
    #     "shared_static": "static",
    #     "release_debug": "release",
    # },
])
def test_keyword_parser_matches_correctly(keyword):
    parser = KeywordParser(keyword["str"])

    assert parser.system_name == keyword["system_name"]
    assert parser.compiler == keyword["compiler"]
    assert parser.kokkos_thread == keyword["kokkos_thread"]
    assert parser.kokkos_arch == keyword["kokkos_arch"]
    assert parser.complex == keyword["complex"]
    assert parser.shared_static == keyword["shared_static"]
    assert parser.release_debug == keyword["release_debug"]


###############################################################################
#                                 Exceptions                                  #
###############################################################################
#################
#  System Name  #
#################
def test_multiple_sys_names_given_raises():
    keyword_string = "machine-type-3-eclipse-intel-19.0.4_openmpi-4.0.3_static_dbg"
    with pytest.raises(Exception) as excinfo:
        KeywordParser(keyword_string)

    exception_msg = excinfo.value.args[0]
    assert "Can't specify more than one system name" in exception_msg


def test_no_sys_name_given_raises():
    keyword_string = "intel-19.0.4_openmpi-4.0.3_static_dbg"
    with pytest.raises(Exception) as excinfo:
        KeywordParser(keyword_string)

    exception_msg = excinfo.value.args[0]
    assert "No valid system name in the keyword string" in exception_msg


##############
#  Compiler  #
##############
@pytest.mark.parametrize("compilers", [
    {"str": "cuda-10.1.243-gnu-7.3.1", "should_raise": False},
    {"str": "intel-19.0.4-gnu-7.3.1", "should_raise": True},
])
def test_multiple_cpu_compilers_given_raises(compilers):
    keyword_string = f"machine-type-3-{compilers['str']}_openmpi-4.0.3_static_dbg"
    if compilers["should_raise"]:
        with pytest.raises(Exception) as excinfo:
            KeywordParser(keyword_string)
        exception_msg = excinfo.value.args[0]
        assert "Can't specify more than one CPU compiler" in exception_msg
    else:
        parser = KeywordParser(keyword_string)
        assert parser.compiler == compilers["str"]


def test_no_compiler_given_raises():
    keyword_string = "machine-type-3-openmpi-4.0.3_static_dbg"
    with pytest.raises(Exception) as excinfo:
        KeywordParser(keyword_string)

    exception_msg = excinfo.value.args[0]
    assert "No valid compiler found in the keyword string" in exception_msg


###################
#  Kokkos_Thread  #
###################
@pytest.mark.parametrize("second_kt", ["intelmpi-2018.4", "mpich2-3.2",
                                       "spmpi", "spmpi-rolling"])
def test_multiple_kokkos_threads_given_raises(second_kt):
    keyword_string = f"machine-type-3-intel-19.0.4_openmpi-4.0.3-{second_kt}_static_dbg"
    with pytest.raises(Exception) as excinfo:
        KeywordParser(keyword_string)

    exception_msg = excinfo.value.args[0]
    assert "Can't specify more than one MPI type" in exception_msg


#################
#  Kokkos_Arch  #
#################
@pytest.mark.parametrize("second_ka", ["BDW", "HSW", "Power8", "Power9", "KNL",
                                       "Kepler37", "Pascal60"])
def test_multiple_kokkos_archs_given_raises(second_ka):
    keyword_string = f"sems-rhel7-cuda-9.2-Volta70-{second_ka}-shared-release"
    with pytest.raises(Exception) as excinfo:
        KeywordParser(keyword_string)

    exception_msg = excinfo.value.args[0]
    assert "Can't specify more than one kokkos_arch" in exception_msg


@pytest.mark.parametrize("cuda_ka", ["Kepler37", "Pascal60", "Volta70"])
def test_cuda_kokkos_arch_specific_for_non_cuda_compiler_raises(cuda_ka):
    keyword_string = f"sems-rhel7-intel-19.0.4-{cuda_ka}-shared-release"
    with pytest.raises(Exception) as excinfo:
        KeywordParser(keyword_string)

    exception_msg = excinfo.value.args[0]
    msg = f"Can't use {cuda_ka} if 'cuda' is not specified as compiler"
    assert msg in exception_msg
