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
import shutil

import pytest

from PyInstaller.building.toc import TOC
from PyInstaller.building.utils import format_binaries_and_datas
from PyInstaller.building.utils import normalize_pyz_toc
from PyInstaller.building.utils import normalize_toc


@pytest.fixture
def basic_toc():
    return [
        # Basic entries
        ('file1', 'path/to/file1', 'BINARY'),
        ('file2', 'path/to/file2', 'BINARY'),
        ('file3', 'path/to/file3', 'BINARY'),

        # Case-variant duplicates
        ('file1', 'path/to/file1', 'BINARY'),
        ('file1', 'path/to/file1', 'BINARY'),
        ('file1', 'path/to/file1', 'BINARY'),
        ('FILE1', 'path/to/file1', 'BINARY'),
        ('File1', 'path/to/file1', 'BINARY'),

        # Non-case-variant duplicates
        ('file2', 'path/to/file2', 'BINARY'),
        ('file2', 'path/to/file2', 'BINARY'),

        # More non-case-variant duplicates, but with different typecodes
        ('file4', 'path/to/file4', 'DATA'),
        ('file4', 'path/to/file4', 'BINARY'),  # higher priority
        ('file4', 'path/to/file4', 'EXTENSION'),  # higher priority

        # Non-case-variant duplicates, with different typecodes and paths
        ('file5', 'path/to/file5', 'BINARY'),
        ('file5', 'path/to/file6', 'EXTENSION'),  # higher priority

        # Entries that must be preserved
        ('file6', 'path/to/file6', 'OPTION'),

        # Duplicates with different src paths
        ('file7', 'path/to/file7', 'BINARY'),
        ('file7', 'path/to/file8', 'BINARY'),  # to be preserved

        # Relative paths
        ('file8', 'path/./../to/file8', 'BINARY'),
        ('file8', './path/./../to/file8', 'BINARY'),

        # Parent directory reference
        ('file9', 'path/../../to/file9', 'BINARY'),

        # Equivalent paths (only the first one should be preserved)
        ('file10', 'path/to/file10', 'BINARY'),
        ('file10', './path/to/file10', 'BINARY'),
        ('file10', 'path/to/./file10', 'BINARY'),
        ('file10', 'path/to/../to/file10', 'BINARY'),
    ]


@pytest.fixture
def basic_toc_normalized():
    return [
        # Basic entries
        ('file1', 'path/to/file1', 'BINARY'),
        ('file2', 'path/to/file2', 'BINARY'),
        ('file3', 'path/to/file3', 'BINARY'),

        # Entries that must be preserved
        ('file6', 'path/to/file6', 'OPTION'),

        # Duplicates with different src paths
        ('file7', 'path/to/file8', 'BINARY'),  # to be preserved

        # Relative paths
        ('file8', 'path/../to/file8', 'BINARY'),

        # Parent directory reference
        ('file9', 'path/../../to/file9', 'BINARY'),

        # Equivalent paths (only the first one should be preserved)
        ('file10', 'path/to/file10', 'BINARY'),

        # Replaced by higher-priority entry
        ('file4', 'path/to/file4', 'EXTENSION'),

        # Replaced by higher-priority entry
        ('file5', 'path/to/file6', 'EXTENSION'),
    ]


@pytest.fixture
def pyz_toc():
    return [
        # Pure-python module
        ('module1', 'path/to/module1', 'PYMODULE'),

        # Optimized pure-python module
        ('module2', 'path/to/module2', 'PYMODULE'),
        ('module2', 'path/to/module2', 'PYMODULE-1'),  # higher priority
        ('module2', 'path/to/module2', 'PYMODULE-2'),  # higher priority

        # Optimized pure-python module
        ('module3', 'path/to/module3', 'PYMODULE'),
        ('module3', 'path/to/module3', 'PYMODULE-1'),  # higher priority

        # Pure-python module
        ('module4', 'path/to/module4', 'PYMODULE'),

        # Pure-python module
        ('module5', 'path/to/module5', 'PYMODULE'),

        # Pure-python module
        ('module6', 'path/to/module6', 'PYMODULE'),
    ]


@pytest.fixture
def pyz_toc_normalized():
    return [
        # Pure-python module
        ('module1', 'path/to/module1', 'PYMODULE'),

        # Optimized pure-python module
        ('module2', 'path/to/module2', 'PYMODULE-2'),  # higher priority

        # Optimized pure-python module
        ('module3', 'path/to/module3', 'PYMODULE-1'),  # higher priority

        # Pure-python module
        ('module4', 'path/to/module4', 'PYMODULE'),

        # Pure-python module
        ('module5', 'path/to/module5', 'PYMODULE'),

        # Pure-python module
        ('module6', 'path/to/module6', 'PYMODULE'),
    ]


@pytest.fixture
def symlink_toc(tempdir, request):
    path = pathlib.Path(tempdir)

    def _create_symlink(src_file, target_file, dest_file):
        target_file.symlink_to(src_file)
        return (str(dest_file), str(target_file), 'BINARY')

    def _create_file(file):
        with open(file, 'wb') as f:
            f.write(b'FOOBAR')

    # Create a file structure as follows:
    # /real/
    #   |- file1
    #   |- file2
    #   |- file3
    #   |- file4
    #   |- file5
    #   |- file6
    #   |- file7
    # /symlink/
    #   |- file1 -> ../../real/file1
    #   |- file2 -> ../real/file2
    #   |- file3 -> ../real/file3
    #   |- file4 -> ../real/file4
    #   |- file5 -> ../real/file5
    #   |- file6 -> ../real/file6
    #   |- file7 -> ../real/file7
    # /dest/
    #   |- file1 -> ../real/file1
    #   |- file2 -> ../real/file2
    #   |- file3 -> ../real/file3
    #   |- file4
    #   |- file5
    #   |- file6
    #   |- file7
    real_dir = path / 'real'
    symlink_dir = path / 'symlink'
    dest_dir = path / 'dest'

    real_dir.mkdir()
    symlink_dir.mkdir()
    dest_dir.mkdir()

    symlink_toc = []

    for i in range(1, 8):
        src_file = real_dir / ('file%d' % i)
        _create_file(src_file)

        target_file = symlink_dir / ('file%d' % i)
        dest_file = dest_dir / ('file%d' % i)
        symlink_toc.append(_create_symlink(src_file, target_file, dest_file))

    return symlink_toc


@pytest.fixture
def symlink_toc_normalized():
    return [
        ('dest/file1', '../real/file1', 'SYMLINK'),
        ('dest/file2', '../real/file2', 'SYMLINK'),
        ('dest/file3', '../real/file3', 'SYMLINK'),
        ('dest/file4', 'symlink/file4', 'BINARY'),
        ('dest/file5', 'symlink/file5', 'BINARY'),
        ('dest/file6', 'symlink/file6', 'BINARY'),
        ('dest/file7', 'symlink/file7', 'BINARY'),
    ]


def test_normalize_toc(basic_toc, basic_toc_normalized):
    res = normalize_toc(basic_toc)
    assert set(res) == set(basic_toc_normalized)


def test_normalize_pyz_toc(pyz_toc, pyz_toc_normalized):
    res = normalize_pyz_toc(pyz_toc)
    assert set(res) == set(pyz_toc_normalized)


def test_toc_process_symbolic_links(symlink_toc, symlink_toc_normalized):
    res = normalize_toc(symlink_toc)
    assert set(res) == set(symlink_toc_normalized)


@pytest.mark.parametrize(
    "binaries_or_datas, expected_toc",
    [
        # A single file.
        ([('/src/file', '.')], [('file', '/src/file')]),
        # A single file with a relative path (the path should be converted to absolute path).
        ([('src/file', '.')], [('file', 'src/file')]),
        # A single file with a target directory.
        ([('/src/file', 'trg')], [('trg/file', '/src/file')]),
        # A single file with a target directory with a trailing slash.
        ([('/src/file', 'trg/')], [('trg/file', '/src/file')]),
        # A single directory.
        ([('/src/dir', '.')], [
            ('dir/file1', '/src/dir/file1'),
            ('dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('dir/subdir2/file3', '/src/dir/subdir2/file3'),
        ]),
        # A single directory with a relative path (the path should be converted to absolute path).
        ([('src/dir', '.')], [
            ('dir/file1', 'src/dir/file1'),
            ('dir/subdir1/file2', 'src/dir/subdir1/file2'),
            ('dir/subdir2/file3', 'src/dir/subdir2/file3'),
        ]),
        # A single directory with a trailing slash.
        ([('/src/dir/', '.')], [
            ('dir/file1', '/src/dir/file1'),
            ('dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('dir/subdir2/file3', '/src/dir/subdir2/file3'),
        ]),
        # A single directory with a target directory.
        ([('/src/dir', 'trg')], [
            ('trg/file1', '/src/dir/file1'),
            ('trg/subdir1/file2', '/src/dir/subdir1/file2'),
            ('trg/subdir2/file3', '/src/dir/subdir2/file3'),
        ]),
        # A single directory with a target directory with a trailing slash.
        ([('/src/dir', 'trg/')], [
            ('trg/file1', '/src/dir/file1'),
            ('trg/subdir1/file2', '/src/dir/subdir1/file2'),
            ('trg/subdir2/file3', '/src/dir/subdir2/file3'),
        ]),
        # A single directory with an implicit target directory.
        ([('/src/dir', '')], [
            ('dir/file1', '/src/dir/file1'),
            ('dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('dir/subdir2/file3', '/src/dir/subdir2/file3'),
        ]),
        # A single directory with an implicit target directory with a trailing slash.
        ([('/src/dir', '')], [
            ('dir/file1', '/src/dir/file1'),
            ('dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('dir/subdir2/file3', '/src/dir/subdir2/file3'),
        ]),
        # A single directory with a target directory outside the working directory.
        ([('/src/dir', '..')], [
            ('../dir/file1', '/src/dir/file1'),
            ('../dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('../dir/subdir2/file3', '/src/dir/subdir2/file3'),
        ]),
        # A single file matching a glob pattern.
        ([('/src/dir/file*', '.')], [('file1', '/src/dir/file1')]),
        # Multiple files matching a glob pattern.
        ([('/src/dir/**/*.py', '.')], [
            ('file1.py', '/src/dir/file1.py'),
            ('subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with an implicit target directory.
        ([('/src/dir/**/*.py', '')], [
            ('file1.py', '/src/dir/file1.py'),
            ('subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory outside the working directory.
        ([('/src/dir/**/*.py', '..')], [
            ('../file1.py', '/src/dir/file1.py'),
            ('../subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('../subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory
        # with a trailing slash.
        ([('/src/dir/**/*.py', 'trg/')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple directories matching a glob pattern.
        ([('/src/*', '.')], [
            ('dir/file1', '/src/dir/file1'),
            ('dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('dir/subdir2/file3', '/src/dir/subdir2/file3'),
            ('dir2/file4', '/src/dir2/file4'),
            ('dir2/subdir3/file5', '/src/dir2/subdir3/file5'),
            ('dir2/subdir4/file6', '/src/dir2/subdir4/file6'),
        ]),
        # Multiple directories matching a glob pattern with a target directory.
        ([('/src/*', 'trg')], [
            ('trg/dir/file1', '/src/dir/file1'),
            ('trg/dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('trg/dir/subdir2/file3', '/src/dir/subdir2/file3'),
            ('trg/dir2/file4', '/src/dir2/file4'),
            ('trg/dir2/subdir3/file5', '/src/dir2/subdir3/file5'),
            ('trg/dir2/subdir4/file6', '/src/dir2/subdir4/file6'),
        ]),
        # Multiple directories matching a glob pattern with a target directory
        # with a trailing slash.
        ([('/src/*', 'trg/')], [
            ('trg/dir/file1', '/src/dir/file1'),
            ('trg/dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('trg/dir/subdir2/file3', '/src/dir/subdir2/file3'),
            ('trg/dir2/file4', '/src/dir2/file4'),
            ('trg/dir2/subdir3/file5', '/src/dir2/subdir3/file5'),
            ('trg/dir2/subdir4/file6', '/src/dir2/subdir4/file6'),
        ]),
        # Multiple directories matching a glob pattern with an implicit target directory.
        ([('/src/*', '')], [
            ('dir/file1', '/src/dir/file1'),
            ('dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('dir/subdir2/file3', '/src/dir/subdir2/file3'),
            ('dir2/file4', '/src/dir2/file4'),
            ('dir2/subdir3/file5', '/src/dir2/subdir3/file5'),
            ('dir2/subdir4/file6', '/src/dir2/subdir4/file6'),
        ]),
        # Multiple directories matching a glob pattern with a target directory outside the working directory.
        ([('/src/*', '..')], [
            ('../dir/file1', '/src/dir/file1'),
            ('../dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('../dir/subdir2/file3', '/src/dir/subdir2/file3'),
            ('../dir2/file4', '/src/dir2/file4'),
            ('../dir2/subdir3/file5', '/src/dir2/subdir3/file5'),
            ('../dir2/subdir4/file6', '/src/dir2/subdir4/file6'),
        ]),
        # Multiple directories matching a glob pattern with a target directory
        # with a trailing slash.
        ([('/src/*', 'trg/')], [
            ('trg/dir/file1', '/src/dir/file1'),
            ('trg/dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('trg/dir/subdir2/file3', '/src/dir/subdir2/file3'),
            ('trg/dir2/file4', '/src/dir2/file4'),
            ('trg/dir2/subdir3/file5', '/src/dir2/subdir3/file5'),
            ('trg/dir2/subdir4/file6', '/src/dir2/subdir4/file6'),
        ]),
        # A single directory with multiple files matching a glob pattern.
        ([('/src/dir/**/*.py', '.')], [
            ('file1.py', '/src/dir/file1.py'),
            ('subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with an implicit target directory.
        ([('/src/dir/**/*.py', '')], [
            ('file1.py', '/src/dir/file1.py'),
            ('subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory outside the working directory.
        ([('/src/dir/**/*.py', '..')], [
            ('../file1.py', '/src/dir/file1.py'),
            ('../subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('../subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory with a trailing slash.
        ([('/src/dir/**/*.py', 'trg/')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
    ],
)
def test_format_binaries_and_datas(binaries_or_datas, expected_toc, tmp_path):
    # Given a source directory with a few files, the function should return
    # a list of tuples with the target path and the source path.
    src_path = tmp_path / 'src'
    src_path.mkdir()
    (src_path / 'file').write_text('file')
    (src_path / 'dir').mkdir()
    (src_path / 'dir' / 'file1').write_text('file1')
    (src_path / 'dir' / 'file1.py').write_text('file1.py')
    (src_path / 'dir' / 'subdir1').mkdir()
    (src_path / 'dir' / 'subdir1' / 'file2').write_text('file2')
    (src_path / 'dir' / 'subdir1' / 'file2.py').write_text('file2.py')
    (src_path / 'dir' / 'subdir2').mkdir()
    (src_path / 'dir' / 'subdir2' / 'file3').write_text('file3')
    (src_path / 'dir' / 'subdir2' / 'file3.py').write_text('file3.py')
    (src_path / 'dir2').mkdir()
    (src_path / 'dir2' / 'file4').write_text('file4')
    (src_path / 'dir2' / 'subdir3').mkdir()
    (src_path / 'dir2' / 'subdir3' / 'file5').write_text('file5')
    (src_path / 'dir2' / 'subdir4').mkdir()
    (src_path / 'dir2' / 'subdir4' / 'file6').write_text('file6')
    binaries_or_datas = [(src_path / src, trg) for src, trg in binaries_or_datas]
    toc = format_binaries_and_datas(binaries_or_datas)
    assert toc == expected_toc


@pytest.mark.parametrize(
    "binaries_or_datas, expected_toc",
    [
        # A single file.
        ([('/src/file', '.')], [('file', '/src/file')]),
        # A single file with a relative path (the path should be converted to absolute path).
        ([('src/file', '.')], [('file', '/workingdir/src/file')]),
        # A single file with a target directory.
        ([('/src/file', 'trg')], [('trg/file', '/src/file')]),
        # A single file with a target directory with a trailing slash.
        ([('/src/file', 'trg/')], [('trg/file', '/src/file')]),
        # A single directory.
        ([('/src/dir', '.')], [
            ('dir/file1', '/src/dir/file1'),
            ('dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('dir/subdir2/file3', '/src/dir/subdir2/file3'),
        ]),
        # A single directory with a relative path (the path should be converted to absolute path).
        ([('src/dir', '.')], [
            ('dir/file1', '/workingdir/src/dir/file1'),
            ('dir/subdir1/file2', '/workingdir/src/dir/subdir1/file2'),
            ('dir/subdir2/file3', '/workingdir/src/dir/subdir2/file3'),
        ]),
        # A single directory with a trailing slash.
        ([('/src/dir/', '.')], [
            ('dir/file1', '/src/dir/file1'),
            ('dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('dir/subdir2/file3', '/src/dir/subdir2/file3'),
        ]),
        # A single directory with a target directory.
        ([('/src/dir', 'trg')], [
            ('trg/file1', '/src/dir/file1'),
            ('trg/subdir1/file2', '/src/dir/subdir1/file2'),
            ('trg/subdir2/file3', '/src/dir/subdir2/file3'),
        ]),
        # A single directory with a target directory with a trailing slash.
        ([('/src/dir', 'trg/')], [
            ('trg/file1', '/src/dir/file1'),
            ('trg/subdir1/file2', '/src/dir/subdir1/file2'),
            ('trg/subdir2/file3', '/src/dir/subdir2/file3'),
        ]),
        # A single directory with an implicit target directory.
        ([('/src/dir', '')], [
            ('dir/file1', '/src/dir/file1'),
            ('dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('dir/subdir2/file3', '/src/dir/subdir2/file3'),
        ]),
        # A single directory with an implicit target directory with a trailing slash.
        ([('/src/dir', '')], [
            ('dir/file1', '/src/dir/file1'),
            ('dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('dir/subdir2/file3', '/src/dir/subdir2/file3'),
        ]),
        # A single directory with a target directory outside the working directory.
        ([('/src/dir', '..')], [
            ('../dir/file1', '/src/dir/file1'),
            ('../dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('../dir/subdir2/file3', '/src/dir/subdir2/file3'),
        ]),
        # A single file matching a glob pattern.
        ([('/src/dir/file*', '.')], [('file1', '/src/dir/file1')]),
        # Multiple files matching a glob pattern.
        ([('/src/dir/**/*.py', '.')], [
            ('file1.py', '/src/dir/file1.py'),
            ('subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with an implicit target directory.
        ([('/src/dir/**/*.py', '')], [
            ('file1.py', '/src/dir/file1.py'),
            ('subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory outside the working directory.
        ([('/src/dir/**/*.py', '..')], [
            ('../file1.py', '/src/dir/file1.py'),
            ('../subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('../subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory with a trailing slash.
        ([('/src/dir/**/*.py', 'trg/')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple directories matching a glob pattern.
        ([('/src/*', '.')], [
            ('dir/file1', '/src/dir/file1'),
            ('dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('dir/subdir2/file3', '/src/dir/subdir2/file3'),
            ('dir2/file4', '/src/dir2/file4'),
            ('dir2/subdir3/file5', '/src/dir2/subdir3/file5'),
            ('dir2/subdir4/file6', '/src/dir2/subdir4/file6'),
        ]),
        # Multiple directories matching a glob pattern with a target directory.
        ([('/src/*', 'trg')], [
            ('trg/dir/file1', '/src/dir/file1'),
            ('trg/dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('trg/dir/subdir2/file3', '/src/dir/subdir2/file3'),
            ('trg/dir2/file4', '/src/dir2/file4'),
            ('trg/dir2/subdir3/file5', '/src/dir2/subdir3/file5'),
            ('trg/dir2/subdir4/file6', '/src/dir2/subdir4/file6'),
        ]),
        # Multiple directories matching a glob pattern with a target directory with a trailing slash.
        ([('/src/*', 'trg/')], [
            ('trg/dir/file1', '/src/dir/file1'),
            ('trg/dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('trg/dir/subdir2/file3', '/src/dir/subdir2/file3'),
            ('trg/dir2/file4', '/src/dir2/file4'),
            ('trg/dir2/subdir3/file5', '/src/dir2/subdir3/file5'),
            ('trg/dir2/subdir4/file6', '/src/dir2/subdir4/file6'),
        ]),
        # Multiple directories matching a glob pattern with an implicit target directory.
        ([('/src/*', '')], [
            ('dir/file1', '/src/dir/file1'),
            ('dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('dir/subdir2/file3', '/src/dir/subdir2/file3'),
            ('dir2/file4', '/src/dir2/file4'),
            ('dir2/subdir3/file5', '/src/dir2/subdir3/file5'),
            ('dir2/subdir4/file6', '/src/dir2/subdir4/file6'),
        ]),
        # Multiple directories matching a glob pattern with a target directory outside the working directory.
        ([('/src/*', '..')], [
            ('../dir/file1', '/src/dir/file1'),
            ('../dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('../dir/subdir2/file3', '/src/dir/subdir2/file3'),
            ('../dir2/file4', '/src/dir2/file4'),
            ('../dir2/subdir3/file5', '/src/dir2/subdir3/file5'),
            ('../dir2/subdir4/file6', '/src/dir2/subdir4/file6'),
        ]),
        # Multiple directories matching a glob pattern with a target directory with a trailing slash.
        ([('/src/*', 'trg/')], [
            ('trg/dir/file1', '/src/dir/file1'),
            ('trg/dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('trg/dir/subdir2/file3', '/src/dir/subdir2/file3'),
            ('trg/dir2/file4', '/src/dir2/file4'),
            ('trg/dir2/subdir3/file5', '/src/dir2/subdir3/file5'),
            ('trg/dir2/subdir4/file6', '/src/dir2/subdir4/file6'),
        ]),
        # A single directory with multiple files matching a glob pattern.
        ([('/src/dir/**/*.py', '.')], [
            ('file1.py', '/src/dir/file1.py'),
            ('subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with an implicit target directory.
        ([('/src/dir/**/*.py', '')], [
            ('file1.py', '/src/dir/file1.py'),
            ('subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory outside the working directory.
        ([('/src/dir/**/*.py', '..')], [
            ('../file1.py', '/src/dir/file1.py'),
            ('../subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('../subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory with a trailing slash.
        ([('/src/dir/**/*.py', 'trg/')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
    ],
)
def test_format_binaries_and_datas_with_workingdir(binaries_or_datas, expected_toc, tmp_path):
    # Given a source directory with a few files, the function should return
    # a list of tuples with the target path and the source path.
    workingdir = tmp_path / 'workingdir'
    src_path = workingdir / 'src'
    workingdir.mkdir()
    src_path.mkdir()
    (src_path / 'file').write_text('file')
    (src_path / 'dir').mkdir()
    (src_path / 'dir' / 'file1').write_text('file1')
    (src_path / 'dir' / 'file1.py').write_text('file1.py')
    (src_path / 'dir' / 'subdir1').mkdir()
    (src_path / 'dir' / 'subdir1' / 'file2').write_text('file2')
    (src_path / 'dir' / 'subdir1' / 'file2.py').write_text('file2.py')
    (src_path / 'dir' / 'subdir2').mkdir()
    (src_path / 'dir' / 'subdir2' / 'file3').write_text('file3')
    (src_path / 'dir' / 'subdir2' / 'file3.py').write_text('file3.py')
    (src_path / 'dir2').mkdir()
    (src_path / 'dir2' / 'file4').write_text('file4')
    (src_path / 'dir2' / 'subdir3').mkdir()
    (src_path / 'dir2' / 'subdir3' / 'file5').write_text('file5')
    (src_path / 'dir2' / 'subdir4').mkdir()
    (src_path / 'dir2' / 'subdir4' / 'file6').write_text('file6')
    binaries_or_datas = [(src_path / src, trg) for src, trg in binaries_or_datas]
    toc = format_binaries_and_datas(binaries_or_datas, workingdir=str(workingdir))
    assert toc == expected_toc


@pytest.mark.parametrize(
    "binaries_or_datas, expected_toc",
    [
        # A single file.
        ([('/src/file', '.')], [('file', '/src/file')]),
        # A single file with a relative path (the path should be converted to absolute path).
        ([('src/file', '.')], [('file', '/src/file')]),
        # A single file with a target directory.
        ([('/src/file', 'trg')], [('trg/file', '/src/file')]),
        # A single file with a target directory with a trailing slash.
        ([('/src/file', 'trg/')], [('trg/file', '/src/file')]),
        # A single directory.
        ([('/src/dir', '.')], [
            ('dir/file1', '/src/dir/file1'),
            ('dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('dir/subdir2/file3', '/src/dir/subdir2/file3'),
        ]),
        # A single directory with a relative path (the path should be converted to absolute path).
        ([('src/dir', '.')], [
            ('dir/file1', '/src/dir/file1'),
            ('dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('dir/subdir2/file3', '/src/dir/subdir2/file3'),
        ]),
        # A single directory with a trailing slash.
        ([('/src/dir/', '.')], [
            ('dir/file1', '/src/dir/file1'),
            ('dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('dir/subdir2/file3', '/src/dir/subdir2/file3'),
        ]),
        # A single directory with a target directory.
        ([('/src/dir', 'trg')], [
            ('trg/file1', '/src/dir/file1'),
            ('trg/subdir1/file2', '/src/dir/subdir1/file2'),
            ('trg/subdir2/file3', '/src/dir/subdir2/file3'),
        ]),
        # A single directory with a target directory with a trailing slash.
        ([('/src/dir', 'trg/')], [
            ('trg/file1', '/src/dir/file1'),
            ('trg/subdir1/file2', '/src/dir/subdir1/file2'),
            ('trg/subdir2/file3', '/src/dir/subdir2/file3'),
        ]),
        # A single directory with an implicit target directory.
        ([('/src/dir', '')], [
            ('dir/file1', '/src/dir/file1'),
            ('dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('dir/subdir2/file3', '/src/dir/subdir2/file3'),
        ]),
        # A single directory with an implicit target directory with a trailing slash.
        ([('/src/dir', '')], [
            ('dir/file1', '/src/dir/file1'),
            ('dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('dir/subdir2/file3', '/src/dir/subdir2/file3'),
        ]),
        # A single directory with a target directory outside the working directory.
        ([('/src/dir', '..')], [
            ('../dir/file1', '/src/dir/file1'),
            ('../dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('../dir/subdir2/file3', '/src/dir/subdir2/file3'),
        ]),
        # A single file matching a glob pattern.
        ([('/src/dir/file*', '.')], [('file1', '/src/dir/file1')]),
        # Multiple files matching a glob pattern.
        ([('/src/dir/**/*.py', '.')], [
            ('file1.py', '/src/dir/file1.py'),
            ('subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with an implicit target directory.
        ([('/src/dir/**/*.py', '')], [
            ('file1.py', '/src/dir/file1.py'),
            ('subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory outside the working directory.
        ([('/src/dir/**/*.py', '..')], [
            ('../file1.py', '/src/dir/file1.py'),
            ('../subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('../subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory with a trailing slash.
        ([('/src/dir/**/*.py', 'trg/')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple directories matching a glob pattern.
        ([('/src/*', '.')], [
            ('dir/file1', '/src/dir/file1'),
            ('dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('dir/subdir2/file3', '/src/dir/subdir2/file3'),
            ('dir2/file4', '/src/dir2/file4'),
            ('dir2/subdir3/file5', '/src/dir2/subdir3/file5'),
            ('dir2/subdir4/file6', '/src/dir2/subdir4/file6'),
        ]),
        # Multiple directories matching a glob pattern with a target directory.
        ([('/src/*', 'trg')], [
            ('trg/dir/file1', '/src/dir/file1'),
            ('trg/dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('trg/dir/subdir2/file3', '/src/dir/subdir2/file3'),
            ('trg/dir2/file4', '/src/dir2/file4'),
            ('trg/dir2/subdir3/file5', '/src/dir2/subdir3/file5'),
            ('trg/dir2/subdir4/file6', '/src/dir2/subdir4/file6'),
        ]),
        # Multiple directories matching a glob pattern with a target directory with a trailing slash.
        ([('/src/*', 'trg/')], [
            ('trg/dir/file1', '/src/dir/file1'),
            ('trg/dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('trg/dir/subdir2/file3', '/src/dir/subdir2/file3'),
            ('trg/dir2/file4', '/src/dir2/file4'),
            ('trg/dir2/subdir3/file5', '/src/dir2/subdir3/file5'),
            ('trg/dir2/subdir4/file6', '/src/dir2/subdir4/file6'),
        ]),
        # Multiple directories matching a glob pattern with an implicit target directory.
        ([('/src/*', '')], [
            ('dir/file1', '/src/dir/file1'),
            ('dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('dir/subdir2/file3', '/src/dir/subdir2/file3'),
            ('dir2/file4', '/src/dir2/file4'),
            ('dir2/subdir3/file5', '/src/dir2/subdir3/file5'),
            ('dir2/subdir4/file6', '/src/dir2/subdir4/file6'),
        ]),
        # Multiple directories matching a glob pattern with a target directory outside the working directory.
        ([('/src/*', '..')], [
            ('../dir/file1', '/src/dir/file1'),
            ('../dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('../dir/subdir2/file3', '/src/dir/subdir2/file3'),
            ('../dir2/file4', '/src/dir2/file4'),
            ('../dir2/subdir3/file5', '/src/dir2/subdir3/file5'),
            ('../dir2/subdir4/file6', '/src/dir2/subdir4/file6'),
        ]),
        # Multiple directories matching a glob pattern with a target directory with a trailing slash.
        ([('/src/*', 'trg/')], [
            ('trg/dir/file1', '/src/dir/file1'),
            ('trg/dir/subdir1/file2', '/src/dir/subdir1/file2'),
            ('trg/dir/subdir2/file3', '/src/dir/subdir2/file3'),
            ('trg/dir2/file4', '/src/dir2/file4'),
            ('trg/dir2/subdir3/file5', '/src/dir2/subdir3/file5'),
            ('trg/dir2/subdir4/file6', '/src/dir2/subdir4/file6'),
        ]),
        # A single directory with multiple files matching a glob pattern.
        ([('/src/dir/**/*.py', '.')], [
            ('file1.py', '/src/dir/file1.py'),
            ('subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with an implicit target directory.
        ([('/src/dir/**/*.py', '')], [
            ('file1.py', '/src/dir/file1.py'),
            ('subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory outside the working directory.
        ([('/src/dir/**/*.py', '..')], [
            ('../file1.py', '/src/dir/file1.py'),
            ('../subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('../subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory with a trailing slash.
        ([('/src/dir/**/*.py', 'trg/')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # Multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
        # A single directory with multiple files matching a glob pattern with a target directory.
        ([('/src/dir/**/*.py', 'trg')], [
            ('trg/file1.py', '/src/dir/file1.py'),
            ('trg/subdir1/file2.py', '/src/dir/subdir1/file2.py'),
            ('trg/subdir2/file3.py', '/src/dir/subdir2/file3.py'),
        ]),
    ],
)
def test_format_binaries_and_datas_with_workingdir_and_relative_src_path(binaries_or_datas, expected_toc, tmp_path):
    # Given a source directory with a few files, the function should return
    # a list of tuples with the target path and the source path.
    workingdir = tmp_path / 'workingdir'
    src_path = workingdir / 'src'
    workingdir.mkdir()
    src_path.mkdir()
    (src_path / 'file').write_text('file')
    (src_path / 'dir').mkdir()
    (src_path / 'dir' / 'file1').write_text('file1')
    (src_path / 'dir' / 'file1.py').write_text('file1.py')
    (src_path / 'dir' / 'subdir1').mkdir()
    (src_path / 'dir' / 'subdir1' / 'file2').write_text('file2')
    (src_path / 'dir' / 'subdir1' / 'file2.py').write_text('file2.py')
    (src_path / 'dir' / 'subdir2').mkdir()
    (src_path / 'dir' / 'subdir2' / 'file3').write_text('file3')
    (src_path / 'dir' / 'subdir2' / 'file3.py').write