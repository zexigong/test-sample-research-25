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
import platform
import shutil
import subprocess
import sys
from unittest import mock

import pytest

from PyInstaller import compat
from PyInstaller.building.utils import (
    _check_guts_eq,
    _check_guts_toc,
    _check_guts_toc_mtime,
    add_suffix_to_extension,
    compile_pymodule,
    create_base_library_zip,
    format_binaries_and_datas,
    process_collected_binary,
    strip_paths_in_code,
)
from PyInstaller.compat import EXTENSION_SUFFIXES, is_darwin
from PyInstaller.config import CONF
from PyInstaller.exceptions import InvalidSrcDestTupleError
from PyInstaller.utils.misc import load_py_data_struct

# Tests for _check_guts_eq.

def test_check_guts_eq_equal():
    """
    Test _check_guts_eq() with equal attribute values.
    """
    # Store the current value of logger.info.
    logger_info = compat.logger.info

    def _mock_logger_info(message, *args):
        """
        Mock logger.info() that raises an exception.
        """
        raise AssertionError(f'logger.info() called: {message % args}')

    compat.logger.info = _mock_logger_info

    try:
        # No logged message should be emitted.
        assert not _check_guts_eq('attr_name', 'old_value', 'old_value', 0)
    finally:
        compat.logger.info = logger_info


def test_check_guts_eq_different():
    """
    Test _check_guts_eq() with different attribute values.
    """
    # Store the current value of logger.info.
    logger_info = compat.logger.info

    def _mock_logger_info(message, *args):
        """
        Mock logger.info() that raises an exception.
        """
        assert message == 'Building because %s changed'
        assert args == ('attr_name',)

    compat.logger.info = _mock_logger_info

    try:
        assert _check_guts_eq('attr_name', 'old_value', 'new_value', 0)
    finally:
        compat.logger.info = logger_info

# Tests for _check_guts_toc_mtime.

def test_check_guts_toc_mtime_empty():
    """
    Test _check_guts_toc_mtime() with an empty TOC.
    """
    # Store the current value of logger.info.
    logger_info = compat.logger.info

    def _mock_logger_info(message, *args):
        """
        Mock logger.info() that raises an exception.
        """
        raise AssertionError(f'logger.info() called: {message % args}')

    compat.logger.info = _mock_logger_info

    try:
        # No logged message should be emitted.
        assert not _check_guts_toc_mtime('attr_name', [], [], 0)
    finally:
        compat.logger.info = logger_info


def test_check_guts_toc_mtime_old():
    """
    Test _check_guts_toc_mtime() with an old TOC file.
    """
    # Store the current value of logger.info.
    logger_info = compat.logger.info

    def _mock_logger_info(message, *args):
        """
        Mock logger.info() that raises an exception.
        """
        raise AssertionError(f'logger.info() called: {message % args}')

    compat.logger.info = _mock_logger_info

    try:
        # No logged message should be emitted.
        assert not _check_guts_toc_mtime('attr_name', [('dest_name', __file__, 'typecode')], [], sys.maxsize)
    finally:
        compat.logger.info = logger_info


def test_check_guts_toc_mtime_new():
    """
    Test _check_guts_toc_mtime() with a new TOC file.
    """
    # Store the current value of logger.info.
    logger_info = compat.logger.info

    def _mock_logger_info(message, *args):
        """
        Mock logger.info() that raises an exception.
        """
        assert message == 'Building because %s changed'
        assert args == (__file__,)

    compat.logger.info = _mock_logger_info

    try:
        assert _check_guts_toc_mtime('attr_name', [('dest_name', __file__, 'typecode')], [], 0)
    finally:
        compat.logger.info = logger_info

# Tests for _check_guts_toc.

def test_check_guts_toc_equal():
    """
    Test _check_guts_toc() with equal TOC contents.
    """
    # Store the current value of logger.info.
    logger_info = compat.logger.info

    def _mock_logger_info(message, *args):
        """
        Mock logger.info() that raises an exception.
        """
        raise AssertionError(f'logger.info() called: {message % args}')

    compat.logger.info = _mock_logger_info

    try:
        # No logged message should be emitted.
        assert not _check_guts_toc('attr_name', [('dest_name', __file__, 'typecode')], [('dest_name', __file__, 'typecode')], sys.maxsize)
    finally:
        compat.logger.info = logger_info


def test_check_guts_toc_different():
    """
    Test _check_guts_toc() with different TOC contents.
    """
    # Store the current value of logger.info.
    logger_info = compat.logger.info

    def _mock_logger_info(message, *args):
        """
        Mock logger.info() that raises an exception.
        """
        assert message == 'Building because %s changed'
        assert args == ('attr_name',)

    compat.logger.info = _mock_logger_info

    try:
        assert _check_guts_toc('attr_name', [('dest_name', __file__, 'typecode')], [], sys.maxsize)
    finally:
        compat.logger.info = logger_info


def test_check_guts_toc_new():
    """
    Test _check_guts_toc() with a new TOC file.
    """
    # Store the current value of logger.info.
    logger_info = compat.logger.info

    def _mock_logger_info(message, *args):
        """
        Mock logger.info() that raises an exception.
        """
        assert message == 'Building because %s changed'
        assert args == (__file__,)

    compat.logger.info = _mock_logger_info

    try:
        assert _check_guts_toc('attr_name', [('dest_name', __file__, 'typecode')], [], 0)
    finally:
        compat.logger.info = logger_info

# Tests for add_suffix_to_extension.

def test_add_suffix_to_extension_noop():
    """
    Test add_suffix_to_extension() with a non-EXTENSION TOC entry.
    """
    toc_entry = ('dest_name', 'src_name', 'typecode')

    assert add_suffix_to_extension(*toc_entry) == toc_entry


def test_add_suffix_to_extension_preprocessed():
    """
    Test add_suffix_to_extension() with a preprocessed TOC entry.
    """
    toc_entry = ('dest_name', 'src_name/dest_name.ext', 'EXTENSION')

    assert add_suffix_to_extension(*toc_entry) == toc_entry


def test_add_suffix_to_extension_nonext():
    """
    Test add_suffix_to_extension() with a non-EXTENSION TOC entry.
    """
    toc_entry = ('dest_name', 'src_name', 'typecode')

    assert add_suffix_to_extension(*toc_entry) == toc_entry


def test_add_suffix_to_extension_suffixed():
    """
    Test add_suffix_to_extension() with an EXTENSION TOC entry with a suffix.
    """
    toc_entry = ('dest_name', 'src_name.ext', 'EXTENSION')

    assert add_suffix_to_extension(*toc_entry) == toc_entry


def test_add_suffix_to_extension():
    """
    Test add_suffix_to_extension() with an EXTENSION TOC entry.
    """
    toc_entry = ('dest_name', 'src_name', 'EXTENSION')

    assert add_suffix_to_extension(*toc_entry) == (
        'dest_name' + os.path.basename('src_name')[len('dest_name'):],
        'src_name',
        'EXTENSION',
    )


def test_add_suffix_to_extension_dotted():
    """
    Test add_suffix_to_extension() with a dotted EXTENSION TOC entry.
    """
    toc_entry = ('dest.name', 'src_name', 'EXTENSION')

    assert add_suffix_to_extension(*toc_entry) == (
        os.path.join('dest', 'name') + os.path.basename('src_name')[len('name'):],
        'src_name',
        'EXTENSION',
    )

# Tests for format_binaries_and_datas.

def test_format_binaries_and_datas():
    """
    Test format_binaries_and_datas() with a valid hook-style 2-tuple.
    """
    assert format_binaries_and_datas([
        (os.path.dirname(__file__), ''),
    ]) == {
        (os.path.basename(__file__), __file__),
    }


def test_format_binaries_and_datas_abs():
    """
    Test format_binaries_and_datas() with an absolute source path.
    """
    assert format_binaries_and_datas([
        (os.path.dirname(__file__), os.path.dirname(__file__)),
    ]) == {
        (os.path.join(os.path.basename(os.path.dirname(__file__)), os.path.basename(__file__)), __file__),
    }


def test_format_binaries_and_datas_glob():
    """
    Test format_binaries_and_datas() with a source glob.
    """
    assert format_binaries_and_datas([
        (__file__, os.path.dirname(__file__)),
    ]) == {
        (os.path.join(os.path.basename(os.path.dirname(__file__)), os.path.basename(__file__)), __file__),
    }


def test_format_binaries_and_datas_glob_workingdir():
    """
    Test format_binaries_and_datas() with a source glob and working directory.
    """
    assert format_binaries_and_datas([
        (os.path.basename(__file__), os.path.dirname(__file__)),
    ], os.path.dirname(__file__)) == {
        (os.path.join(os.path.basename(os.path.dirname(__file__)), os.path.basename(__file__)), __file__),
    }


def test_format_binaries_and_datas_empty_src():
    """
    Test format_binaries_and_datas() with an empty source path.
    """
    with pytest.raises(InvalidSrcDestTupleError):
        format_binaries_and_datas([('', '')])


def test_format_binaries_and_datas_empty_dest():
    """
    Test format_binaries_and_datas() with an empty destination path.
    """
    with pytest.raises(InvalidSrcDestTupleError):
        format_binaries_and_datas([(__file__, '')])


def test_format_binaries_and_datas_abs_dest():
    """
    Test format_binaries_and_datas() with an absolute destination path.
    """
    with pytest.raises(InvalidSrcDestTupleError):
        format_binaries_and_datas([(__file__, os.path.abspath(os.sep))])


def test_format_binaries_and_datas_back_dest():
    """
    Test format_binaries_and_datas() with a relative destination path pointing outside of the top-level directory.
    """
    with pytest.raises(InvalidSrcDestTupleError):
        format_binaries_and_datas([(__file__, os.path.join('..', '..'))])

# Tests for compile_pymodule.

def test_compile_pymodule():
    """
    Test compile_pymodule() with a valid pure-python module.
    """
    assert compile_pymodule('__init__', __file__, os.path.dirname(__file__), 0) == os.path.splitext(__file__)[0] + '.pyc'

# Tests for process_collected_binary.

@pytest.mark.skipif(not is_darwin, reason='macOS-specific test')
def test_process_collected_binary():
    """
    Test process_collected_binary() with a valid binary.
    """
    # Store the current value of CONF['cachedir'].
    cachedir = CONF.get('cachedir')

    try:
        CONF['cachedir'] = os.path.dirname(__file__)

        assert process_collected_binary(__file__, os.path.basename(__file__)) == __file__
    finally:
        if cachedir is None:
            del CONF['cachedir']
        else:
            CONF['cachedir'] = cachedir

def test_process_collected_binary_cache(tmp_path):
    """
    Test process_collected_binary() with a valid binary.

    This test verifies the cache mechanism by processing a binary twice and verifying that the second processing returns
    a different path, indicating that the cached version is returned.
    """
    # Store the current value of CONF['cachedir'].
    cachedir = CONF.get('cachedir')

    try:
        CONF['cachedir'] = str(tmp_path)

        assert process_collected_binary(__file__, os.path.basename(__file__)) != __file__
    finally:
        if cachedir is None:
            del CONF['cachedir']
        else:
            CONF['cachedir'] = cachedir

# Tests for strip_paths_in_code.

def test_strip_paths_in_code():
    """
    Test strip_paths_in_code() with a valid code object.
    """
    assert strip_paths_in_code(compile('', __file__, 'exec')).co_filename == os.path.basename(__file__)

# Tests for create_base_library_zip.

def test_create_base_library_zip():
    """
    Test create_base_library_zip() with a valid modules_toc.
    """
    # Store the current value of logger.info.
    logger_info = compat.logger.info

    def _mock_logger_info(message, *args):
        """
        Mock logger.info() that raises an exception.
        """
        assert message == 'Building because %s changed'
        assert args == ('attr_name',)

    compat.logger.info = _mock_logger_info

    try:
        zip_file = os.path.splitext(__file__)[0] + '.zip'

        try:
            create_base_library_zip(zip_file, [('__init__', __file__, 'PYMODULE')])

            assert load_py_data_struct(zip_file) == {'__init__'}
        finally:
            os.remove(zip_file)
    finally:
        compat.logger.info = logger_info