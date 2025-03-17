import os
import pytest
from unittest.mock import patch, mock_open
from pyinstaller.building.utils import (
    _check_guts_eq,
    _check_guts_toc_mtime,
    _check_guts_toc,
    add_suffix_to_extension,
    process_collected_binary,
    _compute_file_digest,
    _check_path_overlap,
    _make_clean_directory,
    format_binaries_and_datas,
    get_code_object,
    strip_paths_in_code,
    _should_include_system_binary,
    compile_pymodule,
    postprocess_binaries_toc_pywin32,
    postprocess_binaries_toc_pywin32_anaconda,
    create_base_library_zip,
)
from pyinstaller.config import CONF
from pyinstaller.exceptions import InvalidSrcDestTupleError
from pyinstaller.compat import is_darwin, is_win

@pytest.mark.parametrize("old_value, new_value, expected", [
    (1, 2, True),
    (2, 2, False),
    ("abc", "def", True),
    ("abc", "abc", False),
])
def test_check_guts_eq(old_value, new_value, expected):
    assert _check_guts_eq("test_attr", old_value, new_value, None) == expected

@pytest.mark.parametrize("old_toc, new_toc, last_build, expected", [
    ([("dest", "src", "type")], [("dest", "src", "type")], 0, True),
    ([("dest", "src", "type")], [("dest", "src", "type")], 100, False),
])
def test_check_guts_toc_mtime(old_toc, new_toc, last_build, expected):
    with patch("pyinstaller.utils.misc.mtime", return_value=50):
        assert _check_guts_toc_mtime("test_attr", old_toc, new_toc, last_build) == expected

@pytest.mark.parametrize("old_toc, new_toc, last_build, expected", [
    ([("dest", "src", "type")], [("dest", "src", "type")], 0, True),
    ([("dest", "src", "type")], [("dest", "src", "type")], 100, False),
])
def test_check_guts_toc(old_toc, new_toc, last_build, expected):
    with patch("pyinstaller.utils.misc.mtime", return_value=50):
        assert _check_guts_toc("test_attr", old_toc, new_toc, last_build) == expected

@pytest.mark.parametrize("dest_name, src_name, typecode, expected", [
    ("module.so", "module.so", "EXTENSION", ("module.so", "module.so", "EXTENSION")),
    ("module", "module.cpython-38-x86_64-linux-gnu.so", "EXTENSION", 
     ("module.cpython-38-x86_64-linux-gnu.so", "module.cpython-38-x86_64-linux-gnu.so", "EXTENSION")),
    ("module", "module.cpython-38-x86_64-linux-gnu.so", "OTHER", 
     ("module", "module.cpython-38-x86_64-linux-gnu.so", "OTHER")),
])
def test_add_suffix_to_extension(dest_name, src_name, typecode, expected):
    assert add_suffix_to_extension(dest_name, src_name, typecode) == expected

def test_process_collected_binary_no_processing():
    assert process_collected_binary("src", "dest") == "src"

def test_process_collected_binary_with_upx_exclude():
    with patch("pyinstaller.building.utils.pathlib.PurePath.match", return_value=True):
        assert process_collected_binary("src", "dest", use_upx=True, upx_exclude=["pattern"]) == "src"

def test_check_path_overlap_no_overlap():
    with patch.dict(CONF, {"workpath": "/not/overlap", "specpath": "/not/overlap"}):
        assert _check_path_overlap("/path")

def test_check_path_overlap_overlap():
    with patch.dict(CONF, {"workpath": "/path/overlap", "specpath": "/path/overlap"}):
        with pytest.raises(SystemExit):
            _check_path_overlap("/path")

def test_make_clean_directory():
    with patch("pyinstaller.building.utils._check_path_overlap", return_value=True):
        with patch("os.makedirs") as makedirs_mock:
            _make_clean_directory("/path")
            makedirs_mock.assert_called_once_with("/path", exist_ok=True)

@pytest.mark.parametrize("binaries_or_datas, workingdir, expected", [
    ([("src", "dest")], None, {("dest/src", "src")}),
    ([("src", "dest")], "/workingdir", {("/workingdir/dest/src", "/workingdir/src")}),
])
def test_format_binaries_and_datas(binaries_or_datas, workingdir, expected):
    assert format_binaries_and_datas(binaries_or_datas, workingdir) == expected

def test_format_binaries_and_datas_invalid():
    with pytest.raises(InvalidSrcDestTupleError):
        format_binaries_and_datas([("", "dest")])

def test_get_code_object():
    co = get_code_object("test", "-", 0)
    assert co is not None

def test_strip_paths_in_code():
    co = get_code_object("test", "-", 0)
    new_co = strip_paths_in_code(co)
    assert new_co.co_filename == "test"

@pytest.mark.parametrize("binary_tuple, exceptions, expected", [
    (("lib-dynload/test.so", "test"), [], True),
    (("lib/test.so", "test"), [], False),
    (("lib/test.so", "python"), [], True),
    (("lib/test.so", "test"), ["lib/test.so"], True),
])
def test_should_include_system_binary(binary_tuple, exceptions, expected):
    assert _should_include_system_binary(binary_tuple, exceptions) == expected

def test_compile_pymodule():
    with patch("pyinstaller.building.utils.compile", return_value=mock_open(read_data=b"")):
        assert compile_pymodule("test", "test.py", "/workpath", 0) == "/workpath/test.pyc"

def test_postprocess_binaries_toc_pywin32():
    binaries = [("test.dll", "/path/win32/test.dll", "EXTENSION")]
    expected = [("win32/test.dll", "/path/win32/test.dll", "EXTENSION")]
    assert postprocess_binaries_toc_pywin32(binaries) == expected

def test_postprocess_binaries_toc_pywin32_anaconda():
    binaries = [("test.dll", "/path/pywin32_system32/test.dll", "EXTENSION")]
    expected = [("pywin32_system32/test.dll", "/path/pywin32_system32/test.dll", "EXTENSION")]
    assert postprocess_binaries_toc_pywin32_anaconda(binaries) == expected

def test_create_base_library_zip():
    with patch("pyinstaller.building.utils.zipfile.ZipFile") as zipfile_mock:
        create_base_library_zip("test.zip", [])
        zipfile_mock.assert_called_once_with("test.zip", 'w')