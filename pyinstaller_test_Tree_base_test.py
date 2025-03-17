import os
import pytest
from unittest.mock import patch, MagicMock
from pyinstaller.test_Tree import unique_name, TOC, Tree, normalize_toc, normalize_pyz_toc, toc_process_symbolic_links

# Test for unique_name function
def test_unique_name():
    entry = ('example', '/path/to/example', 'BINARY')
    assert unique_name(entry) == 'example'

    entry = ('Example', '/path/to/example', 'BINARY')
    assert unique_name(entry) == 'example'  # normcase should lower the case on windows

    entry = ('example', '/path/to/example', 'OTHER')
    assert unique_name(entry) == 'example'

# Tests for TOC class
def test_toc_append():
    toc = TOC()
    entry = ('example', '/path/to/example', 'BINARY')
    toc.append(entry)
    assert len(toc) == 1
    assert toc[0] == entry

    # Attempting to append a duplicate should not increase length
    toc.append(entry)
    assert len(toc) == 1

    # Test append with non-tuple raises TypeError
    with pytest.raises(TypeError):
        toc.append('not-a-tuple')

def test_toc_setitem():
    toc = TOC([('example', '/path/to/example', 'BINARY')])
    new_entry = ('new_example', '/path/to/new_example', 'BINARY')
    toc[0] = new_entry
    assert toc[0] == new_entry

    # Test setting slice raises KeyError
    with pytest.raises(KeyError):
        toc[:] = [('another_example', '/path/to/another_example', 'BINARY')]

def test_toc_addition():
    toc1 = TOC([('example1', '/path/to/example1', 'BINARY')])
    toc2 = TOC([('example2', '/path/to/example2', 'BINARY')])
    toc3 = toc1 + toc2
    assert len(toc3) == 2
    assert toc3[0] == ('example1', '/path/to/example1', 'BINARY')
    assert toc3[1] == ('example2', '/path/to/example2', 'BINARY')

# Tests for Tree class
def test_tree_assemble():
    with patch('os.listdir', return_value=['file1', 'file2']), \
         patch('os.path.isdir', return_value=False), \
         patch('os.path.isfile', return_value=True):
        tree = Tree(root='/mock/root', prefix='prefix', excludes=[], typecode='DATA')
        tree.assemble()
        assert len(tree) == 2
        assert tree[0] == ('prefix/file1', '/mock/root/file1', 'DATA')
        assert tree[1] == ('prefix/file2', '/mock/root/file2', 'DATA')

def test_tree_assemble_with_excludes():
    with patch('os.listdir', return_value=['file1', 'file2']), \
         patch('os.path.isdir', return_value=False), \
         patch('os.path.isfile', return_value=True):
        tree = Tree(root='/mock/root', prefix='prefix', excludes=['file2'], typecode='DATA')
        tree.assemble()
        assert len(tree) == 1
        assert tree[0] == ('prefix/file1', '/mock/root/file1', 'DATA')

# Test for normalize_toc function
def test_normalize_toc():
    toc = [
        ('module1', '/path/to/module1', 'PYMODULE'),
        ('module1', '/path/to/module1', 'DEPENDENCY'),
        ('module2', '/path/to/module2', 'DATA')
    ]
    normalized = normalize_toc(toc)
    assert len(normalized) == 2
    assert ('module1', '/path/to/module1', 'DEPENDENCY') in normalized
    assert ('module2', '/path/to/module2', 'DATA') in normalized

# Test for toc_process_symbolic_links function
def test_toc_process_symbolic_links():
    with patch('os.path.islink', side_effect=[True, False]), \
         patch('os.readlink', return_value='real_path'), \
         patch('os.path.realpath', return_value='/real/path'), \
         patch('os.path.normpath', side_effect=lambda x: x), \
         patch('os.path.isdir', return_value=False):
        toc = [
            ('link_name', 'link_path', 'BINARY'),
            ('real_name', '/real/path', 'BINARY')
        ]
        processed_toc = toc_process_symbolic_links(toc)
        assert len(processed_toc) == 2
        assert ('link_name', 'real_path', 'SYMLINK') in processed_toc

# Test for normalize_pyz_toc function
def test_normalize_pyz_toc():
    toc = [
        ('module1', '/path/to/module1', 'PYMODULE'),
        ('module1', '/path/to/module1', 'PYMODULE-2'),
        ('module2', '/path/to/module2', 'PYMODULE-1')
    ]
    normalized = normalize_pyz_toc(toc)
    assert len(normalized) == 2
    assert ('module1', '/path/to/module1', 'PYMODULE-2') in normalized
    assert ('module2', '/path/to/module2', 'PYMODULE-1') in normalized