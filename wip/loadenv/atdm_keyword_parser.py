import re


class AtdmKeywordParser:

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
        valid_names = ["ascic", "machine-type-2", "cafe", "chama", "machine-type-3", "machine-type-3empire",
                       "eclipse", "sems-rhel7", "stria", "machine-type-5", "van1",
                       "vortex"]
        valid_name_in_keyword_string = [name in self.keyword_string
                                        for name in valid_names]
        if not any(valid_name_in_keyword_string):
            raise Exception("No valid system name in the keyword string.")

        system_name = [name for name, in_keyword_string
                       in zip(valid_names, valid_name_in_keyword_string)
                       if in_keyword_string is True][0]
        return system_name

    def parse_compiler(self):
        # NOTE: Should "default" be included?
        valid_compilers = ["clang", "cuda", "gnu", "intel"]
        valid_compiler_in_keyword_string = [c in self.keyword_string
                                            for c in valid_compilers]
        if not any(valid_compiler_in_keyword_string):
            raise Exception("No valid compiler name in the keyword string.")

        base = [name for name, in_keyword_string
                in zip(valid_compilers, valid_compiler_in_keyword_string)
                if in_keyword_string is True][0]

        match = re.search(f"({base}[^A-Z^a-z]*)[_-][A-Za-z]",
                          self.keyword_string)
        compiler = match.groups(0)[0]
        return compiler

    def parse_kokkos_thread(self):
        if "openmp" not in self.keyword_string:
            return "serial"

        match = re.search(r"(openmpi?[^A-Z^a-z]*)[_-][A-Za-z]",
                          self.keyword_string)
        kokkos_thread = match.groups(0)[0]
        return kokkos_thread

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
