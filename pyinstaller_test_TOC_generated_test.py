#-----------------------------------------------------------------------------
# Copyright (c) 2013-2023, PyInstaller Development Team.
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
import pytest

from PyInstaller.building.toc import (
    TOC, Target, Tree, normalize_toc, normalize_pyz_toc, toc_process_symbolic_links, _try_preserving_symbolic_link
)


def test_TOC():
    # On Windows, paths will be case-normalized; ensure we have at least one test case that is not already
    # case-normalized.
    test_cases = [
        ('test', 'C:\\Test\\test', 'BINARY'),
        ('test', 'C:\\TeSt\\test', 'BINARY'),
        ('C:\\Test\\test', 'C:\\Test\\test', 'DATA'),
    ]

    toc = TOC()
    toc.append(test_cases[0])
    toc.append(test_cases[1])
    toc.append(test_cases[2])
    assert len(toc) == 2
    assert toc[0] == test_cases[0]
    assert toc[1] == test_cases[2]

    toc = TOC(test_cases)
    assert len(toc) == 2
    assert toc[0] == test_cases[0]
    assert toc[1] == test_cases[2]

    toc2 = TOC()
    toc2.append(('test', 'C:\\Test\\test', 'DATA'))
    toc2.append(('test1', 'C:\\Test\\test1', 'DATA'))
    toc2.extend(toc)
    assert len(toc2) == 3
    assert toc2[0] == ('test', 'C:\\Test\\test', 'DATA')
    assert toc2[1] == ('test1', 'C:\\Test\\test1', 'DATA')
    assert toc2[2] == test_cases[0]

    toc3 = toc + toc2
    assert len(toc3) == 3
    assert toc3[0] == test_cases[0]
    assert toc3[1] == test_cases[2]
    assert toc3[2] == ('test1', 'C:\\Test\\test1', 'DATA')

    toc3 = toc2 + toc
    assert len(toc3) == 3
    assert toc3[0] == ('test', 'C:\\Test\\test', 'DATA')
    assert toc3[1] == ('test1', 'C:\\Test\\test1', 'DATA')
    assert toc3[2] == test_cases[0]

    toc2 += toc
    assert len(toc2) == 3
    assert toc2[0] == ('test', 'C:\\Test\\test', 'DATA')
    assert toc2[1] == ('test1', 'C:\\Test\\test1', 'DATA')
    assert toc2[2] == test_cases[0]

    toc4 = TOC(test_cases)
    toc4.insert(0, ('test1', 'C:\\Test\\test1', 'DATA'))
    assert len(toc4) == 3
    assert toc4[0] == ('test1', 'C:\\Test\\test1', 'DATA')
    assert toc4[1] == test_cases[0]
    assert toc4[2] == test_cases[2]

    toc5 = toc4 - toc2
    assert len(toc5) == 0
    toc5 = toc2 - toc4
    assert len(toc5) == 1
    assert toc5[0] == ('test1', 'C:\\Test\\test1', 'DATA')


def test_Target():
    t = Target()
    assert os.path.exists(t.tocfilename)


def test_Tree(tmp_path):
    d = tmp_path / 'data'
    d.mkdir()
    f = d / 'file'
    f.write_text('test')
    tree = Tree(str(d))
    assert len(tree) == 1
    assert tree[0][0] == 'file'
    assert tree[0][1] == str(f)
    assert tree[0][2] == 'DATA'


def test_normalize_toc():
    toc = [
        ("distutils", "C:\\python37\\lib\\distutils\\__init__.py", "PYMODULE"),
        ("distutils", "C:\\python37\\lib\\distutils\\__init__.py", "PYMODULE"),
        ("distutils", "C:\\python37\\lib\\distutils\\__init__.py", "PYMODULE-1"),
        ("distutils", "C:\\python37\\lib\\distutils\\__init__.py", "PYMODULE-2"),
        ("distutils.util", "C:\\python37\\lib\\distutils\\util.py", "PYMODULE"),
        ("distutils.util", "C:\\python37\\lib\\distutils\\util.py", "PYMODULE"),
        ("distutils.util", "C:\\python37\\lib\\distutils\\util.py", "PYMODULE-1"),
        ("distutils.util", "C:\\python37\\lib\\distutils\\util.py", "PYMODULE-2"),
        ("distutils.version", "C:\\python37\\lib\\distutils\\version.py", "PYMODULE"),
        ("distutils.version", "C:\\python37\\lib\\distutils\\version.py", "PYMODULE"),
        ("distutils.version", "C:\\python37\\lib\\distutils\\version.py", "PYMODULE-1"),
        ("distutils.version", "C:\\python37\\lib\\distutils\\version.py", "PYMODULE-2"),
        ("distutils.versionpredicate", "C:\\python37\\lib\\distutils\\versionpredicate.py", "PYMODULE"),
        ("distutils.versionpredicate", "C:\\python37\\lib\\distutils\\versionpredicate.py", "PYMODULE"),
        ("distutils.versionpredicate", "C:\\python37\\lib\\distutils\\versionpredicate.py", "PYMODULE-1"),
        ("distutils.versionpredicate", "C:\\python37\\lib\\distutils\\versionpredicate.py", "PYMODULE-2"),
        ("_dummy_thread", "C:\\python37\\DLLs\\_dummy_thread.pyd", "BINARY"),
        ("_dummy_thread.pyd", "C:\\python37\\DLLs\\_dummy_thread.pyd", "BINARY"),
        ("_dummy_thread.pyd", "C:\\python37\\DLLs\\_dummy_thread.pyd", "BINARY"),
        ("_dummy_thread.pyd", "C:\\python37\\DLLs\\_dummy_thread.pyd", "BINARY"),
        ("_elementtree", "C:\\python37\\DLLs\\_elementtree.pyd", "BINARY"),
        ("_elementtree.pyd", "C:\\python37\\DLLs\\_elementtree.pyd", "BINARY"),
        ("_elementtree.pyd", "C:\\python37\\DLLs\\_elementtree.pyd", "BINARY"),
        ("_elementtree.pyd", "C:\\python37\\DLLs\\_elementtree.pyd", "BINARY"),
        ("_heapq", "C:\\python37\\DLLs\\_heapq.pyd", "BINARY"),
        ("_heapq.pyd", "C:\\python37\\DLLs\\_heapq.pyd", "BINARY"),
        ("_heapq.pyd", "C:\\python37\\DLLs\\_heapq.pyd", "BINARY"),
        ("_heapq.pyd", "C:\\python37\\DLLs\\_heapq.pyd", "BINARY"),
        ("_lzma", "C:\\python37\\DLLs\\_lzma.pyd", "BINARY"),
        ("_lzma.pyd", "C:\\python37\\DLLs\\_lzma.pyd", "BINARY"),
        ("_lzma.pyd", "C:\\python37\\DLLs\\_lzma.pyd", "BINARY"),
        ("_lzma.pyd", "C:\\python37\\DLLs\\_lzma.pyd", "BINARY"),
        ("_multiprocessing", "C:\\python37\\DLLs\\_multiprocessing.pyd", "BINARY"),
        ("_multiprocessing.pyd", "C:\\python37\\DLLs\\_multiprocessing.pyd", "BINARY"),
        ("_multiprocessing.pyd", "C:\\python37\\DLLs\\_multiprocessing.pyd", "BINARY"),
        ("_multiprocessing.pyd", "C:\\python37\\DLLs\\_multiprocessing.pyd", "BINARY"),
        ("_overlapped", "C:\\python37\\DLLs\\_overlapped.pyd", "BINARY"),
        ("_overlapped.pyd", "C:\\python37\\DLLs\\_overlapped.pyd", "BINARY"),
        ("_overlapped.pyd", "C:\\python37\\DLLs\\_overlapped.pyd", "BINARY"),
        ("_overlapped.pyd", "C:\\python37\\DLLs\\_overlapped.pyd", "BINARY"),
        ("", None, "OPTION"),
    ]

    norm_toc = normalize_pyz_toc(toc)

    assert norm_toc == [
        ("", None, "OPTION"),
        ("distutils", "C:\\python37\\lib\\distutils\\__init__.py", "PYMODULE-2"),
        ("distutils.util", "C:\\python37\\lib\\distutils\\util.py", "PYMODULE-2"),
        ("distutils.version", "C:\\python37\\lib\\distutils\\version.py", "PYMODULE-2"),
        ("distutils.versionpredicate", "C:\\python37\\lib\\distutils\\versionpredicate.py", "PYMODULE-2"),
        ("_dummy_thread.pyd", "C:\\python37\\DLLs\\_dummy_thread.pyd", "BINARY"),
        ("_elementtree.pyd", "C:\\python37\\DLLs\\_elementtree.pyd", "BINARY"),
        ("_heapq.pyd", "C:\\python37\\DLLs\\_heapq.pyd", "BINARY"),
        ("_lzma.pyd", "C:\\python37\\DLLs\\_lzma.pyd", "BINARY"),
        ("_multiprocessing.pyd", "C:\\python37\\DLLs\\_multiprocessing.pyd", "BINARY"),
        ("_overlapped.pyd", "C:\\python37\\DLLs\\_overlapped.pyd", "BINARY"),
    ]


@pytest.mark.parametrize(
    ("toc", "expected"),
    [
        (
            [
                ("distutils", "C:\\python37\\lib\\distutils\\__init__.py", "PYMODULE"),
                ("distutils", "C:\\python37\\lib\\distutils\\__init__.py", "PYMODULE"),
                ("distutils", "C:\\python37\\lib\\distutils\\__init__.py", "PYMODULE-1"),
                ("distutils", "C:\\python37\\lib\\distutils\\__init__.py", "PYMODULE-2"),
                ("distutils.util", "C:\\python37\\lib\\distutils\\util.py", "PYMODULE"),
                ("distutils.util", "C:\\python37\\lib\\distutils\\util.py", "PYMODULE"),
                ("distutils.util", "C:\\python37\\lib\\distutils\\util.py", "PYMODULE-1"),
                ("distutils.util", "C:\\python37\\lib\\distutils\\util.py", "PYMODULE-2"),
                ("distutils.version", "C:\\python37\\lib\\distutils\\version.py", "PYMODULE"),
                ("distutils.version", "C:\\python37\\lib\\distutils\\version.py", "PYMODULE"),
                ("distutils.version", "C:\\python37\\lib\\distutils\\version.py", "PYMODULE-1"),
                ("distutils.version", "C:\\python37\\lib\\distutils\\version.py", "PYMODULE-2"),
                ("distutils.versionpredicate", "C:\\python37\\lib\\distutils\\versionpredicate.py", "PYMODULE"),
                ("distutils.versionpredicate", "C:\\python37\\lib\\distutils\\versionpredicate.py", "PYMODULE"),
                ("distutils.versionpredicate", "C:\\python37\\lib\\distutils\\versionpredicate.py", "PYMODULE-1"),
                ("distutils.versionpredicate", "C:\\python37\\lib\\distutils\\versionpredicate.py", "PYMODULE-2"),
                ("_dummy_thread", "C:\\python37\\DLLs\\_dummy_thread.pyd", "BINARY"),
                ("_dummy_thread.pyd", "C:\\python37\\DLLs\\_dummy_thread.pyd", "BINARY"),
                ("_dummy_thread.pyd", "C:\\python37\\DLLs\\_dummy_thread.pyd", "BINARY"),
                ("_dummy_thread.pyd", "C:\\python37\\DLLs\\_dummy_thread.pyd", "BINARY"),
                ("_elementtree", "C:\\python37\\DLLs\\_elementtree.pyd", "BINARY"),
                ("_elementtree.pyd", "C:\\python37\\DLLs\\_elementtree.pyd", "BINARY"),
                ("_elementtree.pyd", "C:\\python37\\DLLs\\_elementtree.pyd", "BINARY"),
                ("_elementtree.pyd", "C:\\python37\\DLLs\\_elementtree.pyd", "BINARY"),
                ("_heapq", "C:\\python37\\DLLs\\_heapq.pyd", "BINARY"),
                ("_heapq.pyd", "C:\\python37\\DLLs\\_heapq.pyd", "BINARY"),
                ("_heapq.pyd", "C:\\python37\\DLLs\\_heapq.pyd", "BINARY"),
                ("_heapq.pyd", "C:\\python37\\DLLs\\_heapq.pyd", "BINARY"),
                ("_lzma", "C:\\python37\\DLLs\\_lzma.pyd", "BINARY"),
                ("_lzma.pyd", "C:\\python37\\DLLs\\_lzma.pyd", "BINARY"),
                ("_lzma.pyd", "C:\\python37\\DLLs\\_lzma.pyd", "BINARY"),
                ("_lzma.pyd", "C:\\python37\\DLLs\\_lzma.pyd", "BINARY"),
                ("_multiprocessing", "C:\\python37\\DLLs\\_multiprocessing.pyd", "BINARY"),
                ("_multiprocessing.pyd", "C:\\python37\\DLLs\\_multiprocessing.pyd", "BINARY"),
                ("_multiprocessing.pyd", "C:\\python37\\DLLs\\_multiprocessing.pyd", "BINARY"),
                ("_multiprocessing.pyd", "C:\\python37\\DLLs\\_multiprocessing.pyd", "BINARY"),
                ("_overlapped", "C:\\python37\\DLLs\\_overlapped.pyd", "BINARY"),
                ("_overlapped.pyd", "C:\\python37\\DLLs\\_overlapped.pyd", "BINARY"),
                ("_overlapped.pyd", "C:\\python37\\DLLs\\_overlapped.pyd", "BINARY"),
                ("_overlapped.pyd", "C:\\python37\\DLLs\\_overlapped.pyd", "BINARY"),
            ],
            [
                ("distutils", "C:\\python37\\lib\\distutils\\__init__.py", "PYMODULE-2"),
                ("distutils.util", "C:\\python37\\lib\\distutils\\util.py", "PYMODULE-2"),
                ("distutils.version", "C:\\python37\\lib\\distutils\\version.py", "PYMODULE-2"),
                ("distutils.versionpredicate", "C:\\python37\\lib\\distutils\\versionpredicate.py", "PYMODULE-2"),
                ("_dummy_thread.pyd", "C:\\python37\\DLLs\\_dummy_thread.pyd", "BINARY"),
                ("_elementtree.pyd", "C:\\python37\\DLLs\\_elementtree.pyd", "BINARY"),
                ("_heapq.pyd", "C:\\python37\\DLLs\\_heapq.pyd", "BINARY"),
                ("_lzma.pyd", "C:\\python37\\DLLs\\_lzma.pyd", "BINARY"),
                ("_multiprocessing.pyd", "C:\\python37\\DLLs\\_multiprocessing.pyd", "BINARY"),
                ("_overlapped.pyd", "C:\\python37\\DLLs\\_overlapped.pyd", "BINARY"),
            ],
        ),
        # Test with a single OPTION entry
        (
            [
                ("distutils", "C:\\python37\\lib\\distutils\\__init__.py", "PYMODULE"),
                ("", None, "OPTION"),
            ],
            [
                ("", None, "OPTION"),
                ("distutils", "C:\\python37\\lib\\distutils\\__init__.py", "PYMODULE"),
            ],
        ),
        # Test with multiple OPTION entries
        (
            [
                ("distutils", "C:\\python37\\lib\\distutils\\__init__.py", "PYMODULE"),
                ("", None, "OPTION"),
                ("", None, "OPTION"),
                ("", None, "OPTION"),
            ],
            [
                ("", None, "OPTION"),
                ("", None, "OPTION"),
                ("", None, "OPTION"),
                ("distutils", "C:\\python37\\lib\\distutils\\__init__.py", "PYMODULE"),
            ],
        ),
    ],
)
def test_normalize_pyz_toc(toc, expected):
    assert normalize_pyz_toc(toc) == expected


def test_toc_process_symbolic_links(tmp_path):
    # Create a fake library and its corresponding link
    fake_lib = tmp_path / 'mylib.so'
    fake_lib.write_text('fake content')

    link_target = tmp_path / 'libmylib.so'
    link_target.symlink_to(fake_lib)

    # Prepare a simple TOC
    toc = [
        ("mylib.so", str(fake_lib), "BINARY"),
        ("libmylib.so", str(link_target), "BINARY"),
    ]

    # Process the TOC
    new_toc = toc_process_symbolic_links(toc)

    # Ensure the link entry has been converted to SYMLINK
    assert new_toc == [
        ("mylib.so", str(fake_lib), "BINARY"),
        ("libmylib.so", "mylib.so", "SYMLINK"),
    ]

    # Ensure the library has been collected, but not the link
    for dest_name, src_name, typecode in toc:
        if typecode == "SYMLINK":
            assert not os.path.exists(src_name)
        else:
            assert os.path.exists(src_name)


def test_toc_process_symbolic_links_chained(tmp_path):
    # Prepare a chain of links and files
    fake_lib = tmp_path / 'mylib.so'
    fake_lib.write_text('fake content')

    link_target1 = tmp_path / 'libmylib.so.1'
    link_target1.symlink_to(fake_lib)

    link_target2 = tmp_path / 'libmylib.so'
    link_target2.symlink_to(link_target1)

    # Prepare a simple TOC
    toc = [
        ("mylib.so", str(fake_lib), "BINARY"),
        ("libmylib.so.1", str(link_target1), "BINARY"),
        ("libmylib.so", str(link_target2), "BINARY"),
    ]

    # Process the TOC
    new_toc = toc_process_symbolic_links(toc)

    # Ensure the link entry has been converted to SYMLINK
    assert new_toc == [
        ("mylib.so", str(fake_lib), "BINARY"),
        ("libmylib.so.1", "mylib.so", "SYMLINK"),
        ("libmylib.so", "libmylib.so.1", "SYMLINK"),
    ]

    # Ensure the library has been collected, but not the link
    for dest_name, src_name, typecode in toc:
        if typecode == "SYMLINK":
            assert not os.path.exists(src_name)
        else:
            assert os.path.exists(src_name)


def test_toc_process_symbolic_links_broken(tmp_path):
    # Create a fake library and its corresponding link
    fake_lib = tmp_path / 'mylib.so'
    fake_lib.write_text('fake content')

    link_target = tmp_path / 'libmylib.so'
    link_target.symlink_to(fake_lib)

    # Prepare a simple TOC where the link is broken
    toc = [
        ("libmylib.so", str(link_target), "BINARY"),
    ]

    # Process the TOC
    new_toc = toc_process_symbolic_links(toc)

    # Ensure the link entry is not converted to SYMLINK
    assert new_toc == [
        ("libmylib.so", str(link_target), "BINARY"),
    ]

    # Ensure the link has been collected
    for dest_name, src_name, typecode in toc:
        if typecode == "SYMLINK":
            assert not os.path.exists(src_name)
        else:
            assert os.path.exists(src_name)


def test_toc_process_symbolic_links_absolute(tmp_path):
    # Create a fake library and its corresponding link
    fake_lib = tmp_path / 'mylib.so'
    fake_lib.write_text('fake content')

    link_target = tmp_path / 'libmylib.so'
    link_target.symlink_to(fake_lib)

    # Prepare a simple TOC with absolute paths
    toc = [
        (str(fake_lib), str(fake_lib), "BINARY"),
        (str(link_target), str(link_target), "BINARY"),
    ]

    # Process the TOC
    new_toc = toc_process_symbolic_links(toc)

    # Ensure the link entry has been converted to SYMLINK
    assert new_toc == [
        (str(fake_lib), str(fake_lib), "BINARY"),
        (str(link_target), "mylib.so", "SYMLINK"),
    ]

    # Ensure the library has been collected, but not the link
    for dest_name, src_name, typecode in toc:
        if typecode == "SYMLINK":
            assert not os.path.exists(src_name)
        else:
            assert os.path.exists(src_name)


def test_toc_process_symbolic_links_absolute_broken(tmp_path):
    # Create a fake library and its corresponding link
    fake_lib = tmp_path / 'mylib.so'
    fake_lib.write_text('fake content')

    link_target = tmp_path / 'libmylib.so'
    link_target.symlink_to(fake_lib)

    # Prepare a simple TOC with absolute paths where the link is broken
    toc = [
        (str(link_target), str(link_target), "BINARY"),
    ]

    # Process the TOC
    new_toc = toc_process_symbolic_links(toc)

    # Ensure the link entry is not converted to SYMLINK
    assert new_toc == [
        (str(link_target), str(link_target), "BINARY"),
    ]

    # Ensure the link has been collected
    for dest_name, src_name, typecode in toc:
        if typecode == "SYMLINK":
            assert not os.path.exists(src_name)
        else:
            assert os.path.exists(src_name)


def test_try_preserving_symbolic_link(tmp_path):
    # Create a fake library and its corresponding link
    fake_lib = tmp_path / 'mylib.so'
    fake_lib.write_text('fake content')

    link_target = tmp_path / 'libmylib.so'
    link_target.symlink_to(fake_lib)

    # Prepare a simple TOC
    toc = [
        ("mylib.so", str(fake_lib), "BINARY"),
        ("libmylib.so", str(link_target), "BINARY"),
    ]

    # Try preserving symbolic link; expect success
    link_entry = _try_preserving_symbolic_link("libmylib.so", str(link_target), [x[0] for x in toc])
    assert link_entry == ("libmylib.so", "mylib.so", "SYMLINK")


def test_try_preserving_symbolic_link_chained(tmp_path):
    # Prepare a chain of links and files
    fake_lib = tmp_path / 'mylib.so'
    fake_lib.write_text('fake content')

    link_target1 = tmp_path / 'libmylib.so.1'
    link_target1.symlink_to(fake_lib)

    link_target2 = tmp_path / 'libmylib.so'
    link_target2.symlink_to(link_target1)

    # Prepare a simple TOC
    toc = [
        ("mylib.so", str(fake_lib), "BINARY"),
        ("libmylib.so.1", str(link_target1), "BINARY"),
        ("libmylib.so", str(link_target2), "BINARY"),
    ]

    # Try preserving symbolic link; expect success
    link_entry = _try_preserving_symbolic_link("libmylib.so", str(link_target2), [x[0] for x in toc])
    assert link_entry == ("libmylib.so", "libmylib.so.1", "SYMLINK")


def test_try_preserving_symbolic_link_broken(tmp_path):
    # Create a fake library and its corresponding link
    fake_lib = tmp_path / 'mylib.so'
    fake_lib.write_text('fake content')

    link_target = tmp_path / 'libmylib.so'
    link_target.symlink_to(fake_lib)

    # Prepare a simple TOC where the link is broken
    toc = [
        ("libmylib.so", str(link_target), "BINARY"),
    ]

    # Try preserving symbolic link; expect failure
    link_entry = _try_preserving_symbolic_link("libmylib.so", str(link_target), [x[0] for x in toc])
    assert link_entry is None


def test_try_preserving_symbolic_link_absolute(tmp_path):
    # Create a fake library and its corresponding link
    fake_lib = tmp_path / 'mylib.so'
    fake_lib.write_text('fake content')

    link_target = tmp_path / 'libmylib.so'
    link_target.symlink_to(fake_lib)

    # Prepare a simple TOC with absolute paths
    toc = [
        (str(fake_lib), str(fake_lib), "BINARY"),
        (str(link_target), str(link_target), "BINARY"),
    ]

    # Try preserving symbolic link; expect success
    link_entry = _try_preserving_symbolic_link(str(link_target), str(link_target), [x[0] for x in toc])
    assert link_entry == (str(link_target), "mylib.so", "SYMLINK")


def test_try_preserving_symbolic_link_absolute_broken(tmp_path):
    # Create a fake library and its corresponding link
    fake_lib = tmp_path / 'mylib.so'
    fake_lib.write_text('fake content')

    link_target = tmp_path / 'libmylib.so'
    link_target.symlink_to(fake_lib)

    # Prepare a simple TOC with absolute paths where the link is broken
    toc = [
        (str(link_target), str(link_target), "BINARY"),
    ]

    # Try preserving symbolic link; expect failure
    link_entry = _try_preserving_symbolic_link(str(link_target), str(link_target), [x[0] for x in toc])
    assert link_entry is None