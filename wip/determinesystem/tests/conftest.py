from pathlib import Path
import pytest
import shutil


@pytest.fixture(autouse=True)
def use_tmpdir(monkeypatch, request, tmpdir):
    """
    **@pytest.fixture(autouse=True)**

    Automatically use a temporary directory as the current working directory in
    these tests.
    """

    root_dir = (Path.cwd()/".."
                if (Path.cwd()/"conftest.py").exists()
                else Path.cwd())

    shutil.copyfile(root_dir/("tests/test_supported_systems.ini"),
                    tmpdir.join("test_supported_systems.ini"))
    monkeypatch.chdir(tmpdir)
