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

    if (Path.cwd() / "conftest.py").exists():
        root_dir = (Path.cwd()/"../..").resolve()
    elif (Path.cwd() / "unittests/conftest.py").exists():
        root_dir = (Path.cwd()/"..").resolve()
    else:
        root_dir = Path.cwd()

    shutil.copyfile(
        root_dir / ("loadenv/unittests/supporting_files/test_supported_systems.ini"),
        tmpdir.join("test_supported_systems.ini")
    )

    shutil.copyfile(
        root_dir / ("loadenv/unittests/supporting_files/test_supported_envs.ini"),
        tmpdir.join("test_supported_envs.ini")
    )

    shutil.copyfile(
        root_dir / ("loadenv/unittests/supporting_files/test_environment_specs.ini"),
        tmpdir.join("test_environment_specs.ini")
    )

    shutil.copyfile(
        root_dir / ("loadenv/unittests/supporting_files/test_load_env.ini"),
        tmpdir.join("test_load_env.ini")
    )

    monkeypatch.chdir(tmpdir)
