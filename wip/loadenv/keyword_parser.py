import re


class KeywordParser:

    def __init__(self, keyword_string):
        self.keyword_string = keyword_string

        self.system_name = self.parse_system_name()
        self.compiler = self.parse_compiler()
        self.kokkos_thread = self.parse_kokkos_thread()
        self.kokkos_arch = self.parse_kokkos_arch()
        self.complex = self.parse_complex()
        self.shared_static = self.parse_shared_static()
        self.release_debug = self.parse_release_debug()

    def parse_system_name(self):
        valid_sys_names = ["ascic", "machine-type-2", "cafe", "cee-rhel6", "chama",
                           "machine-type-3", "machine-type-3empire", "eclipse", "sems-rhel7",
                           "stria", "machine-type-5", "machine-type-4", "vortex"]
        matched_sys_names = re.findall(f"({'|'.join(valid_sys_names)})",
                                       self.keyword_string)
        if len(matched_sys_names) == 0:
            raise Exception("No valid system name in the keyword string.")
        elif len(matched_sys_names) > 1:
            raise Exception("Can't specify more than one system name "
                            f"(you specified {matched_sys_names}).")

        # Some names are nicknames
        system_name = matched_sys_names[0]
        if system_name in ["ascic", "cafe", "chama", "eclipse", "stria",
                           "vortex"]:
            system_name - {
                "ascic": "sems-rhel7",
                "cafe": "sems-rhel7",
                "chama": "machine-type-5",
                "eclipse": "machine-type-3",
                "stria": "machine-type-4",
                "vortex": "machine-type-2",
            }[system_name]

        return matched_sys_names[0]

    def parse_compiler(self):
        # NOTE: Should "default" be included?
        valid_compilers = ["arm", "cuda", "clang", "gcc", "gnu", "intel", "xl"]

        # Find compilers with version numbers in the keyword string
        regex_list = [f"{c}[^A-Z^a-z]*" for c in valid_compilers]
        matched_compilers = re.findall(f"({'|'.join(regex_list)})[_-]",
                                       self.keyword_string)
        if len(matched_compilers) == 0:
            raise Exception("No valid compiler found in the keyword string.")
        if len(matched_compilers) > 1:
            if "cuda" not in "-".join(matched_compilers):
                raise Exception("Can't specify more than one CPU compiler.")

        return "-".join(matched_compilers)

    def parse_kokkos_thread(self):
        valid_kokkos_threads = ["intelmpi", "mpich", "openmp", "spmpi-rolling",
                                "spmpi"]

        # Find kokkos_threads with version numbers in the keyword string
        regex_list = [f'{vkt}i?[^A-Z^a-z]*' for vkt in valid_kokkos_threads]
        matched_kokkos_threads = re.findall(f"({'|'.join(regex_list)})[_-]",
                                            self.keyword_string)
        if len(matched_kokkos_threads) == 0:
            return "serial"
        if len(matched_kokkos_threads) > 1:
            # Check if the same type is repeated
            for vkt in valid_kokkos_threads:
                if len([k for k in matched_kokkos_threads if vkt in k]) == 1:
                    raise Exception("Can't specify more than one MPI type.")

        # if self.mpi_is_supported(kokkos_thread) is False:
        #     raise Exception(f"MPI {kokkos_thread} is not supported on "
        #                     f"{self.system_name}.")
        return matched_kokkos_threads[0]

    def parse_kokkos_arch(self):
        valid_kokkos_archs = ["BDW", "HSW", "Power8", "Power9", "KNL",
                              "Kepler37", "Pascal60", "Volta70"]
        matched_kokkos_archs = re.findall(f"({'|'.join(valid_kokkos_archs)})",
                                          self.keyword_string)
        if len(matched_kokkos_archs) == 0:
            return ""
        if len(matched_kokkos_archs) > 1:
            raise Exception("Can't specify more than one kokkos_arch "
                            f"(you specified {matched_kokkos_archs}).")

        kokkos_arch = matched_kokkos_archs[0]
        if (kokkos_arch in ["Kepler37", "Pascal60", "Volta70"]
                and "cuda" not in self.keyword_string):
            raise Exception(f"Can't use {kokkos_arch} if 'cuda' is not "
                            "specified as compiler.")
        # Should also check if the host node supports the selected kokkos_arch

        return kokkos_arch

    def parse_complex(self):
        complex_ = ("complex"
                    if "complex" in self.keyword_string
                    else "no-complex")
        return complex_

    def parse_shared_static(self):
        shared_static = ("shared"
                         if "shared" in self.keyword_string
                         else "static")
        return shared_static

    def parse_release_debug(self):
        if ("release-debug" in self.keyword_string
                or "opt-dbg" in self.keyword_string):
            release_debug = "release-debug"
        elif "release" in self.keyword_string or "opt" in self.keyword_string:
            release_debug = "release"
        else:
            release_debug = "debug"

        return release_debug
