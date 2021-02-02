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

    shutil.copyfile(Path.cwd()/"tests/test_supported_envs.ini",
                    tmpdir.join("test_supported_envs.ini"))
    monkeypatch.chdir(tmpdir)
