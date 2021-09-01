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

from gen_config import GenConfig

from configparserenhanced import ConfigParserEnhanced


class Test_verify_rhel7_configs(unittest.TestCase):
    '''Class to iterate through all configs and verify that the loaded
       environment and cmake configure is what we expect'''

    def setUp(self):
        '''Comman data structures for all tests - done on a per-test basis'''
        self.config_verification_map = \
             {'rhel7_sems-gnu-7.2.0-anaconda3-serial_debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_no-mpi_no-pt_no-rdc_pr-framework':
              [
               [self.assert_gcc_version, 7, 2, 0],
               [self.assert_python_version, 3, 7, 3],
               [self.assert_kokkos_nodetype, "serial"],
               [self.assert_build_type, "debug"],
               #[self.assert_lib_type, "shared"],
               [self.assert_kokkos_arch, "no-kokkos-arch"],
               [self.assert_use_asan, False],
               [self.assert_use_complex, False],
               [self.assert_use_fpic, False],
               [self.assert_use_mpi, False],
               [self.assert_use_pt, False],
               [self.assert_use_rdc, False],
               [self.assert_package_config_contains, 'set(Trilinos_ENABLE_TrilinosFrameworkTests ON CACHE BOOL \"from .ini configuration\")'],
              ],
              'rhel7_sems-gnu-7.2.0-openmpi-1.10.1-serial_debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_pr': [],
              'rhel7_sems-gnu-7.2.0-serial_release-debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_no-mpi_no-pt_no-rdc_pr-serial': [],
              'rhel7_sems-gnu-7.2.0-openmpi-1.10.1-serial_release-debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_pr': [],
              'rhel7_sems-gnu-7.2.0-openmpi-1.10.1-serial_release-debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-package-enables':
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
               [self.assert_package_config_contains, 'set(MPI_EXEC_PRE_NUMPROCS_FLAGS --bind-to;none CACHE STRING \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(Tpetra_INST_SERIAL ON CACHE BOOL \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(Trilinos_ENABLE_COMPLEX_DOUBLE ON CACHE BOOL \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(Teko_DISABLE_LSCSTABALIZED_TPETRA_ALPAH_INV_D ON CACHE BOOL \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(CMAKE_CXX_FLAGS "-Wall -Wno-clobbered -Wno-vla -Wno-pragmas -Wno-unknown-pragmas -Wno-unused-local-typedefs -Wno-literal-suffix -Wno-deprecated-declarations -Wno-misleading-indentation -Wno-int-in-bool-context -Wno-maybe-uninitialized -Wno-nonnull-compare -Wno-address -Wno-inline -Werror -DTRILINOS_HIDE_DEPRECATED_HEADER_WARNINGS" CACHE STRING "from .ini configuration")'],
              ],
              'rhel7_sems-gnu-8.3.0-openmpi-1.10.1-openmp_release-debug_static_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_pr': [],
              'rhel7_sems-gnu-8.3.0-openmpi-1.10.1-openmp_release-debug_static_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-package-enables':
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
               [self.assert_package_config_contains, 'set(MPI_EXEC_PRE_NUMPROCS_FLAGS --bind-to;none CACHE STRING \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(Trilinos_ENABLE_COMPLEX_DOUBLE ON CACHE BOOL \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(CMAKE_CXX_EXTENSIONS OFF CACHE BOOL \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(Teko_DISABLE_LSCSTABALIZED_TPETRA_ALPAH_INV_D ON CACHE BOOL \"from .ini configuration\")'],
               [self.assert_package_config_contains, 'set(CMAKE_CXX_FLAGS "-fno-strict-aliasing -Wall -Wno-clobbered -Wno-vla -Wno-pragmas -Wno-unknown-pragmas -Wno-parentheses -Wno-unused-local-typedefs -Wno-literal-suffix -Wno-deprecated-declarations -Wno-misleading-indentation -Wno-int-in-bool-context -Wno-maybe-uninitialized -Wno-class-memaccess -Wno-inline -Wno-nonnull-compare -Wno-address -Werror -DTRILINOS_HIDE_DEPRECATED_HEADER_WARNINGS" CACHE STRING "from .ini configuration")'],
              ],
              'rhel7_sems-clang-7.0.1-openmpi-1.10.1-serial_release-debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_pr': [],
              'rhel7_sems-clang-9.0.0-openmpi-1.10.1-serial_release-debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_pr': [],
              'rhel7_sems-clang-10.0.0-openmpi-1.10.1-serial_release-debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_pr': [],
              'rhel7_sems-intel-17.0.1-mpich-3.2-serial_release-debug_static_no-kokkos-arch_no-asan_no-complex_fpic_mpi_no-pt_no-rdc_pr': [],
              'rhel7_sems-intel-19.0.5-mpich-3.2-serial_release-debug_static_no-kokkos-arch_no-asan_no-complex_fpic_mpi_no-pt_no-rdc_pr': [],
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


    def test_rhel7_sems_gnu_7_2_0_anaconda3_serial_debug_shared_no_kokkos_arch_no_asan_no_complex_no_fpic_no_mpi_no_pt_no_rdc_pr_framework(self):
        '''Check that the job setup for our python testing matches
           expectations'''
        self.check_one_config('rhel7_sems-gnu-7.2.0-anaconda3-serial_debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_no-mpi_no-pt_no-rdc_pr-framework')

    def test_rhel7_sems_gnu_7_2_0_openmpi_1_10_1_serial_release_debug_shared_no_kokkos_arch_no_asan_no_complex_no_fpic_mpi_no_pt_no_rdc_no_package_enables(self):
        '''Check that the gnu 7.2 job is set up without enabled packages for
           PR testing'''
        self.check_one_config('rhel7_sems-gnu-7.2.0-openmpi-1.10.1-serial_release-debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-package-enables')

    def test_rhel7_sems_gnu_8_3_0_openmpi_1_10_1_openmp_release_debug_static_no_kokkos_arch_no_asan_no_complex_no_fpic_mpi_no_pt_no_rdc_no_package_enables(self):
        '''Check that the gnu 8.3 job is set up without enabled packages for
           PR testing'''
        self.check_one_config('rhel7_sems-gnu-8.3.0-openmpi-1.10.1-openmp_release-debug_static_no-kokkos-arch_no-asan_no-complex_no-fpic_mpi_no-pt_no-rdc_no-package-enables')

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
            self.assertTrue(check_string not in opt)

    def assert_gcc_version(self, gc, major, minor, micro):
        '''Run gcc --version and check for exact match only'''
        version = subprocess.check_output('g++ --version',
                                          stderr=subprocess.STDOUT,
                                          shell=True)
        m = re.search(b"g\\+\\+ \\(GCC\\) ([0-9]).([0-9]).([0-9]{0,1}).*", version)
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
            self.assert_package_config_contains(gc,
                                                'set(Kokkos_ENABLE_DEBUG_BOUNDS_CHECK ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Kokkos_ENABLE_DEBUG ON CACHE BOOL \"from .ini configuration\")')
        elif 'debug' == build_type:
            self.assert_package_config_contains(gc,
                                                'set(CMAKE_BUILD_TYPE DEBUG CACHE STRING \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Trilinos_ENABLE_DEBUG ON CACHE BOOL \"from .ini configuration\")')
            self.assert_package_config_contains(gc,
                                                'set(Kokkos_ENABLE_DEBUG_BOUNDS_CHECK ON CACHE BOOL \"from .ini configuration\")')
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
                                                'set(Kokkos_ARCH_{$kokkos_arch} ON CACHE BOOL \"from .ini configuration\")')

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


if __name__ == '__main__':
    unittest.main()  # pragma nocover
