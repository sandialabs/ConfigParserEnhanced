from pathlib import Path
import pytest
import sys

root_dir = (Path.cwd()/".."
            if (Path.cwd()/"conftest.py").exists()
            else Path.cwd())
sys.path.append(str(root_dir))
from src.config_keyword_parser import ConfigKeywordParser


#####################
#  Keyword Parsing  #
#####################
@pytest.mark.parametrize("keyword", [
    {
        "str": "machine-type-5_intel-19.0.4_mpich-7.7.15_hsw_openmp_static_dbg",
        "system_name": "machine-type-5",
    },
    {
        "str": "intel-hsw",
        "system_name": "machine-type-5",
    },
    {
        "str": "machine-type-3-arm-20.1",
        "system_name": "machine-type-3",
    },
    {
        "str": "arm-serial",
        "system_name": "machine-type-3",
    },
])
def test_keyword_parser_matches_correctly(keyword):
    ckp = ConfigKeywordParser(keyword["str"], keyword["system_name"],
                              "test_supported_envs.ini")
