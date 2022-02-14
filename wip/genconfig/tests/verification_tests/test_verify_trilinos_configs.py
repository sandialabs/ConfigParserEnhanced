#!/usr/bin/env python3

import unittest
try:
    import mock
except ImportError:  # pragma nocover
    import unittest.mock as mock

import re
import sys
import subprocess
import pytest

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

# Insert GenConfig directory into path
from pathlib import Path
if (Path.cwd()/"conftest.py").exists():
    root_dir = Path.cwd()/".."
elif (Path.cwd()/"test_verify_trilinos_configs.py").exists():
    root_dir = Path.cwd()/"../.."
else:
    root_dir = Path.cwd()

sys.path.append(str(root_dir))
from gen_config import GenConfig

from configparserenhanced import ConfigParserEnhanced

class common_verify_helpers():
    '''Common verification test helpers'''

    def test_all_configs_are_in_map(self):
        '''This just guards against someone adding a configuration
           without adding it to this testing'''
        # assert that the key for each one is in the class map
        for ini_file_cfg in self.complete_configs:
            self.assertTrue(ini_file_cfg in self.config_verification_map.keys(),
                            msg="{ini_file_cfg_str} from {ini_file_str} not in self.config_verification_map.keys()".\
                            format(ini_file_cfg_str=ini_file_cfg, ini_file_str=self.gc.args.config_specs_file))

        for ver_test_cfg in self.config_verification_map.keys():
            self.assertTrue(ver_test_cfg in self.complete_configs,
                            msg="{ver_test_cfg_str} from self.config_verification_map.keys() not in {ini_file_str}".\
                            format(ver_test_cfg_str=ver_test_cfg, ini_file_str=self.gc.args.config_specs_file))

    def check_one_config(self,
                         cfg):
        '''Load the given test config and iterate through the checks'''

        tmp_gc_argv = self.gc_argv
        tmp_gc_argv.append(cfg)
        gc = GenConfig(argv=tmp_gc_argv)
        gc.load_load_env()
        try:
            tr_env = gc.load_env
            tr_env.load_set_environment()
            tr_env.apply_env()
            for tst_list in self.config_verification_map[cfg]:
                tst_list[0](gc, *tst_list[1:])
        except SystemExit as systemExit:
            pytest.skip("Wrong system: cannot run \"test_{config}\" on \"{hostname}\"".format(config=cfg,
                                                                                              hostname=subprocess.getoutput(
                                                                                                  "hostname")))

    def assert_lib_type(self, gc, lib_type):
        '''set default libraries for code and tpls to srchives'''
        if 'static' == lib_type:
            self.assert_package_config_contains(
                gc, 'set(BUILD_SHARED_LIBS OFF CACHE BOOL "from .ini configuration")')
            self.assert_package_config_contains(
                gc, 'set(TPL_FIND_SHARED_LIBS OFF CACHE BOOL "from .ini configuration")')
            self.assert_package_config_contains(
                gc, 'set(TPL_Boost_LIBRARIES $ENV{SEMS_BOOST_LIBRARY_PATH}/libboost_program_options.a;$ENV{SEMS_BOOST_LIBRARY_PATH}/libboost_system.a CACHE STRING "from .ini configuration")')
            self.assert_package_config_contains(
                gc, 'set(TPL_BoostLib_LIBRARIES $ENV{SEMS_BOOST_LIBRARY_PATH}/libboost_program_options.a;$ENV{SEMS_BOOST_LIBRARY_PATH}/libboost_system.a CACHE STRING "from .ini configuration")')
        elif 'shared' == lib_type:
            self.assert_package_config_contains(
                gc, 'set(BUILD_SHARED_LIBS ON CACHE BOOL "from .ini configuration")')
            self.assert_package_config_contains(
                gc, 'set(TPL_FIND_SHARED_LIBS ON CACHE BOOL "from .ini configuration")')
            self.assert_package_config_contains(
                gc, 'set(TPL_Boost_LIBRARIES $ENV{SEMS_BOOST_LIBRARY_PATH}/libboost_program_options.so;$ENV{SEMS_BOOST_LIBRARY_PATH}/libboost_system.so CACHE STRING "from .ini configuration")')
            self.assert_package_config_contains(
                gc, 'set(TPL_BoostLib_LIBRARIES $ENV{SEMS_BOOST_LIBRARY_PATH}/libboost_program_options.so;$ENV{SEMS_BOOST_LIBRARY_PATH}/libboost_system.so CACHE STRING "from .ini configuration")')

    def assert_python_version(self, gc, major, minor, micro, newer_ok=False):
        '''run python --version and confirm it matches the input values'''
        # the tricky bit is that this needs to run in a different interpreter
        # in case the environment is loading a different python
        version = subprocess.check_output('python --version',
                                          stderr=subprocess.STDOUT,
                                          shell=True)
        m = re.search(b"Python ([0-9]).([0-9]).([0-9]{0,1})", version)
        if not newer_ok:
            self.assertTrue(major == int(m.group(1)) and
                            minor == int(m.group(2)) and
                            micro == int(m.group(3)))
        else:
            self.assertTrue(major <= int(m.group(1)) and
                            minor <= int(m.group(2)) and
                            micro <= int(m.group(3)))

    def assert_openmpi_version(self, gc, major, minor, patch):
        '''Check that major, minor, patch matche the parsed output of mpirun --version'''
        version_string = subprocess.check_output('mpirun --version',
                                          stderr=subprocess.STDOUT,
                                          shell=True)
        m = re.search(b'mpirun \\(Open MPI\\) (\\d).(\\d{1,2}).(\\d)', version_string)
        self.assertTrue(major == int(m.group(1)) and
                        minor == int(m.group(2)) and
                        patch == int(m.group(3)))

    def assert_mpich_version(self, gc, major, minor):
        '''Check that major, minor, patch matche the parsed output of mpirun --version'''
        version_string = subprocess.check_output('mpirun --version',
                                          stderr=subprocess.STDOUT,
                                          shell=True)
        m = re.search(b'HYDRA build details:\n    Version:                                 (\\d).(\\d)', version_string)
        self.assertTrue(major == int(m.group(1)) and
                        minor == int(m.group(2)))

    def assert_package_config_contains(self, gc, check_string):
        '''Check that the  given string is in the set-cmake-var listing'''
        if gc.set_program_options is None:
            gc.load_set_program_options()
        if not gc.has_been_validated:
            gc.validate_config_specs_ini()

        cmake_options_list = gc.set_program_options.gen_option_list(
                gc.complete_config, "cmake_fragment"
            )
        # print(check_string, file=sys.stderr)
        # print(cmake_options_list, file=sys.stderr)
        try:
            self.assertTrue(check_string in cmake_options_list)
        except AssertionError as AE:
            print("The check_string ({check_str})  was not found in the list of cmake options".\
                  format(check_str=check_string),
                  file=sys.stderr)
            raise AE

    def assert_package_config_does_not_contain(self, gc, check_string):
        ''''''
        if gc.set_program_options is None:
            gc.load_set_program_options()
        if not gc.has_been_validated:
            gc.validate_config_specs_ini()

        cmake_options_list = gc.set_program_options.gen_option_list(
                gc.complete_config, "cmake_fragment"
            )
        for opt in cmake_options_list:
            self.assertTrue(check_string not in opt,
                            msg="The check_string ({check_str})  was found in the list of cmake options".\
                            format(check_str=check_string))

    def assert_clang_version(self, gc, major, minor, micro):
        '''Run clang --version and check for exact match only'''
        version = subprocess.check_output('clang --version',
                                          stderr=subprocess.STDOUT,
                                          shell=True)
        m = re.search(b"clang version ([0-9]{1,2}).([0-9]).([0-9]{0,1}).*", version)
        self.assertTrue(major == int(m.group(1)) and
                        minor == int(m.group(2)) and
                        micro == int(m.group(3)))

    def assert_cuda_version(self, gc, major, minor, micro):
        '''Run nvcc --version and check for exact match only'''
        version = subprocess.check_output('nvcc --version',
                                          stderr=subprocess.STDOUT,
                                          shell=True)
        m = re.search(b"release.*V([0-9]{1,2}).([0-9]).([0-9]{1,3}).*", version)
        self.assertTrue(major == int(m.group(1)) and
                        minor == int(m.group(2)) and
                        micro == int(m.group(3)))

    def assert_gcc_version(self, gc, major, minor, micro):
        '''Run gcc --version and check for exact match only'''
        version = subprocess.check_output('g++ --version',
                                          stderr=subprocess.STDOUT,
                                          shell=True)
        m = re.search(b"g\\+\\+ \\(GCC\\) ([0-9]).([0-9]).([0-9]{0,1}).*", version)
        self.assertTrue(major == int(m.group(1)) and
                        minor == int(m.group(2)) and
                        micro == int(m.group(3)))

    def assert_intel_version(self, gc, major, minor, micro):
        '''Run icpc --version and check for exact match only'''
        version = subprocess.check_output('icpc --version',
                                          stderr=subprocess.STDOUT,
                                          shell=True)
        m = re.search(b"icpc \\(ICC\\) ([0-9]{1,2}).([0-9]).([0-9]{0,1}).*", version)
        self.assertTrue(major == int(m.group(1)) and
                        minor == int(m.group(2)) and
                        micro == int(m.group(3)))

    def assert_kokkos_nodetype(self, gc, node_type):
        '''Verify that the given nodetype is specified
           serial
           cuda
           openmp'''
        if ('serial' is node_type):
            self.assert_package_config_contains(gc,
                                                'set(Trilinos_ENABLE_OpenMP OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Kokkos_ENABLE_OPENMP OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Phalanx_KOKKOS_DEVICE_TYPE SERIAL CACHE STRING \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Tpetra_INST_SERIAL ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Kokkos_ENABLE_CUDA_UVM OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Kokkos_ENABLE_CUDA OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Kokkos_ENABLE_CUDA_LAMBDA OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Tpetra_INST_CUDA OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Sacado_ENABLE_HIERARCHICAL_DFAD OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(TPL_ENABLE_CUDA OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(TPL_ENABLE_CUSPARSE OFF CACHE BOOL \"from .ini configuration\")')
        elif ('openmp' is node_type):
            self.assert_package_config_contains(gc,
                                                'set(Trilinos_ENABLE_OpenMP ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Kokkos_ENABLE_OPENMP ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Phalanx_KOKKOS_DEVICE_TYPE OPENMP CACHE STRING \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Tpetra_INST_SERIAL ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Kokkos_ENABLE_CUDA_UVM OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Kokkos_ENABLE_CUDA OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Kokkos_ENABLE_CUDA_LAMBDA OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Tpetra_INST_CUDA OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Sacado_ENABLE_HIERARCHICAL_DFAD OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(TPL_ENABLE_CUDA OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(TPL_ENABLE_CUSPARSE OFF CACHE BOOL \"from .ini configuration\")')
        elif ('cuda' is node_type):
            self.assert_package_config_contains(gc, 'set(Trilinos_ENABLE_OpenMP OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc, 'set(Kokkos_ENABLE_OPENMP OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc, 'set(Phalanx_KOKKOS_DEVICE_TYPE CUDA CACHE STRING \"from .ini configuration\")')
            self.assert_package_config_contains(gc, 'set(Tpetra_INST_SERIAL ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc, 'set(Kokkos_ENABLE_CUDA ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc, 'set(Kokkos_ENABLE_CUDA_LAMBDA ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc, 'set(Tpetra_INST_CUDA ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc, 'set(Sacado_ENABLE_HIERARCHICAL_DFAD ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc, 'set(TPL_ENABLE_CUDA ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc, 'set(TPL_ENABLE_CUSPARSE ON CACHE BOOL \"from .ini configuration\")')
        else:
            self.assertTrue(False, msg="Unsupported node_type: {nodetype_str} passed into assert_kokkos_nodetype".\
                            format(nodetype_str=node_type))

    def assert_build_type(self, gc, build_type):
        '''allowable types are
           release
           release-debug
           debug'''
        if 'release-debug' == build_type:
            self.assert_package_config_contains(gc,
                                                'set(CMAKE_BUILD_TYPE RELEASE CACHE STRING \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Trilinos_ENABLE_DEBUG ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_does_not_contain(gc,
                                                'set(Kokkos_ENABLE_DEBUG_BOUNDS_CHECK ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Kokkos_ENABLE_DEBUG_BOUNDS_CHECK OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Kokkos_ENABLE_DEBUG ON CACHE BOOL \"from .ini configuration\")')
        elif 'debug' == build_type:
            self.assert_package_config_contains(gc,
                                                'set(CMAKE_BUILD_TYPE DEBUG CACHE STRING \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Trilinos_ENABLE_DEBUG ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_does_not_contain(gc,
                                                'set(Kokkos_ENABLE_DEBUG_BOUNDS_CHECK ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Kokkos_ENABLE_DEBUG_BOUNDS_CHECK OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Kokkos_ENABLE_DEBUG ON CACHE BOOL \"from .ini configuration\")')
        else:
            self.assertTrue(False, msg="Unsupported build_type: {buildtype_str} passed into assert_build_type". \
                            format(buildtype_str=build_type))

    def assert_kokkos_arch(self, gc, kokkos_arch):
        '''Allowable types are not listed as other than no-kokkos-arch
           we can check for "Kokkos_ARCH_$(KOKKOS_ARCH) ON'''
        if "no-kokkos-arch" == kokkos_arch:
            self.assert_package_config_does_not_contain(gc, "Kokkos_ARCH")
        else:
            self.assert_package_config_contains(gc,
                                                'set(Kokkos_ARCH_{arch} ON CACHE BOOL \"from .ini configuration\")'.format(arch=kokkos_arch))

    def assert_use_asan(self, gc, use_asan):
        '''Address Sanitizer usage Off (False) or on (True)'''
        if use_asan:
            self.assert_package_config_contains(gc,
                                                'set(CMAKE_CXX_FLAGS "-g -O1 -fsanitize=address -fno-omit-frame-pointer" CACHE STRING \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(CMAKE_EXE_LINKER_FLAGS "-ldl -fsanitize=address" CACHE STRING \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Trilinos_EXTRA_LINK_FLAGS STRING "-ldl -fsanitize=address" CACHE STRING \"from .ini configuration\")')
        else:
            self.assert_package_config_does_not_contain(gc, "-fsanitize=address")

    def assert_use_fpic(self, gc, use_fpic):
        '''Position Independent Code (relocatable) usage Off (False) or on (True)'''
        if use_fpic:
            self.assert_package_config_contains(gc,
                                                'set(CMAKE_POSITION_INDEPENDENT_CODE ON CACHE BOOL \"from .ini configuration\")')
        else:
            self.assert_package_config_does_not_contain(gc, "CMAKE_POSITION_INDEPENDENT_CODE")

    def assert_use_mpi(self, gc, use_mpi):
        '''Message Passing Interface usage Off (False) or on (True)'''
        if use_mpi:
            self.assert_package_config_contains(gc,
                                                'set(TPL_ENABLE_MPI ON CACHE BOOL \"from .ini configuration\")')
        else:
            self.assert_package_config_contains(gc,
                                                'set(TPL_ENABLE_MPI OFF CACHE BOOL \"from .ini configuration\")')

    def assert_use_pt(self, gc, use_pt):
        '''Primary Tested Code usage Off (False) or on (True)
           Note this is actually always on and this toggle is for
           exclusivity so turns off secondary  code - I think?'''
        if use_pt:
            self.assert_package_config_contains(gc,
                                                'set(Trilinos_ENABLE_SECONDARY_TESTED_CODE OFF CACHE BOOL \"from .ini configuration\")')
        else:
            self.assert_package_config_contains(gc,
                                                'set(Trilinos_ENABLE_SECONDARY_TESTED_CODE ON CACHE BOOL \"from .ini configuration\")')

    def assert_use_complex(self, gc, use_complex):
        '''Use of the complex data type Off (False) or on (True)'''
        if use_complex:
            self.assert_package_config_contains(gc,
                                                'set(Trilinos_ENABLE_COMPLEX ON CACHE BOOL \"from .ini configuration\")')
        else:
            self.assert_package_config_contains(gc,
                                                'set(Trilinos_ENABLE_COMPLEX OFF CACHE BOOL \"from .ini configuration\")')

    def assert_use_rdc(self, gc, use_rdc):
        '''Use of relocatable device code for CUDA kernels'''
        if use_rdc:
            self.assert_package_config_contains(gc,
                                                'set(Kokkos_ENABLE_CUDA_RELOCATABLE_DEVICE_CODE ON CACHE BOOL \"from .ini configuration\")')
        else:
            self.assert_package_config_contains(gc,
                                                'set(Kokkos_ENABLE_CUDA_RELOCATABLE_DEVICE_CODE OFF CACHE BOOL \"from .ini configuration\")')

    def assert_use_uvm(self, gc, use_uvm):
        '''Use of unified virtual memory for CUDA'''
        if use_uvm:
            self.assert_package_config_contains(gc,
                                                'set(Kokkos_ENABLE_CUDA_UVM ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(KokkosKernels_INST_MEMSPACE_CUDAUVMSPACE ON CACHE BOOL \"from .ini configuration\")')
        else:
            self.assert_package_config_contains(gc,
                                                'set(Kokkos_ENABLE_CUDA_UVM OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(KokkosKernels_INST_MEMSPACE_CUDAUVMSPACE ON CACHE BOOL \"from .ini configuration\")')

    def assert_use_deprecated(self, gc, use_deprecated):
        '''Use of deprecated code'''
        if use_deprecated:
            self.assert_package_config_does_not_contain(gc,
                                                        'set(KOKKOS_ENABLE_DEPRECATED_CODE OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_does_not_contain(gc,
                                                        'set(Tpetra_ENABLE_DEPRECATED_CODE OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_does_not_contain(gc,
                                                        'set(Belos_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_does_not_contain(gc,
                                                        'set(Epetra_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_does_not_contain(gc,
                                                        'set(Ifpack2_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_does_not_contain(gc,
                                                        'set(Ifpack2_ENABLE_DEPRECATED_CODE OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_does_not_contain(gc,
                                                        'set(MueLu_ENABLE_DEPRECATED_CODE OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_does_not_contain(gc,
                                                        'set(Panzer_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_does_not_contain(gc,
                                                        'set(Phalanx_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_does_not_contain(gc,
                                                        'set(RTop_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_does_not_contain(gc,
                                                        'set(STK_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_does_not_contain(gc,
                                                        'set(Teuchos_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_does_not_contain(gc,
                                                        'set(Thyra_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_does_not_contain(gc,
                                                        'set(Claps_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_does_not_contain(gc,
                                                        'set(GlobiPack_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_does_not_contain(gc,
                                                        'set(OptiPack_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_does_not_contain(gc,
                                                        'set(Trios_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_does_not_contain(gc,
                                                        'set(Xpetra_ENABLE_DEPRECATED_CODE OFF CACHE BOOL \"from .ini configuration\" FORCE)')
        else:
            self.assert_package_config_contains(gc,
                                                'set(KOKKOS_ENABLE_DEPRECATED_CODE OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Tpetra_ENABLE_DEPRECATED_CODE OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Belos_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Epetra_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Ifpack2_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Ifpack2_ENABLE_DEPRECATED_CODE OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(MueLu_ENABLE_DEPRECATED_CODE OFF CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Panzer_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Phalanx_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(RTop_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(STK_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Teuchos_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Thyra_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Claps_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(GlobiPack_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(OptiPack_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Trios_HIDE_DEPRECATED_CODE ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Xpetra_ENABLE_DEPRECATED_CODE OFF CACHE BOOL \"from .ini configuration\" FORCE)')


class Test_verify_rhel7_configs(unittest.TestCase, common_verify_helpers):
    '''Class to iterate through all configs and verify that the loaded
       environment and cmake configure is what we expect'''

    def setUp(self):
        '''Comman data structures for all tests - done on a per-test basis'''
        self.config_verification_map = \
             {'rhel7_sems-gnu-7.2.0-anaconda3-serial_debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_no-mpi_no-pt_no-rdc_no-uvm_deprecated-on_pr-framework':
              [
               [self.assert_gcc_version, 7, 2, 0],
               [self.assert_python_version, 3, 7, 3],
               [self.assert_kokkos_nodetype, "serial"],
               [self.assert_build_type, "debug"],
               # [self.assert_lib_type, "shared"],
               [self.assert_kokkos_arch, "no-kokkos-arch"],
               [self.assert_use_asan, False],
               [self.assert_use_complex, False],
               [self.assert_use_fpic, False],
               [self.assert_use_mpi, False],
               [self.assert_use_pt, False],
               [self.assert_use_rdc, False],
               [self.assert_use_uvm, False],
               [self.assert_use_deprecated, True],
               [self.assert_package_config_contains, 'set(Trilinos_ENABLE_TrilinosFrameworkTests ON CACHE BOOL \"from .ini configuration\")'],
               # TODO: [self.assert_common_mpi_disables],
              ],
              'rhel7_sems-gnu-7.2.0-openmpi-1.10.1-serial_debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-uvm_deprecated-on_no-package-enables':
              [
               [self.assert_gcc_version, 7, 2, 0],
               [self.assert_python_version, 3,7,3],
               [self.assert_openmpi_version, 1, 10, 1],
               [self.assert_kokkos_nodetype, "serial"],
               [self.assert_build_type, "debug"],
               [self.assert_lib_type, "shared"],
               [self.assert_kokkos_arch, "no-kokkos-arch"],
               [self.assert_use_asan, False],
               [self.assert_use_complex, False],
               [self.assert_use_fpic, False],
               [self.assert_use_mpi, True],
               [self.assert_use_pt, False],
               [self.assert_use_rdc, False],
               [self.assert_use_uvm, False],
               [self.assert_use_deprecated, True],
               [self.assert_package_config_contains, 'set(Trilinos_ENABLE_Fortran OFF CACHE BOOL "from .ini configuration")'],
               [self.assert_package_config_contains, 'set(Trilinos_ENABLE_COMPLEX_DOUBLE ON CACHE BOOL "from .ini configuration")'],
               [self.assert_package_config_contains, 'set(CMAKE_CXX_FLAGS "-Wall -Wno-clobbered -Wno-vla -Wno-pragmas -Wno-unknown-pragmas -Wno-unused-local-typedefs -Wno-literal-suffix -Wno-deprecated-declarations -Wno-misleading-indentation -Wno-int-in-bool-context -Wno-maybe-uninitialized -Wno-nonnull-compare -Wno-address -Wno-inline -Wno-unused-but-set-variable -Wno-unused-variable -Wno-unused-label -Werror -DTRILINOS_HIDE_DEPRECATED_HEADER_WARNINGS" CACHE STRING "from .ini configuration")'],
               [self.assert_package_config_contains, 'set(TPL_ENABLE_ParMETIS OFF CACHE BOOL "from .ini configuration" FORCE)'],
              ],
              'rhel7_sems-gnu-7.2.0-serial_release-debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_no-mpi_no-pt_no-rdc_no-uvm_deprecated-on_no-package-enables':
              [[self.assert_gcc_version, 7, 2, 0],
               [self.assert_kokkos_nodetype, "serial"],
               [self.assert_build_type, "release-debug"],
               [self.assert_kokkos_arch, "no-kokkos-arch"],
               [self.assert_use_asan, False],
               [self.assert_use_complex, False],
               [self.assert_use_fpic, False],
               [self.assert_use_mpi, False],
               [self.assert_use_pt, False],
               [self.assert_use_rdc, False],
               [self.assert_use_uvm, False],
               [self.assert_use_deprecated, True],
               [self.assert_package_config_contains,
               'set(Trilinos_ENABLE_Fortran OFF CACHE BOOL "from .ini configuration")'],
               [self.assert_package_config_contains,
                'set(Trilinos_ENABLE_COMPLEX_DOUBLE ON CACHE BOOL "from .ini configuration")'],
               [self.assert_package_config_contains,
                'set(CMAKE_CXX_FLAGS "-Wall -Wno-clobbered -Wno-vla -Wno-pragmas -Wno-unknown-pragmas -Wno-unused-local-typedefs -Wno-literal-suffix -Wno-deprecated-declarations -Wno-misleading-indentation -Wno-int-in-bool-context -Wno-maybe-uninitialized -Wno-nonnull-compare -Wno-address -Wno-inline -Wno-unused-but-set-variable -Wno-unused-variable -Wno-unused-label -Werror -DTRILINOS_HIDE_DEPRECATED_HEADER_WARNINGS" CACHE STRING "from .ini configuration")'],
               [self.assert_package_config_contains,
                'set(TPL_ENABLE_ParMETIS OFF CACHE BOOL "from .ini configuration" FORCE)'],
               # TODO: [self.assert_common_mpi_disables],
              ],
              'rhel7_sems-gnu-7.2.0-openmpi-1.10.1-serial_release-debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-uvm_deprecated-on_pr': [],
              'rhel7_sems-gnu-7.2.0-openmpi-1.10.1-serial_release-debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-uvm_deprecated-on_no-package-enables':
              [[self.assert_gcc_version, 7, 2, 0],
               [self.assert_openmpi_version, 1, 10, 1],
               [self.assert_kokkos_nodetype, "serial"],
               [self.assert_build_type, "release-debug"],
               [self.assert_kokkos_arch, "no-kokkos-arch"],
               [self.assert_use_asan, False],
               [self.assert_use_fpic, False],
               [self.assert_use_mpi, True],
               [self.assert_use_pt, False],
               [self.assert_use_complex, False],
               [self.assert_use_rdc, False],
               [self.assert_use_uvm, False],
               [self.assert_use_deprecated, True],
               [self.assert_package_config_contains, 'set(MPI_EXEC_PRE_NUMPROCS_FLAGS --bind-to;none CACHE STRING \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(Tpetra_INST_SERIAL ON CACHE BOOL \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(Trilinos_ENABLE_COMPLEX_DOUBLE ON CACHE BOOL \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(Teko_DISABLE_LSCSTABALIZED_TPETRA_ALPAH_INV_D ON CACHE BOOL \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(CMAKE_CXX_FLAGS "-Wall -Wno-clobbered -Wno-vla -Wno-pragmas -Wno-unknown-pragmas -Wno-unused-local-typedefs -Wno-literal-suffix -Wno-deprecated-declarations -Wno-misleading-indentation -Wno-int-in-bool-context -Wno-maybe-uninitialized -Wno-nonnull-compare -Wno-address -Wno-inline -Werror -DTRILINOS_HIDE_DEPRECATED_HEADER_WARNINGS" CACHE STRING "from .ini configuration")'],
              ],
              'rhel7_sems-gnu-8.3.0-openmpi-1.10.1-openmp_release-debug_static_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-uvm_deprecated-on_pr':
              [[self.assert_gcc_version, 8, 3, 0],
               [self.assert_openmpi_version, 1, 10, 1],
               [self.assert_kokkos_nodetype, "openmp"],
               [self.assert_build_type, "release-debug"],
               [self.assert_kokkos_arch, "no-kokkos-arch"],
               [self.assert_use_asan, False],
               [self.assert_use_fpic, False],
               [self.assert_use_mpi, True],
               [self.assert_use_pt, False],
               [self.assert_use_complex, False],
               [self.assert_use_rdc, False],
               [self.assert_use_uvm, False],
               [self.assert_use_deprecated, True],
               [self.assert_package_config_contains, 'set(MPI_EXEC_PRE_NUMPROCS_FLAGS --bind-to;none CACHE STRING \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(Tpetra_INST_SERIAL ON CACHE BOOL \"from .ini configuration\" FORCE)'],
               [self.assert_package_config_contains, 'set(Trilinos_ENABLE_COMPLEX_DOUBLE ON CACHE BOOL \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(CMAKE_CXX_EXTENSIONS OFF CACHE BOOL \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(Teko_DISABLE_LSCSTABALIZED_TPETRA_ALPAH_INV_D ON CACHE BOOL \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(CMAKE_CXX_FLAGS "-fno-strict-aliasing -Wall -Wno-clobbered -Wno-vla -Wno-pragmas -Wno-unknown-pragmas -Wno-parentheses -Wno-unused-local-typedefs -Wno-literal-suffix -Wno-deprecated-declarations -Wno-misleading-indentation -Wno-int-in-bool-context -Wno-maybe-uninitialized -Wno-class-memaccess -Wno-inline -Wno-nonnull-compare -Wno-address -Werror -DTRILINOS_HIDE_DEPRECATED_HEADER_WARNINGS" CACHE STRING "from .ini configuration")'],
              ],
              'rhel7_sems-gnu-8.3.0-openmpi-1.10.1-openmp_release-debug_static_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-uvm_deprecated-off_pr':
              [[self.assert_gcc_version, 8, 3, 0],
               [self.assert_openmpi_version, 1, 10, 1],
               [self.assert_kokkos_nodetype, "openmp"],
               [self.assert_build_type, "release-debug"],
               [self.assert_kokkos_arch, "no-kokkos-arch"],
               [self.assert_use_asan, False],
               [self.assert_use_fpic, False],
               [self.assert_use_mpi, True],
               [self.assert_use_pt, False],
               [self.assert_use_complex, False],
               [self.assert_use_rdc, False],
               [self.assert_use_uvm, False],
               [self.assert_use_deprecated, False],
               [self.assert_package_config_contains, 'set(MPI_EXEC_PRE_NUMPROCS_FLAGS --bind-to;none CACHE STRING \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(Tpetra_INST_SERIAL ON CACHE BOOL \"from .ini configuration\" FORCE)'],
               [self.assert_package_config_contains, 'set(Trilinos_ENABLE_COMPLEX_DOUBLE ON CACHE BOOL \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(CMAKE_CXX_EXTENSIONS OFF CACHE BOOL \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(Teko_DISABLE_LSCSTABALIZED_TPETRA_ALPAH_INV_D ON CACHE BOOL \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(CMAKE_CXX_FLAGS "-fno-strict-aliasing -Wall -Wno-clobbered -Wno-vla -Wno-pragmas -Wno-unknown-pragmas -Wno-parentheses -Wno-unused-local-typedefs -Wno-literal-suffix -Wno-deprecated-declarations -Wno-misleading-indentation -Wno-int-in-bool-context -Wno-maybe-uninitialized -Wno-class-memaccess -Wno-inline -Wno-nonnull-compare -Wno-address -Werror -DTRILINOS_HIDE_DEPRECATED_HEADER_WARNINGS" CACHE STRING "from .ini configuration")'],
              ],
              'rhel7_sems-gnu-8.3.0-openmpi-1.10.1-openmp_release-debug_static_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-uvm_deprecated-on_no-package-enables':
              [[self.assert_gcc_version, 8, 3, 0],
               [self.assert_openmpi_version, 1, 10, 1],
               [self.assert_kokkos_nodetype, "openmp"],
               [self.assert_build_type, "release-debug"],
               [self.assert_kokkos_arch, "no-kokkos-arch"],
               [self.assert_use_asan, False],
               [self.assert_use_fpic, False],
               [self.assert_use_mpi, True],
               [self.assert_use_pt, False],
               [self.assert_use_complex, False],
               [self.assert_use_rdc, False],
               [self.assert_use_uvm, False],
               [self.assert_use_deprecated, True],
               [self.assert_package_config_contains, 'set(MPI_EXEC_PRE_NUMPROCS_FLAGS --bind-to;none CACHE STRING \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(Trilinos_ENABLE_COMPLEX_DOUBLE ON CACHE BOOL \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(CMAKE_CXX_EXTENSIONS OFF CACHE BOOL \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(Teko_DISABLE_LSCSTABALIZED_TPETRA_ALPAH_INV_D ON CACHE BOOL \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(CMAKE_CXX_FLAGS "-fno-strict-aliasing -Wall -Wno-clobbered -Wno-vla -Wno-pragmas -Wno-unknown-pragmas -Wno-parentheses -Wno-unused-local-typedefs -Wno-literal-suffix -Wno-deprecated-declarations -Wno-misleading-indentation -Wno-int-in-bool-context -Wno-maybe-uninitialized -Wno-class-memaccess -Wno-inline -Wno-nonnull-compare -Wno-address -Werror -DTRILINOS_HIDE_DEPRECATED_HEADER_WARNINGS" CACHE STRING "from .ini configuration")'],
              ],
              'rhel7_sems-clang-7.0.1-openmpi-1.10.1-serial_release-debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-uvm_deprecated-on_no-package-enables':
                  [[self.assert_clang_version, 7, 0, 1],
                   [self.assert_openmpi_version, 1, 10, 1],
                   [self.assert_kokkos_nodetype, "serial"],
                   [self.assert_build_type, "release-debug"],
                   [self.assert_rhel7_sems_lib_type, "shared"],
                   [self.assert_kokkos_arch, "no-kokkos-arch"],
                   [self.assert_use_asan, False],
                   [self.assert_use_complex, False],
                   [self.assert_use_fpic, False],
                   [self.assert_use_mpi, True],
                   [self.assert_use_pt, False],
                   [self.assert_use_rdc, False],
                   [self.assert_use_uvm, False],
                   [self.assert_use_deprecated, True],
                   [self.assert_package_config_contains, 'set(MPI_EXEC_PRE_NUMPROCS_FLAGS --bind-to;none CACHE STRING \"from .ini configuration\")'],
                   [self.assert_package_config_contains, 'set(Teko_DISABLE_LSCSTABALIZED_TPETRA_ALPAH_INV_D ON CACHE BOOL \"from .ini configuration\")'],
                  ],
                'rhel7_sems-clang-9.0.0-openmpi-1.10.1-serial_release-debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-uvm_deprecated-on_no-package-enables':
                  [
                   [self.assert_clang_version, 9, 0, 0],
                   [self.assert_openmpi_version, 1, 10, 1],
                   [self.assert_kokkos_nodetype, "serial"],
                   [self.assert_build_type, "release-debug"],
                   [self.assert_rhel7_sems_lib_type, "shared"],
                   [self.assert_kokkos_arch, "no-kokkos-arch"],
                   [self.assert_use_asan, False],
                   [self.assert_use_complex, False],
                   [self.assert_use_fpic, False],
                   [self.assert_use_mpi, True],
                   [self.assert_use_pt, False],
                   [self.assert_use_rdc, False],
                   [self.assert_use_uvm, False],
                   [self.assert_use_deprecated, True],
                   [self.assert_package_config_contains, 'set(MPI_EXEC_PRE_NUMPROCS_FLAGS --bind-to;none CACHE STRING \"from .ini configuration\")'],
                   [self.assert_package_config_contains, 'set(Teko_DISABLE_LSCSTABALIZED_TPETRA_ALPAH_INV_D ON CACHE BOOL \"from .ini configuration\")'],
                  ],
              'rhel7_sems-clang-10.0.0-openmpi-1.10.1-serial_release-debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-uvm_deprecated-on_no-package-enables':
                  [[self.assert_clang_version, 10, 0, 0],
                   [self.assert_openmpi_version, 1, 10, 1],
                   [self.assert_kokkos_nodetype, "serial"],
                   [self.assert_build_type, "release-debug"],
                   [self.assert_rhel7_sems_lib_type, "shared"],
                   [self.assert_kokkos_arch, "no-kokkos-arch"],
                   [self.assert_use_asan, False],
                   [self.assert_use_complex, False],
                   [self.assert_use_fpic, False],
                   [self.assert_use_mpi, True],
                   [self.assert_use_pt, False],
                   [self.assert_use_rdc, False],
                   [self.assert_use_uvm, False],
                   [self.assert_use_deprecated, True],
                   [self.assert_package_config_contains, 'set(MPI_EXEC_PRE_NUMPROCS_FLAGS --bind-to;none CACHE STRING \"from .ini configuration\")'],
                   [self.assert_package_config_contains, 'set(Teko_DISABLE_LSCSTABALIZED_TPETRA_ALPAH_INV_D ON CACHE BOOL \"from .ini configuration\")'],
                  ],
             'rhel7_sems-intel-17.0.1-mpich-3.2-serial_release-debug_static_no-kokkos-arch_no-asan_no-complex_fpic_mpi_no-pt_no-rdc_no-uvm_deprecated-on_no-package-enables':
                 [[self.assert_intel_version, 17, 0, 1],
                  [self.assert_mpich_version, 3, 2],
                  [self.assert_kokkos_nodetype, "serial"],
                  [self.assert_build_type, "release-debug"],
                  [self.assert_rhel7_sems_lib_type, "static"],
                  [self.assert_kokkos_arch, "no-kokkos-arch"],
                  [self.assert_use_asan, False],
                  [self.assert_use_complex, False],
                  [self.assert_use_fpic, True],
                  [self.assert_use_mpi, True],
                  [self.assert_use_pt, False],
                  [self.assert_use_rdc, False],
                  [self.assert_use_uvm, False],
                  [self.assert_use_deprecated, True],
                  [self.assert_package_config_contains, 'set(TPL_ENABLE_SuperLU OFF CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains,
                   'set(CMAKE_CXX_FLAGS "-Wall -Warray-bounds -Wchar-subscripts -Wcomment -Wenum-compare -Wformat -Wuninitialized -Wmaybe-uninitialized -Wmain -Wnarrowing -Wnonnull -Wparentheses -Wpointer-sign -Wreorder -Wreturn-type -Wsign-compare -Wsequence-point -Wtrigraphs -Wunused-function -Wunused-but-set-variable -Wunused-variable -Wwrite-strings" CACHE STRING "from .ini configuration")'],
                  [self.assert_rhel7_test_disables_intel],
                  ],
              'rhel7_sems-intel-19.0.5-mpich-3.2-serial_release-debug_static_no-kokkos-arch_no-asan_no-complex_fpic_mpi_no-pt_no-rdc_no-uvm_deprecated-on_no-package-enables':
              [[self.assert_intel_version, 19, 0, 5],
               [self.assert_mpich_version, 3, 2],
               [self.assert_kokkos_nodetype, "serial"],
               [self.assert_build_type, "release-debug"],
               [self.assert_rhel7_sems_lib_type, "shared"],
               [self.assert_kokkos_arch, "no-kokkos-arch"],
               [self.assert_use_asan, False],
               [self.assert_use_fpic, True],
               [self.assert_use_mpi, True],
               [self.assert_use_pt, False],
               [self.assert_use_complex, False],
               [self.assert_use_rdc, False],
               [self.assert_use_uvm, False],
               [self.assert_use_deprecated, True],
               [self.assert_package_config_contains, 'set(Phalanx_dynamic_data_layout_MPI_1_DISABLE ON CACHE BOOL \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(TPL_ENABLE_SuperLU ON CACHE BOOL "from .ini configuration")'],
               [self.assert_package_config_contains, 'set(TPL_ENABLE_Scotch OFF CACHE BOOL "from .ini configuration" FORCE)'],
               [self.assert_package_config_does_not_contain, 'set(Trilinos_ENABLE_Zoltan2 OFF CACHE BOOL "from .ini configuration" FORCE)'],
               [self.assert_package_config_does_not_contain, 'set(Trilinos_ENABLE_Zoltan2Core OFF CACHE BOOL "from .ini configuration" FORCE)'],
               [self.assert_package_config_does_not_contain, 'set(Trilinos_ENABLE_Zoltan2Sphynx OFF CACHE BOOL "from .ini configuration" FORCE)'],
               [self.assert_package_config_contains, 'set(Zoltan_ENABLE_Scotch OFF CACHE BOOL "from .ini configuration" FORCE)'],
               [self.assert_package_config_contains, 'set(CMAKE_CXX_FLAGS "-fPIC -Wall -Warray-bounds -Wchar-subscripts -Wcomment -Wenum-compare -Wformat -Wuninitialized -Wmaybe-uninitialized -Wmain -Wnarrowing -Wnonnull -Wparentheses -Wpointer-sign -Wreorder -Wreturn-type -Wsign-compare -Wsequence-point -Wtrigraphs -Wunused-function -Wunused-but-set-variable -Wunused-variable -Wwrite-strings" CACHE STRING "from .ini configuration")'],
               [self.assert_package_config_contains, 'set(MPI_BASE_DIR $ENV{SEMS_MPI_ROOT} CACHE PATH "from .ini configuration")'],
               [self.assert_rhel7_test_disables_intel],
               [self.assert_package_config_contains, 'set(Zoltan2_Partitioning1_EWeights_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration" FORCE)'],
               [self.assert_package_config_contains, 'set(Zoltan2_Partitioning1_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration" FORCE)'],
               [self.assert_package_config_contains, 'set(Zoltan2_Partitioning1_OneProc_EWeights_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration" FORCE)'],
               [self.assert_package_config_contains, 'set(Zoltan2_Partitioning1_OneProc_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration" FORCE)'],
               [self.assert_package_config_contains, 'set(Zoltan2_Partitioning1_OneProc_VWeights_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration" FORCE)'],
               [self.assert_package_config_contains, 'set(Zoltan2_Partitioning1_VWeights_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration" FORCE)'],
               [self.assert_package_config_contains, 'set(Zoltan2_pamgenMeshAdapterTest_scotch_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration" FORCE)'],
               [self.assert_package_config_contains, 'set(Zoltan2_scotch_example_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration" FORCE)'],
              ],
             }

        self.stdoutRedirect = mock.patch('sys.stdout', new_callable=StringIO)
        # self.stderrRedirect = mock.patch('sys.stderr', new_callable=StringIO)
        self.stdoutRedirect.start()
        # self.stderrRedirect.start()

        self.gc_argv = ["--supported-config-flags", "test-trilinos-supported-config-flags.ini",
                        "--config-specs", "test-trilinos-config-specs.ini",
                        "--supported-systems", "test-trilinos-supported-systems.ini",
                        "--supported-envs", "test-trilinos-supported-envs.ini",
                        "--environment-specs", "test-trilinos-environment-specs.ini"]

        # get the set of configurations
        self.gc = GenConfig(argv=self.gc_argv)

        config_specs = ConfigParserEnhanced(
            self.gc.args.config_specs_file
        ).configparserenhanceddata
        self.complete_configs = [_ for _ in config_specs.sections()
                                 if _.startswith('rhel7')]

    def tearDown(self):
        '''close-out after each test'''
        self.stdoutRedirect.stop()
        # self.stderrRedirect.stop()


    def test_rhel7_sems_gnu_7_2_0_anaconda3_serial_debug_shared_no_kokkos_arch_no_asan_no_complex_no_fpic_no_mpi_no_pt_no_rdc_no_uvm_deprecated_on_pr_framework(self):
        '''Check that the job setup for our python testing matches
           expectations'''
        self.check_one_config('rhel7_sems-gnu-7.2.0-anaconda3-serial_debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_no-mpi_no-pt_no-rdc_no-uvm_deprecated-on_pr-framework')

    def test_rhel7_sems_gnu_7_2_0_openmpi_1_10_1_serial_release_debug_shared_no_kokkos_arch_no_asan_no_complex_no_fpic_mpi_no_pt_no_rdc_no_uvm_deprecated_on_no_package_enables(self):
        '''Check that the gnu 7.2 job is set up without enabled packages for
           PR testing'''
        self.check_one_config('rhel7_sems-gnu-7.2.0-openmpi-1.10.1-serial_release-debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-uvm_deprecated-on_no-package-enables')

    def test_rhel7_sems_gnu_7_2_0_serial_release_debug_shared_no_kokkos_arch_no_asan_no_complex_no_fpic_no_mpi_no_pt_no_rdc_no_uvm_deprecated_on_no_package_enables(self):
        '''Check that the 7.2.0 serial job is set up and without package enables'''
        self.check_one_config('rhel7_sems-gnu-7.2.0-serial_release-debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_no-mpi_no-pt_no-rdc_no-uvm_deprecated-on_no-package-enables')

    def test_rhel7_sems_gnu_8_3_0_openmpi_1_10_1_openmp_release_debug_static_no_kokkos_arch_no_asan_no_complex_no_fpic_mpi_no_pt_no_rdc_no_uvm_deprecated_on_pr(self):
        '''Check that the gnu 8.3 job is set up with enabled packages for
           PR testing'''
        self.check_one_config('rhel7_sems-gnu-8.3.0-openmpi-1.10.1-openmp_release-debug_static_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-uvm_deprecated-on_pr')

    def test_rhel7_sems_gnu_8_3_0_openmpi_1_10_1_openmp_release_debug_static_no_kokkos_arch_no_asan_no_complex_no_fpic_mpi_no_pt_no_rdc_no_uvm_deprecated_off_pr(self):
        '''Check that the gnu 8.3 job is set up with enabled packages for
           PR testing and deprecated code OFF'''
        self.check_one_config('rhel7_sems-gnu-8.3.0-openmpi-1.10.1-openmp_release-debug_static_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-uvm_deprecated-off_pr')

    def test_rhel7_sems_gnu_8_3_0_openmpi_1_10_1_openmp_release_debug_static_no_kokkos_arch_no_asan_no_complex_no_fpic_mpi_no_pt_no_rdc_no_uvm_deprecated_on_no_package_enables(self):
        '''Check that the gnu 8.3 job is set up without enabled packages for
           PR testing'''
        self.check_one_config('rhel7_sems-gnu-8.3.0-openmpi-1.10.1-openmp_release-debug_static_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-uvm_deprecated-on_no-package-enables')

    def test_rhel7_sems_clang_9_0_0_openmpi_1_10_1_serial_release_debug_shared_no_kokkos_arch_no_asan_no_complex_no_fpic_mpi_no_pt_no_rdc_no_uvm_deprecated_on_no_package_enables(self):
        '''Check that the clang 10.0.0 job is set up without enabled packages for
           PR testing'''
        self.check_one_config('rhel7_sems-clang-9.0.0-openmpi-1.10.1-serial_release-debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-uvm_deprecated-on_no-package-enables')

    def test_rhel7_sems_clang_10_0_0_openmpi_1_10_1_serial_release_debug_shared_no_kokkos_arch_no_asan_no_complex_no_fpic_mpi_no_pt_no_rdc_no_uvm_deprecated_on_no_package_enables(self):
        '''Check that the clang 10.0.0 job is set up without enabled packages for
           PR testing'''
        self.check_one_config('rhel7_sems-clang-10.0.0-openmpi-1.10.1-serial_release-debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-uvm_deprecated-on_no-package-enables')

    def test_rhel7_sems_intel_19_0_5_mpich_3_2_serial_release_debug_static_no_kokkos_arch_no_asan_no_complex_fpic_mpi_no_pt_no_rdc_no_uvm_deprecated_on_no_package_enables(self):
        '''Check that the intel 19.0.5 job is set up without enabled packages for
           PR testing'''
        self.check_one_config('rhel7_sems-intel-19.0.5-mpich-3.2-serial_release-debug_static_no-kokkos-arch_no-asan_no-complex_fpic_mpi_no-pt_no-rdc_no-uvm_deprecated-on_no-package-enables')

    def test_rhel7_sems_intel_17_0_1_mpich_3_2_serial_release_debug_static_no_kokkos_arch_no_asan_no_complex_fpic_mpi_no_pt_no_rdc_no_uvm_deprecated_on_no_package_enables(self):
        '''Check that the intel 19.0.5 job is set up without enabled packages for
           PR testing'''
        self.check_one_config('rhel7_sems-intel-17.0.1-mpich-3.2-serial_release-debug_static_no-kokkos-arch_no-asan_no-complex_fpic_mpi_no-pt_no-rdc_no-uvm_deprecated-on_no-package-enables')


    def assert_rhel7_sems_lib_type(self, gc, lib_type):
        '''This just asserts LIB-TYPE|STATIC then the hdf libraries to shared libraries'''
        self.assert_lib_type(gc, lib_type)
        self.assert_package_config_contains(
            gc, 'set(TPL_HDF5_LIBRARIES $ENV{SEMS_HDF5_LIBRARY_PATH}/libhdf5_hl.so;$ENV{SEMS_HDF5_LIBRARY_PATH}/libhdf5.so;$ENV{SEMS_ZLIB_LIBRARY_PATH}/libz.so;-ldl CACHE STRING "from .ini configuration")')

    def assert_rhel7_test_disables_intel(self, gc):
        '''stock test disables used in both intel 17 and 19
          insert TDM rant here'''
        self.assert_package_config_contains(
            gc, 'set(Piro_AnalysisDriver_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(Piro_AnalysisDriverTpetra_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_adapters_epetra_test_sol_EpetraSROMSampleGenerator_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_adapters_minitensor_test_function_test_01_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_adapters_minitensor_test_sol_test_01_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_adapters_teuchos_test_sol_solSROMGenerator_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_burgers-control_example_01_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_diode-circuit_example_01_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_parabolic-control_example_01_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_parabolic-control_example_02_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_parabolic-control_example_03_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_parabolic-control_example_04_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_parabolic-control_example_05_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_PDE-OPT_0ld_adv-diff-react_example_02_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_PDE-OPT_0ld_poisson_example_01_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_PDE-OPT_0ld_stoch-adv-diff_example_01_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_PDE-OPT_adv-diff-react_example_02_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_PDE-OPT_navier-stokes_example_02_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_PDE-OPT_nonlinear-elliptic_example_01_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_PDE-OPT_nonlinear-elliptic_example_02_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_PDE-OPT_obstacle_example_01_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_PDE-OPT_topo-opt_poisson_example_01_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_poisson-control_example_01_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_poisson-control_example_02_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_poisson-inversion_example_02_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_tensor-opt_example_01_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_NonlinearProblemTest_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_test_algorithm_OptimizationSolverStatusTestInput_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_test_elementwise_BoundConstraint_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_test_function_BinaryConstraintCheck_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_test_function_ExplicitLinearConstraintCheck_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_test_step_AugmentedLagrangianStep_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_test_step_BoxConstrained_LineSearch_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_test_step_BoxConstrained_LM_TrustRegion_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_test_step_BoxConstrained_PrimalDualActiveSet_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_test_step_BoxConstrained_TrustRegion_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_test_step_CubicTest_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_test_step_fletcher_ALLPROBLEMS_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_test_step_fletcher_BOUNDFLETCHER_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_test_step_FletcherStep_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_test_step_interiorpoint_PrimalDualNewtonKrylov_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_test_step_InteriorPointStep_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_test_step_LineSearch_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_test_step_MoreauYosidaPenaltyStep_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_test_step_TrustRegion_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_tutorial_BoundAndInequality_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(MueLu_UnitTestsEpetra_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(MueLu_UnitTestsEpetra_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(MueLu_UnitTestsTpetra_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_poisson-inversion_example_01_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(Amesos2_SolverFactory_UnitTests_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(Amesos2_SuperLU_DIST_Solver_Test_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(Stratimikos_test_single_amesos2_tpetra_solver_driver_SuperLU_DIST_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(Intrepid2_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Werror" CACHE STRING "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(Pike_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Werror" CACHE STRING "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(Tempus_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Werror" CACHE STRING "from .ini configuration")')


class Test_verify_machine-type-4_configs(unittest.TestCase, common_verify_helpers):
    '''Class to iterate through all rhel7 configs and verify that the loaded
       environment and cmake configure is what we expect'''

    def setUp(self):
        '''Comman data structures for all tests - done on a per-test basis'''
        self.config_verification_map = \
             {'machine-type-4_cuda-10.1.243-gnu-8.3.1-spmpi-rolling_release_static_Volta70_Power9_no-asan_no-complex_no-fpic_mpi_pt_no-rdc_uvm_deprecated-on_no-package-enables':
              [
               [self.assert_gcc_version, 8, 3, 1],
               [self.assert_kokkos_nodetype, "cuda"],
               #TODO: [self.assert_build_type, "release"],
               [self.assert_lib_type, "static"],
               [self.assert_kokkos_arch, "VOLTA70"],
               [self.assert_kokkos_arch, "POWER9"],
               [self.assert_use_asan, False],
               [self.assert_use_complex, False],
               [self.assert_use_fpic, False],
               [self.assert_use_mpi, True],
               [self.assert_use_pt, True],
               [self.assert_use_rdc, False],
               [self.assert_use_uvm, True],
               [self.assert_use_deprecated, True],
               [self.assert_package_config_contains, 'set(TPL_ENABLE_Scotch OFF CACHE BOOL \"from .ini configuration\" FORCE)'],
              ],
              'machine-type-4_cuda-10.1.243-gnu-8.3.1-spmpi-rolling_release_static_Volta70_Power9_no-asan_no-complex_no-fpic_mpi_pt_rdc_uvm_deprecated-on_no-package-enables':
              [
               [self.assert_gcc_version, 8, 3, 1],
               [self.assert_kokkos_nodetype, "cuda"],
               #TODO: [self.assert_build_type, "release"],
               [self.assert_lib_type, "static"],
               [self.assert_kokkos_arch, "VOLTA70"],
               [self.assert_kokkos_arch, "POWER9"],
               [self.assert_use_asan, False],
               [self.assert_use_complex, False],
               [self.assert_use_fpic, False],
               [self.assert_use_mpi, True],
               [self.assert_use_pt, True],
               [self.assert_use_rdc, True],
               [self.assert_use_uvm, True],
               [self.assert_use_deprecated, True],
               [self.assert_package_config_contains, 'set(TPL_ENABLE_Scotch OFF CACHE BOOL \"from .ini configuration\" FORCE)'],
              ],
             }

        self.stdoutRedirect = mock.patch('sys.stdout', new_callable=StringIO)
        # self.stderrRedirect = mock.patch('sys.stderr', new_callable=StringIO)
        self.stdoutRedirect.start()
        # self.stderrRedirect.start()

        self.gc_argv = ["--supported-config-flags", "test-trilinos-supported-config-flags.ini",
                        "--config-specs", "test-trilinos-config-specs.ini",
                        "--supported-systems", "test-trilinos-supported-systems.ini",
                        "--supported-envs", "test-trilinos-supported-envs.ini",
                        "--environment-specs", "test-trilinos-environment-specs.ini"]

        # get the set of configurations
        self.gc = GenConfig(argv=self.gc_argv)

        config_specs = ConfigParserEnhanced(
            self.gc.args.config_specs_file
        ).configparserenhanceddata
        self.complete_configs = [_ for _ in config_specs.sections()
                                 if _.startswith('machine-type-4')]

    def tearDown(self):
        '''close-out after each test'''
        self.stdoutRedirect.stop()
        # self.stderrRedirect.stop()

    def test_machine-type-4_cuda_10_1_243_gnu_8_3_1_spmpi_rolling_release_static_Volta70_Power9_no_asan_no_complex_no_fpic_mpi_pt_no_rdc_uvm_deprecated_on_no_package_enables(self):
        '''Check that the job setup for our python testing matches
           expectations'''
        self.check_one_config('machine-type-4_cuda-10.1.243-gnu-8.3.1-spmpi-rolling_release_static_Volta70_Power9_no-asan_no-complex_no-fpic_mpi_pt_no-rdc_uvm_deprecated-on_no-package-enables')

    def test_machine-type-4_cuda_10_1_243_gnu_8_3_1_spmpi_rolling_release_static_Volta70_Power9_no_asan_no_complex_no_fpic_mpi_pt_rdc_uvm_deprecated_on_no_package_enables(self):
        '''Check that the job setup for our python testing matches
           expectations'''
        self.check_one_config('machine-type-4_cuda-10.1.243-gnu-8.3.1-spmpi-rolling_release_static_Volta70_Power9_no-asan_no-complex_no-fpic_mpi_pt_rdc_uvm_deprecated-on_no-package-enables')


class Test_verify_weaver_configs(unittest.TestCase, common_verify_helpers):
    '''Class to iterate through all configs and verify that the loaded
       environment and cmake configure is what we expect'''

    def setUp(self):
        '''Comman data structures for all tests - done on a per-test basis'''
        self.config_verification_map = \
             {'weaver_cuda-10.1.105-gnu-7.2.0-spmpi-rolling_release_static_Volta70_Power9_no-asan_complex_fpic_mpi_pt_no-rdc_no-uvm_deprecated-on_pr-framework-atdm':
                 [[self.assert_cuda_version, 10, 1, 105],
                  [self.assert_gcc_version, 7, 2, 0],
                  [self.assert_kokkos_nodetype, "cuda"],
                  #TODO: [self.assert_build_type, "release"],
                  [self.assert_lib_type, "static"],
                  [self.assert_kokkos_arch, "VOLTA70"],
                  [self.assert_kokkos_arch, "POWER9"],
                  [self.assert_use_asan, False],
                  [self.assert_use_complex, True],
                  [self.assert_use_fpic, True],
                  [self.assert_use_mpi, True],
                  [self.assert_use_pt, True],
                  [self.assert_use_rdc, False],
                  [self.assert_use_uvm, False],
                  [self.assert_use_deprecated, True],
                  [self.assert_weaver_test_disables_cuda],
                  [self.assert_package_config_contains, 'set(Trilinos_ENABLE_Kokkos ON CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains, 'set(TPL_ENABLE_Pthread OFF CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains, 'set(TPL_ENABLE_BinUtils OFF CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains, 'set(TPL_ENABLE_METIS OFF CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains, 'set(TPL_ENABLE_ParMETIS OFF CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains, 'set(TPL_ENABLE_Zlib OFF CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains, 'set(TPL_ENABLE_SuperLU OFF CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains, 'set(TPL_ENABLE_SuperLUDist OFF CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains, 'set(TPL_ENABLE_Scotch OFF CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains, 'set(TPL_ENABLE_HWLOC OFF CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains, 'set(TPL_ENABLE_CGNS OFF CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains, 'set(Trilinos_ENABLE_Stokhos OFF CACHE BOOL "from .ini configuration" FORCE)'],
                 ],
                 'weaver_cuda-10.1.105-gnu-7.2.0-spmpi-rolling_release_static_Volta70_Power9_no-asan_complex_fpic_mpi_pt_no-rdc_no-uvm_deprecated-on_no-package-enables':
                     [[self.assert_cuda_version, 10, 1, 105],
                      [self.assert_gcc_version, 7, 2, 0],
                      [self.assert_kokkos_nodetype, "cuda"],
                      # TODO: [self.assert_build_type, "release"],
                      [self.assert_lib_type, "static"],
                      [self.assert_kokkos_arch, "VOLTA70"],
                      [self.assert_kokkos_arch, "POWER9"],
                      [self.assert_use_asan, False],
                      [self.assert_use_complex, True],
                      [self.assert_use_fpic, True],
                      [self.assert_use_mpi, True],
                      [self.assert_use_pt, True],
                      [self.assert_use_rdc, False],
                      [self.assert_use_uvm, False],
                      [self.assert_use_deprecated, True],
                      [self.assert_weaver_test_disables_cuda],
                      [self.assert_package_config_contains,
                       'set(Trilinos_ENABLE_Kokkos ON CACHE BOOL "from .ini configuration" FORCE)'],
                      [self.assert_package_config_contains,
                       'set(TPL_ENABLE_Pthread OFF CACHE BOOL "from .ini configuration" FORCE)'],
                      [self.assert_package_config_contains,
                       'set(TPL_ENABLE_BinUtils OFF CACHE BOOL "from .ini configuration" FORCE)'],
                      [self.assert_package_config_contains,
                       'set(TPL_ENABLE_METIS OFF CACHE BOOL "from .ini configuration" FORCE)'],
                      [self.assert_package_config_contains,
                       'set(TPL_ENABLE_ParMETIS OFF CACHE BOOL "from .ini configuration" FORCE)'],
                      [self.assert_package_config_contains,
                       'set(TPL_ENABLE_Zlib OFF CACHE BOOL "from .ini configuration" FORCE)'],
                      [self.assert_package_config_contains,
                       'set(TPL_ENABLE_SuperLU OFF CACHE BOOL "from .ini configuration" FORCE)'],
                      [self.assert_package_config_contains,
                       'set(TPL_ENABLE_SuperLUDist OFF CACHE BOOL "from .ini configuration" FORCE)'],
                      [self.assert_package_config_contains,
                       'set(TPL_ENABLE_Scotch OFF CACHE BOOL "from .ini configuration" FORCE)'],
                      [self.assert_package_config_contains,
                       'set(TPL_ENABLE_HWLOC OFF CACHE BOOL "from .ini configuration" FORCE)'],
                      [self.assert_package_config_contains,
                       'set(TPL_ENABLE_CGNS OFF CACHE BOOL "from .ini configuration" FORCE)'],
                      [self.assert_package_config_contains,
                       'set(Trilinos_ENABLE_Stokhos OFF CACHE BOOL "from .ini configuration" FORCE)'],
                      ],
             'weaver_cuda-10.1.105-gnu-7.2.0-spmpi-rolling_release_static_Volta70_Power9_no-asan_complex_fpic_mpi_pt_no-rdc_uvm_deprecated-on_pr-framework-atdm':
                 [[self.assert_cuda_version, 10, 1, 105],
                  [self.assert_gcc_version, 7, 2, 0],
                  [self.assert_kokkos_nodetype, "cuda"],
                  #TODO: [self.assert_build_type, "release"],
                  [self.assert_lib_type, "static"],
                  [self.assert_kokkos_arch, "VOLTA70"],
                  [self.assert_kokkos_arch, "POWER9"],
                  [self.assert_use_asan, False],
                  [self.assert_use_complex, True],
                  [self.assert_use_fpic, True],
                  [self.assert_use_mpi, True],
                  [self.assert_use_pt, True],
                  [self.assert_use_rdc, False],
                  [self.assert_use_uvm, True],
                  [self.assert_use_deprecated, True],
                  [self.assert_weaver_test_disables_cuda],
                  [self.assert_package_config_contains, 'set(Trilinos_ENABLE_Kokkos ON CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains, 'set(TPL_ENABLE_Pthread OFF CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains, 'set(TPL_ENABLE_BinUtils OFF CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains, 'set(TPL_ENABLE_METIS OFF CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains, 'set(TPL_ENABLE_ParMETIS OFF CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains, 'set(TPL_ENABLE_Zlib OFF CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains, 'set(TPL_ENABLE_SuperLU OFF CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains, 'set(TPL_ENABLE_SuperLUDist OFF CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains, 'set(TPL_ENABLE_Scotch OFF CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains, 'set(TPL_ENABLE_HWLOC OFF CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains, 'set(TPL_ENABLE_CGNS OFF CACHE BOOL "from .ini configuration" FORCE)'],
                  [self.assert_package_config_contains, 'set(Trilinos_ENABLE_Stokhos OFF CACHE BOOL "from .ini configuration" FORCE)'],
                 ],
                 'weaver_cuda-10.1.105-gnu-7.2.0-spmpi-rolling_release_static_Volta70_Power9_no-asan_complex_fpic_mpi_pt_no-rdc_uvm_deprecated-on_no-package-enables':
                     [[self.assert_cuda_version, 10, 1, 105],
                      [self.assert_gcc_version, 7, 2, 0],
                      [self.assert_kokkos_nodetype, "cuda"],
                      # TODO: [self.assert_build_type, "release"],
                      [self.assert_lib_type, "static"],
                      [self.assert_kokkos_arch, "VOLTA70"],
                      [self.assert_kokkos_arch, "POWER9"],
                      [self.assert_use_asan, False],
                      [self.assert_use_complex, True],
                      [self.assert_use_fpic, True],
                      [self.assert_use_mpi, True],
                      [self.assert_use_pt, True],
                      [self.assert_use_rdc, False],
                      [self.assert_use_uvm, True],
                      [self.assert_use_deprecated, True],
                      [self.assert_weaver_test_disables_cuda],
                      [self.assert_package_config_contains,
                       'set(Trilinos_ENABLE_Kokkos ON CACHE BOOL "from .ini configuration" FORCE)'],
                      [self.assert_package_config_contains,
                       'set(TPL_ENABLE_Pthread OFF CACHE BOOL "from .ini configuration" FORCE)'],
                      [self.assert_package_config_contains,
                       'set(TPL_ENABLE_BinUtils OFF CACHE BOOL "from .ini configuration" FORCE)'],
                      [self.assert_package_config_contains,
                       'set(TPL_ENABLE_METIS OFF CACHE BOOL "from .ini configuration" FORCE)'],
                      [self.assert_package_config_contains,
                       'set(TPL_ENABLE_ParMETIS OFF CACHE BOOL "from .ini configuration" FORCE)'],
                      [self.assert_package_config_contains,
                       'set(TPL_ENABLE_Zlib OFF CACHE BOOL "from .ini configuration" FORCE)'],
                      [self.assert_package_config_contains,
                       'set(TPL_ENABLE_SuperLU OFF CACHE BOOL "from .ini configuration" FORCE)'],
                      [self.assert_package_config_contains,
                       'set(TPL_ENABLE_SuperLUDist OFF CACHE BOOL "from .ini configuration" FORCE)'],
                      [self.assert_package_config_contains,
                       'set(TPL_ENABLE_Scotch OFF CACHE BOOL "from .ini configuration" FORCE)'],
                      [self.assert_package_config_contains,
                       'set(TPL_ENABLE_HWLOC OFF CACHE BOOL "from .ini configuration" FORCE)'],
                      [self.assert_package_config_contains,
                       'set(TPL_ENABLE_CGNS OFF CACHE BOOL "from .ini configuration" FORCE)'],
                      [self.assert_package_config_contains,
                       'set(Trilinos_ENABLE_Stokhos OFF CACHE BOOL "from .ini configuration" FORCE)'],
                      ],
             }

        self.stdoutRedirect = mock.patch('sys.stdout', new_callable=StringIO)
        # self.stderrRedirect = mock.patch('sys.stderr', new_callable=StringIO)
        self.stdoutRedirect.start()
        # self.stderrRedirect.start()

        self.gc_argv = ["--supported-config-flags", "test-trilinos-supported-config-flags.ini",
                        "--config-specs", "test-trilinos-config-specs.ini",
                        "--supported-systems", "test-trilinos-supported-systems.ini",
                        "--supported-envs", "test-trilinos-supported-envs.ini",
                        "--environment-specs", "test-trilinos-environment-specs.ini"]

        # get the set of configurations
        self.gc = GenConfig(argv=self.gc_argv)

        config_specs = ConfigParserEnhanced(
            self.gc.args.config_specs_file
        ).configparserenhanceddata
        self.complete_configs = [_ for _ in config_specs.sections()
                                 if _.startswith('weaver')]

    def tearDown(self):
        '''close-out after each test'''
        self.stdoutRedirect.stop()
        # self.stderrRedirect.stop()

    def test_weaver_cuda_10_1_105_gnu_7_2_0_spmpi_rolling_release_static_Volta70_Power9_no_asan_complex_fpic_mpi_pt_no_rdc_no_uvm_deprecated_on_pr_framework_atdm(self):
        '''Check that the cuda 10.1.105 uvm=off job is set up with certain
        enabled packages for PR testing'''
        self.check_one_config('weaver_cuda-10.1.105-gnu-7.2.0-spmpi-rolling_release_static_Volta70_Power9_no-asan_complex_fpic_mpi_pt_no-rdc_no-uvm_deprecated-on_pr-framework-atdm')

    def test_weaver_cuda_10_1_105_gnu_7_2_0_spmpi_rolling_release_static_Volta70_Power9_no_asan_complex_fpic_mpi_pt_no_rdc_no_uvm_deprecated_on_no_package_enables(self):
        '''Check that the cuda 10.1.105 uvm=off job is set up without enabled packages for
           PR testing'''
        self.check_one_config('weaver_cuda-10.1.105-gnu-7.2.0-spmpi-rolling_release_static_Volta70_Power9_no-asan_complex_fpic_mpi_pt_no-rdc_no-uvm_deprecated-on_no-package-enables')

    def test_weaver_cuda_10_1_105_gnu_7_2_0_spmpi_rolling_release_static_Volta70_Power9_no_asan_complex_fpic_mpi_pt_no_rdc_uvm_deprecated_on_pr_framework_atdm(self):
        '''Check that the cuda 10.1.105 uvm=on job is set up with certain
        enabled packages for PR testing'''
        self.check_one_config('weaver_cuda-10.1.105-gnu-7.2.0-spmpi-rolling_release_static_Volta70_Power9_no-asan_complex_fpic_mpi_pt_no-rdc_uvm_deprecated-on_pr-framework-atdm')

    def test_weaver_cuda_10_1_105_gnu_7_2_0_spmpi_rolling_release_static_Volta70_Power9_no_asan_complex_fpic_mpi_pt_no_rdc_uvm_deprecated_on_no_package_enables(self):
        '''Check that the cuda 10.1.105 uvm=on job is set up without enabled packages for
           PR testing'''
        self.check_one_config('weaver_cuda-10.1.105-gnu-7.2.0-spmpi-rolling_release_static_Volta70_Power9_no-asan_complex_fpic_mpi_pt_no-rdc_uvm_deprecated-on_no-package-enables')

    def assert_weaver_test_disables_cuda(self, gc):
        '''stock test disables used in both cuda 10.1.105 builds'''
        self.assert_package_config_contains(
            gc, 'set(MueLu_ParameterListInterpreterTpetra_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(MueLu_ParameterListInterpreterTpetraHeavy_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(STKUnit_tests_stk_ngp_test_utest_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_PDE-OPT_0ld_adv-diff-react_example_01_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_PDE-OPT_0ld_adv-diff-react_example_02_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_PDE-OPT_0ld_poisson_example_01_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_PDE-OPT_0ld_stefan-boltzmann_example_03_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_PDE-OPT_navier-stokes_example_01_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_PDE-OPT_navier-stokes_example_02_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_PDE-OPT_nonlinear-elliptic_example_01_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_PDE-OPT_nonlinear-elliptic_example_02_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_PDE-OPT_obstacle_example_01_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_PDE-OPT_topo-opt_poisson_example_01_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_test_elementwise_TpetraMultiVector_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_NonlinearProblemTest_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(PanzerAdaptersSTK_CurlLaplacianExample-ConvTest-Quad-Order-4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(PanzerAdaptersSTK_MixedPoissonExample-ConvTest-Hex-Order-3_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(TrilinosCouplings_Example_Maxwell_MueLu_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(TrilinosCouplings_Example_Maxwell_MueLu_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(TrilinosCouplings_Example_Maxwell_MueLu_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')

        # Disable some tests that should not need to be disabled but do because the
        # Trilinos PR tester is using too high a parallel level for ctest. (If the
        # ctest parallel test level is dropped from 29 to 8, all of these will pass.)
        self.assert_package_config_contains(
            gc, 'set(MueLu_UnitTestsIntrepid2Tpetra_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(PanzerAdaptersSTK_main_driver_energy-ss-blocked-tp_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(PanzerAdaptersSTK_MixedCurlLaplacianExample-ConvTest-Tri-Order-1_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(PanzerAdaptersSTK_PoissonInterfaceExample_3d_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(PanzerMiniEM_MiniEM-BlockPrec_Augmentation_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(PanzerMiniEM_MiniEM-BlockPrec_RefMaxwell_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(ROL_example_PDE-OPT_poisson-boltzmann_example_01_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')

        # Disable a couple of unit tests in test KokkosCore_UnitTest_Cuda_MPI_1 that
        # are randomly failing in PR test iterations (#6799)
        self.assert_package_config_contains(
            gc, 'set(KokkosCore_UnitTest_Cuda_MPI_1_EXTRA_ARGS --gtest_filter=-cuda.debug_pin_um_to_host:cuda.debug_serial_execution CACHE STRING "from .ini configuration")')

        # Disable a few failing tests for initial release of Cuda 10.1.105 PR build
        self.assert_package_config_contains(
            gc, 'set(EpetraExt_inout_test_LL_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(EpetraExt_inout_test_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(Teko_testdriver_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(Zoltan2_fix4785_MPI_4_DISABLE ON CACHE BOOL "from .ini configuration")')
        self.assert_package_config_contains(
            gc, 'set(Intrepid2_unit-test_Discretization_Basis_HierarchicalBases_Hierarchical_Basis_Tests_MPI_1_DISABLE ON CACHE BOOL "from .ini configuration")')

if __name__ == '__main__':
    unittest.main()  # pragma nocover