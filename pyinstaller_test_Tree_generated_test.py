#-----------------------------------------------------------------------------
# Copyright (c) 2005-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

import os
import pathlib
import sys
import tempfile

import pytest

from PyInstaller.building.datastruct import TOC
from PyInstaller.building.tree import Tree
from PyInstaller.utils import misc


def test_Tree_simple():
    root = os.path.join(os.getcwd(), 'pyinstaller', 'bootloader', 'windows')
    prefix = os.path.join('pyinstaller', 'bootloader')
    t = Tree(root, prefix)
    # test root is not empty
    assert t.root
    # test prefix is not empty
    assert t.prefix
    assert isinstance(t, Tree)
    assert len(t) == 6
    assert t.typecode == 'DATA'


def test_Tree_none():
    t = Tree()
    assert isinstance(t, Tree)
    assert len(t) == 0


def test_Tree_with_prefix():
    # The test will create a Tree with prefix provided
    root = os.path.join(os.getcwd(), 'pyinstaller', 'bootloader', 'windows')
    prefix = os.path.join('pyinstaller', 'bootloader')
    t = Tree(root, prefix)
    assert isinstance(t, Tree)
    assert len(t) == 6
    assert t.typecode == 'DATA'


def test_Tree_with_prefix_and_excludes():
    # The test will create a Tree with prefix and excludes provided
    excludes = ['test.py']
    root = os.path.join(os.getcwd(), 'pyinstaller', 'bootloader', 'windows')
    prefix = os.path.join('pyinstaller', 'bootloader')
    t = Tree(root, prefix, excludes)
    assert isinstance(t, Tree)
    assert len(t) == 6
    assert t.typecode == 'DATA'


def test_Tree_with_typecode():
    # The test will create a Tree with prefix, excludes and typecode provided
    excludes = ['test.py']
    root = os.path.join(os.getcwd(), 'pyinstaller', 'bootloader', 'windows')
    prefix = os.path.join('pyinstaller', 'bootloader')
    t = Tree(root, prefix, excludes, 'BINARY')
    assert isinstance(t, Tree)
    assert len(t) == 6
    assert t.typecode == 'BINARY'


def test_Tree_with_directory():
    # The test will create a Tree with prefix, excludes and typecode provided
    excludes = ['test.py']
    root = os.path.join(os.getcwd(), 'pyinstaller', 'bootloader', 'windows')
    prefix = os.path.join('pyinstaller', 'bootloader')
    t = Tree(root, prefix, excludes, 'BINARY')
    assert isinstance(t, Tree)
    assert len(t) == 6
    assert t.typecode == 'BINARY'
    assert t.root == root
    assert t.prefix == prefix
    assert t.excludes == excludes


def test_Tree_directory_changed():
    # Test if the directory changes, the Tree object is updated
    excludes = ['test.py']
    root = os.path.join(os.getcwd(), 'pyinstaller', 'bootloader', 'windows')
    prefix = os.path.join('pyinstaller', 'bootloader')
    t = Tree(root, prefix, excludes, 'BINARY')
    assert isinstance(t, Tree)
    assert len(t) == 6
    assert t.typecode == 'BINARY'
    assert t.root == root
    assert t.prefix == prefix
    assert t.excludes == excludes
    new_root = os.path.join(os.getcwd(), 'pyinstaller', 'bootloader', 'posix')
    t.root = new_root
    assert t.root == new_root
    t.root = root


def test_Tree_directory_changed_empty():
    # Test if the directory changes to empty, the Tree object is updated
    excludes = ['test.py']
    root = os.path.join(os.getcwd(), 'pyinstaller', 'bootloader', 'windows')
    prefix = os.path.join('pyinstaller', 'bootloader')
    t = Tree(root, prefix, excludes, 'BINARY')
    assert isinstance(t, Tree)
    assert len(t) == 6
    assert t.typecode == 'BINARY'
    assert t.root == root
    assert t.prefix == prefix
    assert t.excludes == excludes
    new_root = os.path.join(os.getcwd(), 'pyinstaller', 'bootloader', 'posix')
    t.root = None
    assert t.root is None


def test_Tree_directory_changed_to_empty():
    # Test if the directory changes to empty, the Tree object is updated
    excludes = ['test.py']
    root = os.path.join(os.getcwd(), 'pyinstaller', 'bootloader', 'windows')
    prefix = os.path.join('pyinstaller', 'bootloader')
    t = Tree(root, prefix, excludes, 'BINARY')
    assert isinstance(t, Tree)
    assert len(t) == 6
    assert t.typecode == 'BINARY'
    assert t.root == root
    assert t.prefix == prefix
    assert t.excludes == excludes
    new_root = os.path.join(os.getcwd(), 'pyinstaller', 'bootloader', 'posix')
    t.root = ''
    assert t.root == ''


def test_Tree_prefix_changed():
    # Test if the prefix changes, the Tree object is updated
    excludes = ['test.py']
    root = os.path.join(os.getcwd(), 'pyinstaller', 'bootloader', 'windows')
    prefix = os.path.join('pyinstaller', 'bootloader')
    t = Tree(root, prefix, excludes, 'BINARY')
    assert isinstance(t, Tree)
    assert len(t) == 6
    assert t.typecode == 'BINARY'
    assert t.root == root
    assert t.prefix == prefix
    assert t.excludes == excludes
    new_prefix = os.path.join('pyinstaller', 'bootloader', 'posix')
    t.prefix = new_prefix
    assert t.prefix == new_prefix


def test_Tree_prefix_changed_empty():
    # Test if the prefix changes to empty, the Tree object is updated
    excludes = ['test.py']
    root = os.path.join(os.getcwd(), 'pyinstaller', 'bootloader', 'windows')
    prefix = os.path.join('pyinstaller', 'bootloader')
    t = Tree(root, prefix, excludes, 'BINARY')
    assert isinstance(t, Tree)
    assert len(t) == 6
    assert t.typecode == 'BINARY'
    assert t.root == root
    assert t.prefix == prefix
    assert t.excludes == excludes
    new_prefix = os.path.join('pyinstaller', 'bootloader', 'posix')
    t.prefix = None
    assert t.prefix is None


def test_Tree_prefix_changed_to_empty():
    # Test if the prefix changes to empty, the Tree object is updated
    excludes = ['test.py']
    root = os.path.join(os.getcwd(), 'pyinstaller', 'bootloader', 'windows')
    prefix = os.path.join('pyinstaller', 'bootloader')
    t = Tree(root, prefix, excludes, 'BINARY')
    assert isinstance(t, Tree)
    assert len(t) == 6
    assert t.typecode == 'BINARY'
    assert t.root == root
    assert t.prefix == prefix
    assert t.excludes == excludes
    new_prefix = os.path.join('pyinstaller', 'bootloader', 'posix')
    t.prefix = ''
    assert t.prefix == ''


def test_Tree_excludes_changed():
    # Test if the excludes changes, the Tree object is updated
    excludes = ['test.py']
    root = os.path.join(os.getcwd(), 'pyinstaller', 'bootloader', 'windows')
    prefix = os.path.join('pyinstaller', 'bootloader')
    t = Tree(root, prefix, excludes, 'BINARY')
    assert isinstance(t, Tree)
    assert len(t) == 6
    assert t.typecode == 'BINARY'
    assert t.root == root
    assert t.prefix == prefix
    assert t.excludes == excludes
    new_excludes = ['test.py', 'test2.py']
    t.excludes = new_excludes
    assert t.excludes == new_excludes


def test_Tree_excludes_changed_empty():
    # Test if the excludes changes to empty, the Tree object is updated
    excludes = ['test.py']
    root = os.path.join(os.getcwd(), 'pyinstaller', 'bootloader', 'windows')
    prefix = os.path.join('pyinstaller', 'bootloader')
    t = Tree(root, prefix, excludes, 'BINARY')
    assert isinstance(t, Tree)
    assert len(t) == 6
    assert t.typecode == 'BINARY'
    assert t.root == root
    assert t.prefix == prefix
    assert t.excludes == excludes
    new_excludes = []
    t.excludes = new_excludes
    assert t.excludes == new_excludes


def test_Tree_excludes_changed_to_empty():
    # Test if the excludes changes to empty, the Tree object is updated
    excludes = ['test.py']
    root = os.path.join(os.getcwd(), 'pyinstaller', 'bootloader', 'windows')
    prefix = os.path.join('pyinstaller', 'bootloader')
    t = Tree(root, prefix, excludes, 'BINARY')
    assert isinstance(t, Tree)
    assert len(t) == 6
    assert t.typecode == 'BINARY'
    assert t.root == root
    assert t.prefix == prefix
    assert t.excludes == excludes
    new_excludes = None
    t.excludes = new_excludes
    assert t.excludes == new_excludes


def test_Tree_excludes_changed_to_None():
    # Test if the excludes changes to None, the Tree object is updated
    excludes = ['test.py']
    root = os.path.join(os.getcwd(), 'pyinstaller', 'bootloader', 'windows')
    prefix = os.path.join('pyinstaller', 'bootloader')
    t = Tree(root, prefix, excludes, 'BINARY')
    assert isinstance(t, Tree)
    assert len(t) == 6
    assert t.typecode == 'BINARY'
    assert t.root == root
    assert t.prefix == prefix
    assert t.excludes == excludes
    new_excludes = None
    t.excludes = new_excludes
    assert t.excludes == new_excludes


def test_Tree_typecode_changed():
    # Test if the typecode changes, the Tree object is updated
    excludes = ['test.py']
    root = os.path.join(os.getcwd(), 'pyinstaller', 'bootloader', 'windows')
    prefix = os.path.join('pyinstaller', 'bootloader')
    t = Tree(root, prefix, excludes, 'BINARY')
    assert isinstance(t, Tree)
    assert len(t) == 6
    assert t.typecode == 'BINARY'
    assert t.root == root
    assert t.prefix == prefix
    assert t.excludes == excludes
    new_typecode = 'EXTENSION'
    t.typecode = new_typecode
    assert t.typecode == new_typecode


def test_Tree_typecode_changed_empty():
    # Test if the typecode changes to empty, the Tree object is updated
    excludes = ['test.py']
    root = os.path.join(os.getcwd(), 'pyinstaller', 'bootloader', 'windows')
    prefix = os.path.join('pyinstaller', 'bootloader')
    t = Tree(root, prefix, excludes, 'BINARY')
    assert isinstance(t, Tree)
    assert len(t) == 6
    assert t.typecode == 'BINARY'
    assert t.root == root
    assert t.prefix == prefix
    assert t.excludes == excludes
    new_typecode = None
    t.typecode = new_typecode
    assert t.typecode == new_typecode


def test_Tree_typecode_changed_to_empty():
    # Test if the typecode changes to empty, the Tree object is updated
    excludes = ['test.py']
    root = os.path.join(os.getcwd(), 'pyinstaller', 'bootloader', 'windows')
    prefix = os.path.join('pyinstaller', 'bootloader')
    t = Tree(root, prefix, excludes, 'BINARY')
    assert isinstance(t, Tree)
    assert len(t) == 6
    assert t.typecode == 'BINARY'
    assert t.root == root
    assert t.prefix == prefix
    assert t.excludes == excludes
    new_typecode = ''
    t.typecode = new_typecode
    assert t.typecode == new_typecode


def test_Tree_typecode_changed_to_None():
    # Test if the typecode changes to None, the Tree object is updated
    excludes = ['test.py']
    root = os.path.join(os.getcwd(), 'pyinstaller', 'bootloader', 'windows')
    prefix = os.path.join('pyinstaller', 'bootloader')
    t = Tree(root, prefix, excludes, 'BINARY')
    assert isinstance(t, Tree)
    assert len(t) == 6
    assert t.typecode == 'BINARY'
    assert t.root == root
    assert t.prefix == prefix
    assert t.excludes == excludes
    new_typecode = None
    t.typecode = new_typecode
    assert t.typecode == new_typecode


@pytest.fixture
def toc():
    return TOC([
        ('a.txt', 'a.txt', 'DATA'),
        ('b.txt', 'b.txt', 'DATA'),
        ('c.txt', 'c.txt', 'DATA'),
        ('d.txt', 'd.txt', 'DATA'),
        ('e.txt', 'e.txt', 'DATA'),
    ])


@pytest.fixture
def toc_with_duplicates():
    return TOC([
        ('a.txt', 'a.txt', 'DATA'),
        ('b.txt', 'b.txt', 'DATA'),
        ('c.txt', 'c.txt', 'DATA'),
        ('d.txt', 'd.txt', 'DATA'),
        ('e.txt', 'e.txt', 'DATA'),
        ('a.txt', 'a.txt', 'DATA'),
        ('b.txt', 'b.txt', 'DATA'),
        ('c.txt', 'c.txt', 'DATA'),
        ('d.txt', 'd.txt', 'DATA'),
        ('e.txt', 'e.txt', 'DATA'),
    ])


@pytest.fixture
def toc_with_different_types():
    return TOC([
        ('a.txt', 'a.txt', 'DATA'),
        ('b.txt', 'b.txt', 'DATA'),
        ('c.txt', 'c.txt', 'DATA'),
        ('d.txt', 'd.txt', 'DATA'),
        ('e.txt', 'e.txt', 'DATA'),
        ('a.txt', 'a.txt', 'EXTENSION'),
        ('b.txt', 'b.txt', 'EXTENSION'),
        ('c.txt', 'c.txt', 'EXTENSION'),
        ('d.txt', 'd.txt', 'EXTENSION'),
        ('e.txt', 'e.txt', 'EXTENSION'),
    ])


@pytest.fixture
def toc_with_different_types_and_duplicates():
    return TOC([
        ('a.txt', 'a.txt', 'DATA'),
        ('b.txt', 'b.txt', 'DATA'),
        ('c.txt', 'c.txt', 'DATA'),
        ('d.txt', 'd.txt', 'DATA'),
        ('e.txt', 'e.txt', 'DATA'),
        ('a.txt', 'a.txt', 'EXTENSION'),
        ('b.txt', 'b.txt', 'EXTENSION'),
        ('c.txt', 'c.txt', 'EXTENSION'),
        ('d.txt', 'd.txt', 'EXTENSION'),
        ('e.txt', 'e.txt', 'EXTENSION'),
        ('a.txt', 'a.txt', 'DATA'),
        ('b.txt', 'b.txt', 'DATA'),
        ('c.txt', 'c.txt', 'DATA'),
        ('d.txt', 'd.txt', 'DATA'),
        ('e.txt', 'e.txt', 'DATA'),
        ('a.txt', 'a.txt', 'EXTENSION'),
        ('b.txt', 'b.txt', 'EXTENSION'),
        ('c.txt', 'c.txt', 'EXTENSION'),
        ('d.txt', 'd.txt', 'EXTENSION'),
        ('e.txt', 'e.txt', 'EXTENSION'),
    ])


def test_normalize_toc(toc):
    result = misc.normalize_toc(toc)
    assert len(result) == 5


def test_normalize_toc_with_duplicates(toc_with_duplicates):
    result = misc.normalize_toc(toc_with_duplicates)
    assert len(result) == 5


def test_normalize_toc_with_different_types(toc_with_different_types):
    result = misc.normalize_toc(toc_with_different_types)
    assert len(result) == 5


def test_normalize_toc_with_different_types_and_duplicates(toc_with_different_types_and_duplicates):
    result = misc.normalize_toc(toc_with_different_types_and_duplicates)
    assert len(result) == 5


def test_normalize_toc_with_different_types_and_duplicates_and_options(toc_with_different_types_and_duplicates):
    toc_with_options = toc_with_different_types_and_duplicates + TOC([('option', 'option', 'OPTION')])
    result = misc.normalize_toc(toc_with_options)
    assert len(result) == 6


def test_toc_process_symbolic_links():
    # Create a temporary directory with a file and a symbolic link
    with tempfile.TemporaryDirectory() as tempdir:
        file_name = os.path.join(tempdir, 'file.txt')
        with open(file_name, 'w') as file:
            file.write('Test file content')

        symlink_name = os.path.join(tempdir, 'symlink.txt')
        os.symlink(file_name, symlink_name)

        # Create a TOC entry for the file and the symbolic link
        toc = TOC([
            (file_name, file_name, 'DATA'),
            (symlink_name, symlink_name, 'DATA'),
        ])

        # Process the TOC with symbolic links
        processed_toc = misc.toc_process_symbolic_links(toc)

        # Check that the symbolic link entry has been replaced with a SYMLINK entry
        assert len(processed_toc) == 2
        assert processed_toc[1][2] == 'SYMLINK'