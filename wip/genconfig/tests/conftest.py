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
    shutil.copyfile(Path.cwd() / ("tests/supporting_files/"
                                  "test-config-specs-1-new-system-1-section.ini"),
                    tmpdir.join("test-config-specs-1-new-system-1-section.ini"))
    shutil.copyfile(Path.cwd() / ("tests/supporting_files/"
                                  "test-config-specs-1-new-system-2-section.ini"),
                    tmpdir.join("test-config-specs-1-new-system-2-section.ini"))
    shutil.copyfile(Path.cwd() / ("tests/supporting_files/"
                                  "test-config-specs-2-new-system-3-section.ini"),
                    tmpdir.join("test-config-specs-2-new-system-3-section.ini"))
    shutil.copyfile(Path.cwd() / ("tests/supporting_files/"
                                  "test-supported-config-flags-invalid-option-in-build-name-raises.ini"),
                    tmpdir.join("test-supported-config-flags-invalid-option-in-build-name-raises.ini"))
    shutil.copyfile(Path.cwd() / ("tests/supporting_files/"
                                  "test-config-specs-invalid-option-in-build-name-raises.ini"),
                    tmpdir.join("test-config-specs-invalid-option-in-build-name-raises.ini"))
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
    shutil.copyfile(Path.cwd() / ("ini_files/trilinos/"
                                  "config-specs.ini"),
                    tmpdir.join("test-trilinos-config-specs.ini"))
    shutil.copyfile(Path.cwd() / ("ini_files/trilinos/"
                                  "supported-config-flags.ini"),
                    tmpdir.join("test-trilinos-supported-config-flags.ini"))
    shutil.copyfile(Path.cwd() / ("deps/LoadEnv/ini_files/trilinos/"
                                  "supported-envs.ini"),
                    tmpdir.join("test-trilinos-supported-envs.ini"))
    if Path.is_dir(Path("deps/LoadEnv/ini_files/srn-ini-files")):
        shutil.copyfile(Path.cwd() / ("deps/LoadEnv/ini_files/srn-ini-files/trilinos/framework/"
                                      "supported-systems.ini"),
                        tmpdir.join("test-trilinos-supported-systems.ini"))
        shutil.copyfile(Path.cwd() / ("deps/LoadEnv/ini_files/srn-ini-files/trilinos/framework/"
                                      "environment-specs.ini"),
                        tmpdir.join("test-trilinos-environment-specs.ini"))
    else:
        shutil.copyfile(Path.cwd() / ("deps/LoadEnv/ini_files/trilinos/"
                                      "supported-systems.ini"),
                        tmpdir.join("test-trilinos-supported-systems.ini"))
        shutil.copyfile(Path.cwd() / ("deps/LoadEnv/ini_files/trilinos/"
                                      "environment-specs.ini"),
                        tmpdir.join("test-trilinos-environment-specs.ini"))

    # TODO: ATDM ini files
    monkeypatch.chdir(tmpdir)
