import os
import pytest
import tempfile
from pyinstaller.compat import is_win
from pyinstaller.test_miscutils import (
    dlls_in_subdirs,
    dlls_in_dir,
    files_in_dir,
    get_path_to_toplevel_modules,
    mtime,
    save_py_data_struct,
    load_py_data_struct,
    absnormpath,
    module_parent_packages,
    is_file_qt_plugin,
    decode,
    is_iterable,
    path_to_parent_archive
)

@pytest.fixture
def temp_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def temp_file():
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        yield temp_file.name
    os.remove(temp_file.name)

def test_dlls_in_subdirs(temp_directory):
    subdir = os.path.join(temp_directory, 'subdir')
    os.makedirs(subdir)
    dll_file = os.path.join(subdir, 'test.dll')
    open(dll_file, 'w').close()
    assert dlls_in_subdirs(temp_directory) == [dll_file]

def test_dlls_in_dir(temp_directory):
    dll_file = os.path.join(temp_directory, 'test.dll')
    open(dll_file, 'w').close()
    assert dlls_in_dir(temp_directory) == [dll_file]

def test_files_in_dir(temp_directory):
    txt_file = os.path.join(temp_directory, 'test.txt')
    open(txt_file, 'w').close()
    assert files_in_dir(temp_directory, ["*.txt"]) == [txt_file]

def test_get_path_to_toplevel_modules(temp_file):
    init_file = os.path.join(os.path.dirname(temp_file), '__init__.py')
    open(init_file, 'w').close()
    assert get_path_to_toplevel_modules(temp_file) == os.path.dirname(os.path.dirname(temp_file))
    os.remove(init_file)

def test_mtime(temp_file):
    assert mtime(temp_file) == int(os.path.getmtime(temp_file))

def test_save_and_load_py_data_struct(temp_file):
    data = {'key': 'value'}
    save_py_data_struct(temp_file, data)
    assert load_py_data_struct(temp_file) == data

def test_absnormpath():
    path = 'folder/../file.txt'
    assert absnormpath(path) == os.path.abspath(os.path.normpath(path))

def test_module_parent_packages():
    assert module_parent_packages('aaa.bb.c.dddd') == ['aaa', 'aaa.bb', 'aaa.bb.c']

def test_is_file_qt_plugin(temp_file):
    with open(temp_file, 'wb') as f:
        f.write(b'QTMETADATA some content')
    assert is_file_qt_plugin(temp_file) is True

def test_decode():
    assert decode(b'# encoding: utf-8\ntext') == 'text'

def test_is_iterable():
    assert is_iterable([1, 2, 3]) is True
    assert is_iterable('string') is True
    assert is_iterable(123) is False

def test_path_to_parent_archive(temp_directory):
    archive_file = os.path.join(temp_directory, 'archive.zip')
    open(archive_file, 'w').close()
    file_in_archive = os.path.join(temp_directory, 'archive.zip', 'file.txt')
    assert path_to_parent_archive(file_in_archive) == pathlib.Path(archive_file)