import os
import pytest
import warnings
from pyinstaller.test_TOC.test_TOC import TOC, Tree, unique_name, normalize_toc, normalize_pyz_toc, toc_process_symbolic_links

def test_unique_name():
    entry = ('name', 'path', 'BINARY')
    assert unique_name(entry) == 'name'

    entry = ('name', 'path', 'DATA')
    assert unique_name(entry) == 'name'

    entry = ('name', 'path', 'PYMODULE')
    assert unique_name(entry) == 'name'

def test_TOC_deprecation_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        toc = TOC()
        assert len(w) == 1
        assert issubclass(w[-1].category, DeprecationWarning)

def test_TOC_append():
    toc = TOC()
    entry = ('name', 'path', 'BINARY')
    toc.append(entry)
    assert toc == [entry]

    with pytest.raises(TypeError):
        toc.append('not_a_tuple')

def test_TOC_insert():
    toc = TOC()
    entry = ('name', 'path', 'BINARY')
    toc.insert(0, entry)
    assert toc == [entry]

    with pytest.raises(TypeError):
        toc.insert(0, 'not_a_tuple')

def test_TOC_add():
    toc1 = TOC([('name1', 'path1', 'BINARY')])
    toc2 = TOC([('name2', 'path2', 'DATA')])
    result = toc1 + toc2
    assert result == TOC([('name1', 'path1', 'BINARY'), ('name2', 'path2', 'DATA')])

def test_TOC_sub():
    toc1 = TOC([('name1', 'path1', 'BINARY'), ('name2', 'path2', 'DATA')])
    toc2 = TOC([('name1', 'path1', 'BINARY')])
    result = toc1 - toc2
    assert result == TOC([('name2', 'path2', 'DATA')])

def test_TOC_setitem():
    toc = TOC([('name1', 'path1', 'BINARY')])
    toc[0] = ('name2', 'path2', 'DATA')
    assert toc == TOC([('name2', 'path2', 'DATA')])

def test_TOC_extend():
    toc = TOC([('name1', 'path1', 'BINARY')])
    toc.extend([('name2', 'path2', 'DATA')])
    assert toc == TOC([('name1', 'path1', 'BINARY'), ('name2', 'path2', 'DATA')])

def test_tree_assemble(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "file1.txt").write_text("content")
    (root / "subdir").mkdir()
    (root / "subdir/file2.txt").write_text("content")

    tree = Tree(str(root))
    tree.assemble()

    expected = [
        ('file1.txt', str(root / "file1.txt"), 'DATA'),
        ('subdir/file2.txt', str(root / "subdir/file2.txt"), 'DATA')
    ]

    assert sorted(tree) == sorted(expected)

def test_normalize_toc():
    toc = [
        ('name1', 'path1', 'OPTION'),
        ('name2', 'path2', 'BINARY'),
        ('name3', 'path3', 'DATA'),
        ('name2', 'path2', 'EXTENSION')
    ]
    normalized = normalize_toc(toc)
    expected = [
        ('name1', 'path1', 'OPTION'),
        ('name2', 'path2', 'EXTENSION'),
        ('name3', 'path3', 'DATA')
    ]
    assert normalized == expected

def test_normalize_pyz_toc():
    toc = [
        ('name1', 'path1', 'PYMODULE'),
        ('name2', 'path2', 'PYMODULE-1'),
        ('name3', 'path3', 'PYMODULE-2'),
        ('name1', 'path1', 'PYMODULE-1')
    ]
    normalized = normalize_pyz_toc(toc)
    expected = [
        ('name3', 'path3', 'PYMODULE-2'),
        ('name2', 'path2', 'PYMODULE-1'),
        ('name1', 'path1', 'PYMODULE-1')
    ]
    assert normalized == expected

def test_toc_process_symbolic_links(tmp_path):
    file1 = tmp_path / "file1.txt"
    file1.write_text("content")
    symlink = tmp_path / "symlink.txt"
    symlink.symlink_to(file1)

    toc = [
        ('file1.txt', str(file1), 'DATA'),
        ('symlink.txt', str(symlink), 'DATA')
    ]

    processed_toc = toc_process_symbolic_links(toc)
    expected = [
        ('file1.txt', str(file1), 'DATA'),
        ('symlink.txt', 'file1.txt', 'SYMLINK')
    ]

    assert processed_toc == expected