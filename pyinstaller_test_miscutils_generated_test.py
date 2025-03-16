# -----------------------------------------------------------------------------
# Copyright (c) 2013-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
# -----------------------------------------------------------------------------
import os
import sys
import pytest
from io import BytesIO

from PyInstaller.utils.misc import (
    absnormpath,
    module_parent_packages,
    is_iterable,
    is_file_qt_plugin,
    path_to_parent_archive,
    decode,
)

from PyInstaller.compat import is_win

from PyInstaller.utils.misc import (
    dlls_in_subdirs,
    files_in_dir,
    get_path_to_toplevel_modules,
    mtime,
    save_py_data_struct,
    load_py_data_struct,
)


@pytest.mark.parametrize(
    "path, result",
    [
        ("", ""),
        ("/", "/"),
        ("//", "/"),
        ("///", "/"),
        ("./", "."),
        ("./.", "."),
        ("././", "."),
        ("././.", "."),
        ("./././", "."),
        ("./././.", "."),
        ("././././", "."),
        ("././././.", "."),
        ("./././././", "."),
        ("./././././.", "."),
        ("././././././", "."),
        ("././././././.", "."),
        ("./././././././", "."),
        ("./././././././.", "."),
        ("././././././././", "."),
        ("././././././././.", "."),
        ("./././././././././", "."),
        ("./././././././././.", "."),
        ("././././././././././", "."),
        ("././././././././././.", "."),
        ("./././././././././././", "."),
        ("./././././././././././.", "."),
        ("././././././././././././", "."),
        ("././././././././././././.", "."),
        ("./././././././././././././", "."),
        ("./././././././././././././.", "."),
        ("././././././././././././././", "."),
        ("././././././././././././././.", "."),
        ("./././././././././././././././", "."),
        ("./././././././././././././././.", "."),
        ("././././././././././././././././", "."),
        ("././././././././././././././././.", "."),
        ("./././././././././././././././././", "."),
        ("./././././././././././././././././.", "."),
        ("././././././././././././././././././", "."),
        ("././././././././././././././././././.", "."),
        ("./././././././././././././././././././", "."),
        ("./././././././././././././././././././.", "."),
        ("././././././././././././././././././././", "."),
        ("././././././././././././././././././././.", "."),
        ("./././././././././././././././././././././", "."),
        ("./././././././././././././././././././././.", "."),
        ("././././././././././././././././././././././", "."),
        ("././././././././././././././././././././././.", "."),
        ("./././././././././././././././././././././././", "."),
        ("./././././././././././././././././././././././.", "."),
        ("././././././././././././././././././././././././", "."),
        ("././././././././././././././././././././././././.", "."),
        ("./././././././././././././././././././././././././", "."),
        ("././././././././././././././././././././././././