import os
import platform
import subprocess
import sys
import sysconfig
import pytest
from unittest.mock import patch, Mock
from PyInstaller._shared_with_waf import _pyi_machine
from PyInstaller.compat import (
    getenv,
    setenv,
    unsetenv,
    exec_command,
    exec_command_rc,
    exec_command_all,
    exec_python,
    exec_python_rc,
    getsitepackages,
    importlib_load_source,
    check_requirements,
    is_wine_dll,
    PYDYLIB_NAMES
)
from PyInstaller.exceptions import ExecCommandFailed, ImportlibMetadataError, PythonLibraryNotFoundError

# Mocking some constants for test purposes
pytestmark = pytest.mark.skipif(
    sys.platform.startswith('win'), reason="These tests are not applicable on Windows."
)


def test_getenv():
    os.environ['TEST_ENV_VAR'] = 'test_value'
    assert getenv('TEST_ENV_VAR') == 'test_value'
    assert getenv('NON_EXISTENT_VAR', 'default') == 'default'


def test_setenv():
    setenv('TEST_ENV_VAR', 'new_value')
    assert os.environ['TEST_ENV_VAR'] == 'new_value'


def test_unsetenv():
    os.environ['TEST_ENV_VAR'] = 'value_to_remove'
    unsetenv('TEST_ENV_VAR')
    assert 'TEST_ENV_VAR' not in os.environ


def test_exec_command():
    result = exec_command('echo', 'hello', encoding='utf-8')
    assert 'hello' in result


def test_exec_command_enoent():
    with pytest.raises(ExecCommandFailed):
        exec_command('non_existent_command', raise_enoent=True)


def test_exec_command_rc():
    result = exec_command_rc('echo', 'hello')
    assert result == 0


def test_exec_command_all():
    rc, out, err = exec_command_all('echo', 'hello', encoding='utf-8')
    assert rc == 0
    assert 'hello' in out
    assert err == ''


def test_exec_python():
    result = exec_python('-c', 'print("hello")')
    assert 'hello' in result


def test_exec_python_rc():
    result = exec_python_rc('-c', 'print("hello")')
    assert result == 0


def test_getsitepackages():
    site_packages = getsitepackages()
    assert isinstance(site_packages, list)
    assert all(isinstance(path, str) for path in site_packages)


def test_importlib_load_source(tmp_path):
    sample_code = "x = 42"
    module_path = tmp_path / "sample_module.py"
    module_path.write_text(sample_code)

    module = importlib_load_source('sample_module', str(module_path))
    assert module.x == 42


def test_check_requirements():
    # Assuming the test environment meets the requirements
    check_requirements()


def test_is_wine_dll():
    # This test is environment-specific, we mock it instead
    with patch('builtins.open', Mock(side_effect=FileNotFoundError)):
        assert not is_wine_dll('non_existent_file.dll')


def test_pyi_machine():
    assert _pyi_machine('x86_64', 'Linux') == 'intel'
    assert _pyi_machine('armv7l', 'Linux') == 'arm'
    assert _pyi_machine('arm64', 'Windows') == 'arm'


def test_python_library_not_found_error():
    with pytest.raises(PythonLibraryNotFoundError) as excinfo:
        raise PythonLibraryNotFoundError()
    assert "Python library not found" in str(excinfo.value)


def test_importlib_metadata_error():
    with pytest.raises(ImportlibMetadataError) as excinfo:
        raise ImportlibMetadataError()
    assert "PyInstaller requires importlib.metadata" in str(excinfo.value)