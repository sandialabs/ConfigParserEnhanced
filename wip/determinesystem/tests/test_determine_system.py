from pathlib import Path
import pytest
import re
import sys
from unittest.mock import patch

root_dir = (Path.cwd()/".."
            if (Path.cwd()/"conftest.py").exists()
            else Path.cwd())

sys.path.append(str(root_dir))
from determinesystem import DetermineSystem


@pytest.fixture
def supported_systems_file():
    return "test_supported_systems.ini"


###############################
#  System Name Determination  #
###############################
@pytest.mark.parametrize("data", [
    {"hostname": "machine-prefix-1", "sys_name": "machine-type-1"},
    {"hostname": "machine-prefix-2", "sys_name": "machine-type-2"},
    {"hostname": "machine-prefix-3", "sys_name": "machine-type-3"},
    {"hostname": "machine-prefix-4007", "sys_name": "rhel7"},
    {"hostname": "machine-prefix-5004", "sys_name": "rhel7"},
    {"hostname": "machine-prefix-5005", "sys_name": "rhel7"},
])
@patch("socket.gethostname")
def test_system_name_determination_correct_for_hostname(
    mock_gethostname, data, supported_systems_file
):
    mock_gethostname.return_value = data["hostname"]
    ds = DetermineSystem("build_name", supported_systems_file)
    assert ds.system_name == data["sys_name"]


@patch("socket.gethostname")
def test_sys_name_in_build_name_not_matching_hostname_raises(
    mock_gethostname, supported_systems_file
):
    mock_gethostname.return_value = "machine-prefix-6"
    ds = DetermineSystem("machine-type-1_build-name", supported_systems_file)
    with pytest.raises(SystemExit) as excinfo:
        ds.system_name
    exc_msg = excinfo.value.args[0]
    for msg in ["Hostname 'machine-prefix-6' matched to system 'machine-type-4'",
                "but you specified 'machine-type-1' in the build name",
                "add the --force flag"]:
        msg = msg.replace(" ", r"\s+\|?\s*")  # account for line breaks
        assert re.search(msg, exc_msg) is not None


@patch("socket.gethostname")
def tests_sys_name_in_build_name_overrides_hostname_match_when_forced(
    mock_gethostname, supported_systems_file
):
    mock_gethostname.return_value = "machine-prefix-6"
    ds = DetermineSystem("machine-type-1_build-name", supported_systems_file,
                         force_build_name=True)
    assert ds.system_name == "machine-type-1"


@pytest.mark.parametrize("hostname", ["machine-prefix-6", "unsupported_hostname"])
@patch("socket.gethostname")
def test_multiple_sys_names_in_build_name_raises_regardless_of_hostname_match(
    mock_gethostname, hostname, supported_systems_file
):
    mock_gethostname.return_value = hostname
    ds = DetermineSystem("machine-type-1_rhel7_build-name", supported_systems_file)
    with pytest.raises(SystemExit) as excinfo:
        ds.system_name
    exc_msg = excinfo.value.args[0]
    assert ("Cannot specify more than one system name in the build name"
            in exc_msg)
    assert "- machine-type-1" in exc_msg
    assert "- rhel7" in exc_msg


@pytest.mark.parametrize("data", [
    {"build_name": "no-system-here", "sys_name": None, "raises": True, hostname: "unsupported_hostname"},
    {"build_name": "any-host_build-name", "sys_name": "any-host", "raises": False, hostname: "machine-prefix-1"},
])
@patch("socket.gethostname")
def test_unsupported_hostname_handled_correctly(mock_gethostname, data,
                                                supported_systems_file):
    mock_gethostname.return_value = data["hostname"]
    ds = DetermineSystem(data["build_name"], supported_systems_file)
    if data["raises"]:
        with pytest.raises(SystemExit) as excinfo:
            ds.system_name
        exc_msg = excinfo.value.args[0]
        msg = ("Unable to find valid system name in the build name or for "
               "the hostname 'unsupported_hostname'")
        msg = msg.replace(" ", r"\s+\|?\s*")  # account for line breaks
        assert re.search(msg, exc_msg) is not None
        assert str(ds.supported_systems_file) in exc_msg
    else:
        assert ds.system_name == data["sys_name"]
