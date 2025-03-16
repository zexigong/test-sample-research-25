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
import shutil
import sys
import tempfile

import pytest

from PyInstaller import compat
from PyInstaller.utils.win32.winmanifest import (
    _DEFAULT_MANIFEST_XML, create_application_manifest, read_manifest_from_executable, write_manifest_to_executable,
)


@pytest.fixture
def temporary_file():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        filename = f.name
    yield filename
    os.unlink(filename)


@pytest.fixture
def temporary_directory():
    dirname = tempfile.mkdtemp()
    yield dirname
    shutil.rmtree(dirname)


@pytest.mark.skipif(not compat.is_win, reason='Only applies to Windows')
def test_create_application_manifest():
    manifest = create_application_manifest()
    assert manifest == _DEFAULT_MANIFEST_XML

    manifest = create_application_manifest(uac_admin=True, uac_uiaccess=True)
    assert b'requestedExecutionLevel level="requireAdministrator"' in manifest
    assert b'requestedExecutionLevel uiAccess="true"' in manifest

    manifest = create_application_manifest(uac_admin=False, uac_uiaccess=True)
    assert b'requestedExecutionLevel level="asInvoker"' in manifest
    assert b'requestedExecutionLevel uiAccess="true"' in manifest

    manifest = create_application_manifest(uac_admin=True, uac_uiaccess=False)
    assert b'requestedExecutionLevel level="requireAdministrator"' in manifest
    assert b'requestedExecutionLevel uiAccess="false"' in manifest


@pytest.mark.skipif(not compat.is_win, reason='Only applies to Windows')
def test_write_and_read_manifest_to_executable(temporary_file):
    filename = temporary_file

    # Write the manifest to the executable.
    write_manifest_to_executable(filename, _DEFAULT_MANIFEST_XML)

    # Read the manifest back from the executable.
    manifest = read_manifest_from_executable(filename)
    assert manifest == _DEFAULT_MANIFEST_XML