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
    shutil.copyfile(Path.cwd()/("tests/supporting_files/ini_files/"
                                "config-specs.ini"),
                    tmpdir.join("config-specs.ini"))
    shutil.copyfile(Path.cwd()/("tests/supporting_files/ini_files/"
                                "supported-config-flags.ini"),
                    tmpdir.join("supported-config-flags.ini"))
    shutil.copyfile(Path.cwd()/("tests/supporting_files/ini_files/"
                                "supported-systems.ini"),
                    tmpdir.join("supported-systems.ini"))
    shutil.copyfile(Path.cwd()/("tests/supporting_files/ini_files/"
                                "environment-specs.ini"),
                    tmpdir.join("environment-specs.ini"))
    shutil.copyfile(Path.cwd()/("tests/supporting_files/ini_files/"
                                "config-specs.ini"),
                    tmpdir.join("config-specs.ini"))
    shutil.copyfile(Path.cwd()/("tests/supporting_files/ini_files/"
                                "supported-envs.ini"),
                    tmpdir.join("supported-envs.ini"))
    shutil.copyfile(Path.cwd()/("tests/supporting_files/"
                                "gen-config.ini"),
                    tmpdir.join("gen-config.ini"))

    monkeypatch.chdir(tmpdir)
