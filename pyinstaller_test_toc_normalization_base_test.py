import os
import pytest
import warnings
from pyinstaller.test_toc_normalization.test_toc_normalization import (
    TOC, unique_name, Target, Tree, normalize_toc, normalize_pyz_toc, toc_process_symbolic_links
)

def test_unique_name():
    entry = ('name', '/path/to/file', 'BINARY')
    assert unique_name(entry) == 'name'

    entry = ('Name', '/path/to/file', 'BINARY')
    assert unique_name(entry) == 'name'

    entry = ('name', '/path/to/file', 'DATA')
    assert unique_name(entry) == 'name'

    entry = ('name', '/path/to/file', 'OPTION')
    assert unique_name(entry) == 'name'

def test_TOC_append():
    toc = TOC()
    toc.append(('name', '/path/to/file', 'BINARY'))
    assert len(toc) == 1
    toc.append(('name', '/path/to/file', 'BINARY'))  # duplicate
    assert len(toc) == 1

def test_TOC_append_type_error():
    toc = TOC()
    with pytest.raises(TypeError):
        toc.append(['not', 'a', 'tuple'])

def test_TOC_insert():
    toc = TOC()
    toc.append(('name1', '/path/to/file1', 'BINARY'))
    toc.insert(0, ('name2', '/path/to/file2', 'DATA'))
    assert len(toc) == 2
    assert toc[0] == ('name2', '/path/to/file2', 'DATA')

def test_TOC_insert_type_error():
    toc = TOC()
    with pytest.raises(TypeError):
        toc.insert(0, ['not', 'a', 'tuple'])

def test_TOC_add():
    toc1 = TOC([('name1', '/path/to/file1', 'BINARY')])
    toc2 = TOC([('name2', '/path/to/file2', 'DATA')])
    result = toc1 + toc2
    assert len(result) == 2

def test_TOC_sub():
    toc1 = TOC([('name1', '/path/to/file1', 'BINARY'), ('name2', '/path/to/file2', 'DATA')])
    toc2 = TOC([('name2', '/path/to/file2', 'DATA')])
    result = toc1 - toc2
    assert len(result) == 1
    assert result[0] == ('name1', '/path/to/file1', 'BINARY')

def test_TOC_setitem_slice():
    toc = TOC([('name1', '/path/to/file1', 'BINARY')])
    toc[:] = [('name2', '/path/to/file2', 'DATA')]
    assert len(toc) == 1
    assert toc[0] == ('name2', '/path/to/file2', 'DATA')

def test_TOC_setitem_keyerror():
    toc = TOC([('name1', '/path/to/file1', 'BINARY')])
    with pytest.raises(KeyError):
        toc[1:2] = [('name2', '/path/to/file2', 'DATA')]

def test_Target_postinit():
    class TestTarget(Target):
        def assemble(self):
            pass

    target = TestTarget()
    target.__postinit__()
    assert os.path.basename(target.tocfilename) == target.tocbasename

def test_normalize_toc():
    toc = [
        ('name1', '/path/to/file1', 'BINARY'),
        ('name2', '/path/to/file2', 'DATA'),
        ('name1', '/path/to/file3', 'DEPENDENCY')
    ]
    result = normalize_toc(toc)
    assert len(result) == 2
    assert result[0] == ('name1', '/path/to/file3', 'DEPENDENCY')

def test_normalize_pyz_toc():
    toc = [
        ('name1', '/path/to/file1', 'PYMODULE'),
        ('name2', '/path/to/file2', 'PYMODULE-1'),
        ('name1', '/path/to/file3', 'PYMODULE-2')
    ]
    result = normalize_pyz_toc(toc)
    assert len(result) == 2
    assert result[0] == ('name2', '/path/to/file2', 'PYMODULE-1')
    assert result[1] == ('name1', '/path/to/file3', 'PYMODULE-2')

def test_toc_process_symbolic_links(tmp_path):
    link_target = tmp_path / 'target'
    link_target.write_text("content")
    link_path = tmp_path / 'link'
    link_path.symlink_to(link_target)

    toc = [
        ('name1', str(link_path), 'DATA'),
        ('name2', str(link_target), 'DATA')
    ]

    result = toc_process_symbolic_links(toc)
    assert len(result) == 2
    assert result[0][2] == 'SYMLINK' or result[1][2] == 'SYMLINK'

def test_tree_assemble(tmp_path):
    root = tmp_path / 'root'
    root.mkdir()
    file = root / 'file.txt'
    file.write_text("content")

    tree = Tree(root=str(root))
    tree.assemble()

    assert len(tree) == 1
    assert tree[0] == ('file.txt', str(file), 'DATA')

def test_tree_excludes(tmp_path):
    root = tmp_path / 'root'
    root.mkdir()
    file1 = root / 'file1.txt'
    file1.write_text("content")
    file2 = root / 'file2.log'
    file2.write_text("content")

    tree = Tree(root=str(root), excludes=['*.log'])
    tree.assemble()

    assert len(tree) == 1
    assert tree[0] == ('file1.txt', str(file1), 'DATA')