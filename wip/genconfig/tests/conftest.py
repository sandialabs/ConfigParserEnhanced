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

    shutil.copyfile(Path.cwd()/("tests/supporting_files/"
                                "test-supported-config-flags.ini"),
                    tmpdir.join("test-supported-config-flags.ini"))
    monkeypatch.chdir(tmpdir)
