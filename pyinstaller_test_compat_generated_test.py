# ----------------------------------------------------------------------------
# Copyright (c) 2005-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
# ----------------------------------------------------------------------------

import os
import platform
import sys

import pytest

from PyInstaller import compat

# Set environment variable for testing purposes.
compat.setenv('TEST_ENV', '1')


def test_check_requirements():
    # Ensure function runs without errors.
    compat.check_requirements()


def test_set_get_env():
    assert compat.getenv('TEST_ENV') == '1'
    compat.unsetenv('TEST_ENV')
    assert compat.getenv('TEST_ENV') is None


def test_exec_command():
    if os.name == 'posix':
        compat.exec_command('/bin/ls')
    elif os.name == 'nt':
        compat.exec_command('dir', shell=True)


def test_exec_command_rc():
    if os.name == 'posix':
        compat.exec_command_rc('/bin/ls')
    elif os.name == 'nt':
        compat.exec_command_rc('dir', shell=True)


def test_exec_command_all():
    if os.name == 'posix':
        compat.exec_command_all('/bin/ls')
    elif os.name == 'nt':
        compat.exec_command_all('dir', shell=True)


def test_exec_python():
    compat.exec_python('-c', 'print("test")')


def test_exec_python_rc():
    compat.exec_python_rc('-c', 'print("test")')


def test_getsitepackages():
    compat.getsitepackages()


def test_is_wine_dll():
    with pytest.raises(Exception):
        assert compat.is_wine_dll('')


def test_is_win_wine():
    if compat.is_win:
        assert compat.is_win_wine in [True, False]


def test_bytecode_magic():
    assert isinstance(compat.BYTECODE_MAGIC, bytes)


def test_architecture():
    assert compat.architecture in ['32bit', '64bit']


def test_python_dylib_names():
    dylib_names = compat.PYDYLIB_NAMES
    assert isinstance(dylib_names, set)
    assert len(dylib_names) > 0


def test_importlib_load_source():
    # Check if the function successfully loads a module from a Python source file.
    module = compat.importlib_load_source('compat', compat.__file__)
    assert module.__name__ == 'compat'


@pytest.mark.parametrize('machine, system, expected', [
    ('x86_64', 'Linux', 'intel'),
    ('armv7l', 'Linux', 'arm'),
    ('i386', 'Windows', 'intel'),
    ('aarch64', 'Linux', 'arm'),
    ('ppc64', 'Linux', 'ppc'),
    ('mips', 'Linux', 'mips'),
    ('riscv64', 'Linux', 'riscv'),
    ('s390x', 'Linux', 's390x'),
])
def test__pyi_machine(machine, system, expected):
    assert compat._pyi_machine(machine, system) == expected