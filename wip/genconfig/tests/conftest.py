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

    # Test ini files
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
    
    # Trilinos ini files
    shutil.copyfile(Path.cwd() / ("examples/trilinos/"
                                  "config-specs.ini"),
                    tmpdir.join("test-trilinos-config-specs.ini"))
    shutil.copyfile(Path.cwd() / ("examples/trilinos/"
                                  "supported-config-flags.ini"),
                    tmpdir.join("test-trilinos-supported-config-flags.ini"))
    shutil.copyfile(Path.cwd() / ("deps/LoadEnv/examples/trilinos/"
                                  "supported-systems.ini"),
                    tmpdir.join("test-trilinos-supported-systems.ini"))
    shutil.copyfile(Path.cwd() / ("deps/LoadEnv/examples/trilinos/"
                                  "supported-envs.ini"),
                    tmpdir.join("test-trilinos-supported-envs.ini"))
    shutil.copyfile(Path.cwd() / ("deps/LoadEnv/examples/trilinos/"
                                  "environment-specs.ini"),
                    tmpdir.join("test-trilinos-environment-specs.ini"))
    
    # TODO: ATDM ini files
    monkeypatch.chdir(tmpdir)