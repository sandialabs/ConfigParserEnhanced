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
    {
        "str": "Deploy-develop-ascic-clang-opt-serial-static",
        "system_name": "ascic",
        "compiler": "clang",
        "kokkos_thread": "serial",
        "kokkos_arch": "",
        "complex": "no-complex",
        "shared_static": "static",
        "release_debug": "release",
    },
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
def test_atdm_keyword_parser_matches_correctly(keyword):
    parser = KeywordParser(keyword["str"])

    assert parser.system_name == keyword["system_name"]
    assert parser.compiler == keyword["compiler"]
    assert parser.kokkos_thread == keyword["kokkos_thread"]
    assert parser.kokkos_arch == keyword["kokkos_arch"]
    assert parser.complex == keyword["complex"]
    assert parser.shared_static == keyword["shared_static"]
    assert parser.release_debug == keyword["release_debug"]
