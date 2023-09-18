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
                                "test-config-specs.ini"),
                    tmpdir.join("test-config-specs.ini"))
    shutil.copyfile(Path.cwd()/("tests/supporting_files/"
                                "test-supported-config-flags.ini"),
                    tmpdir.join("test-supported-config-flags.ini"))
    shutil.copyfile(Path.cwd()/("tests/supporting_files/"
                                "test-supported-systems.ini"),
                    tmpdir.join("test-supported-systems.ini"))
    shutil.copyfile(Path.cwd()/("tests/supporting_files/"
                                "test-supported-envs.ini"),
                    tmpdir.join("test-supported-envs.ini"))
    shutil.copyfile(Path.cwd()/("tests/supporting_files/"
                                "test-environment-specs.ini"),
                    tmpdir.join("test-environment-specs.ini"))
    monkeypatch.chdir(tmpdir)
