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

    # @property
    # def supported_compilers(self):
    #     # Need a list of supported compilers for certain systems
    #     if self.system_name is None:
    #         self.parse_system_name()

    #     supported_compilers_list = {
    #         "ascic": [],
    #         # cuda can be in combination with either gnu or xl
    #         "machine-type-2": ["gnu-7.3.1", "cuda-10.1.243", "xl-2020.03.18"],
    #         "cafe": [],
    #         "chama": [],
    #         "cee-rhel6": ["clang-9.0.1", "gnu-7.2.0", "intel-19.0.3",
    #                       "cuda-10.1.243"],
    #         "machine-type-3": [],
    #         "machine-type-3empire": [],
    #         "eclipse": [],
    #         "sems-rhel7": [],
    #         "stria": [],
    #         "machine-type-5": [],
    #         "machine-type-4": [],
    #         "vortex": [],
    #     }
    #     return supported_compilers_list[self.system_name]

    def parse_system_name(self):
        valid_names = ["ascic", "machine-type-2", "cafe", "cee-rhel6", "chama", "machine-type-3",
                       "machine-type-3empire", "eclipse", "sems-rhel7", "stria", "machine-type-5",
                       "machine-type-4", "vortex"]
        valid_name_in_keyword_string = [name in self.keyword_string
                                        for name in valid_names]
        print(f"Keyword String: {self.keyword_string}")
        if not any(valid_name_in_keyword_string):
            raise Exception("No valid system name in the keyword string.")

        system_name = [name for name, in_keyword_string
                       in zip(valid_names, valid_name_in_keyword_string)
                       if in_keyword_string is True][0]
        return system_name

    def parse_compiler(self):
        # NOTE: Should "default" be included?
        valid_compilers = ["cuda", "clang", "gcc", "gnu", "intel", "xl"]
        compilers = re.findall(
            f"({'|'.join(f'{c}[^A-Z^a-z]*' for c in valid_compilers)})[_-]",
            self.keyword_string
        )
        if len(compilers) == 0:
            raise Exception("No valid compiler name in the keyword string.")

        return "-".join(compilers)

    def parse_kokkos_thread(self):
        valid_mpis = ["intelmpi", "mpich", "openmp", "spmpi-rolling", "spmpi"]
        kokkos_threads = re.findall(
            f"({'|'.join(f'{m}i?[^A-Z^a-z]*' for m in valid_mpis)})[_-]",
            self.keyword_string
        )
        if len(kokkos_threads) == 0:
            return "serial"
        if len(kokkos_threads) > 1:
            # Check if the same type is repeated
            for mpi in valid_mpis:
                if len([k for k in kokkos_threads if mpi in k]) == 1:
                    raise Exception("Can't specify more than one MPI type.")

        # if self.mpi_is_supported(kokkos_thread) is False:
        #     raise Exception(f"MPI {kokkos_thread} is not supported on "
        #                     f"{self.system_name}.")
        return kokkos_threads[0]

    # def mpi_is_supported(self, mpi):
    #     if self.system_name is None:
    #         self.parse_system_name()

    #     supported_mpi_list = {
    #         "ascic": [],
    #         "machine-type-2": ["spmpi-rolling", "spmpi_rolling"],
    #         "cafe": [],
    #         "cee-rhel6": [],
    #         "chama": [],
    #         "machine-type-3": [],
    #         "machine-type-3empire": [],
    #         "eclipse": [],
    #         "sems-rhel7": [],
    #         "stria": [],
    #         "machine-type-5": [],
    #         "machine-type-4": [],
    #         "vortex": [],
    #     }
    #     supported_mpis = supported_mpi_list[self.system_name]

    #     if self.system_name == "cee-rhel6":
    #         match = re.search(r"([A-Za-z])", self.compiler)
    #         compiler_base_name = match.groups(0)[0]

    #         supported_mpis = {
    #             "clang": ["openmpi-4.0.3"],
    #             "gnu": ["openmpi-4.0.3"],
    #             "intel": ["mpich2-3.2", "intelmpi-2018.4"],
    #             "cuda": ["openmpi-4.0.3"],
    #         }[compiler_base_name]

    #     return True if mpi in supported_mpis else False

    def parse_kokkos_arch(self):
        valid_kokkos_arch = ["BDW", "HSW", "Power8", "Power9", "KNL",
                             "Kepler37", "Pascal60", "Volta70"]
        valid_kokkos_arch_in_keyword_string = [ka in self.keyword_string
                                               for ka in valid_kokkos_arch]
        if not any(valid_kokkos_arch_in_keyword_string):
            return ""

        kokkos_arch = [name for name, in_keyword_string
                       in zip(valid_kokkos_arch,
                              valid_kokkos_arch_in_keyword_string)
                       if in_keyword_string is True][0]

        if (kokkos_arch in ["Kepler37", "Pascal60", "Volta70"]
                and "cuda" not in self.keyword_string):
            raise Exception(f"Cannot use {kokkos_arch} if 'cuda' is not "
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
