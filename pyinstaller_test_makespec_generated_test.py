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
"""
The tests in this file run `pyi-makespec` with various options and check if
the generated .spec file is correct.
"""

import os
import pytest

from PyInstaller import __main__ as pyi_main
from PyInstaller.test.conftest import skipif_notwin, skipif_notwin_amd64
from PyInstaller.utils.tests import test_utils

# Folder where test scripts are located.
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data', 'makespec')

# Work around for Windows.
if os.name == 'nt':
    # On Windows '.exe' extension must be added to the command name.
    MKPSPEC_CMD = 'pyi-makespec.exe'
else:
    MKPSPEC_CMD = 'pyi-makespec'


def run_makespec(test_id, args, testdir, expected_specfnm=None):
    """
    Run pyi-makespec with given arguments and compare the generated .spec file with the expected one.
    """
    # Run pyi-makespec.
    cmd = [MKPSPEC_CMD] + args
    pyi_main.run(cmd)

    # Load expected .spec file.
    if not expected_specfnm:
        # Expected .spec file is located in the same directory as the test script with suffix '_expected.spec'.
        expected_specfnm = os.path.join(testdir, test_id + '_expected.spec')
    with open(expected_specfnm, 'r', encoding='utf-8') as expected_specfile:
        expected_spec = expected_specfile.read()

    # Load generated .spec file.
    # If specpath is not specified, script name is used for the .spec file name.
    specfnm = test_id + '.spec'
    with open(specfnm, 'r', encoding='utf-8') as specfile:
        spec = specfile.read()

    # Compare the generated .spec file with the expected one.
    # Strip because of newlines.
    assert spec.strip() == expected_spec.strip()


def test_help():
    """
    Run pyi-makespec with --help option.
    """
    cmd = [MKPSPEC_CMD, '--help']
    pyi_main.run(cmd)


def test_simple_script(testdir):
    """
    Make spec file for a simple script without any special options.
    """
    test_id = 'simple_script'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script], testdir)


def test_simple_script_with_specpath(testdir):
    """
    Make spec file for a simple script with the --specpath option.
    """
    test_id = 'simple_script'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    specpath = os.path.join(testdir, 'specpath')

    run_makespec(test_id, [script, '--specpath', specpath], specpath)


def test_exclude_module(testdir):
    """
    Exclude module from the analysis with --exclude-module option.
    """
    test_id = 'exclude_module'
    script = os.path.join(DATA_DIR, 'exclude_module.py')
    run_makespec(test_id, [script, '--exclude-module=excluded_module'], testdir)


def test_hidden_import(testdir):
    """
    Add hidden import with --hidden-import option.
    """
    test_id = 'hidden_import'
    script = os.path.join(DATA_DIR, 'hidden_import.py')
    run_makespec(test_id, [script, '--hidden-import=hidden_module'], testdir)


def test_collect_submodules(testdir):
    """
    Collect submodules with --collect-submodules option.
    """
    test_id = 'collect_submodules'
    script = os.path.join(DATA_DIR, 'collect_submodules.py')
    run_makespec(test_id, [script, '--collect-submodules=collected_submodules'], testdir)


def test_console(testdir):
    """
    Make spec file with --console option.
    """
    test_id = 'console'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--console'], testdir)


def test_no_console(testdir):
    """
    Make spec file with --noconsole option.
    """
    test_id = 'noconsole'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--noconsole'], testdir)


def test_onefile(testdir):
    """
    Make spec file with --onefile option.
    """
    test_id = 'onefile'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--onefile'], testdir)


def test_onefile_with_splash(testdir):
    """
    Make spec file with --onefile --splash option.
    """
    test_id = 'onefile_with_splash'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    splash = os.path.join(DATA_DIR, 'splash.png')
    run_makespec(test_id, [script, '--onefile', '--splash', splash], testdir)


def test_onefile_with_splash_no_console(testdir):
    """
    Make spec file with --onefile --splash --noconsole option.
    """
    test_id = 'onefile_with_splash_no_console'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    splash = os.path.join(DATA_DIR, 'splash.png')
    run_makespec(test_id, [script, '--onefile', '--splash', splash, '--noconsole'], testdir)


def test_debug(testdir):
    """
    Make spec file with --debug option.
    """
    test_id = 'debug'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--debug=bootloader', '--debug=imports', '--debug=noarchive'], testdir)


def test_debug_all(testdir):
    """
    Make spec file with --debug=all option.
    """
    test_id = 'debug_all'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--debug=all'], testdir)


def test_runtime_hook(testdir):
    """
    Make spec file with --runtime-hook option.
    """
    test_id = 'runtime_hook'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    hook = os.path.join(DATA_DIR, 'runtime_hook.py')
    run_makespec(test_id, [script, '--runtime-hook', hook], testdir)


def test_windowed_traceback(testdir):
    """
    Make spec file with --disable-windowed-traceback option.
    """
    test_id = 'windowed_traceback'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--disable-windowed-traceback'], testdir)


@skipif_notwin
def test_icon(testdir):
    """
    Make spec file with --icon option.
    """
    test_id = 'icon'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    ico = os.path.join(DATA_DIR, 'icon.ico')
    run_makespec(test_id, [script, '--icon', ico], testdir)


@skipif_notwin
def test_icon_exe(testdir):
    """
    Make spec file with --icon option, using an icon extracted from an executable.
    """
    test_id = 'icon_exe'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    ico = os.path.join(DATA_DIR, 'icon.exe,1')
    run_makespec(test_id, [script, '--icon', ico], testdir)


@skipif_notwin_amd64
def test_icon_exe_id_0(testdir):
    """
    Make spec file with --icon option, using an icon extracted from an executable.

    Test with icon ID 0, which is a special case.
    """
    test_id = 'icon_exe_id_0'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    ico = os.path.join(DATA_DIR, 'icon_0.exe,0')
    run_makespec(test_id, [script, '--icon', ico], testdir)


@skipif_notwin
def test_icon_none(testdir):
    """
    Make spec file with --icon option, using "NONE" icon.
    """
    test_id = 'icon_none'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    ico = "NONE"
    run_makespec(test_id, [script, '--icon', ico], testdir)


@skipif_notwin
def test_version_file(testdir):
    """
    Make spec file with --version-file option.
    """
    test_id = 'version_file'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    version_file = os.path.join(DATA_DIR, 'version_file.txt')
    run_makespec(test_id, [script, '--version-file', version_file], testdir)


@skipif_notwin
def test_manifest(testdir):
    """
    Make spec file with --manifest option.
    """
    test_id = 'manifest'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    manifest = os.path.join(DATA_DIR, 'manifest.xml')
    run_makespec(test_id, [script, '--manifest', manifest], testdir)


@skipif_notwin
def test_manifest_xml(testdir):
    """
    Make spec file with --manifest option, using XML.
    """
    test_id = 'manifest_xml'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    manifest = '<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0"/>'
    run_makespec(test_id, [script, '--manifest', manifest], testdir)


@skipif_notwin
def test_resources(testdir):
    """
    Make spec file with --resource option.
    """
    test_id = 'resources'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    resource = os.path.join(DATA_DIR, 'resource.rc')
    run_makespec(test_id, [script, '--resource', resource], testdir)


@skipif_notwin
def test_uac_admin(testdir):
    """
    Make spec file with --uac-admin option.
    """
    test_id = 'uac_admin'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--uac-admin'], testdir)


@skipif_notwin
def test_uac_uiaccess(testdir):
    """
    Make spec file with --uac-uiaccess option.
    """
    test_id = 'uac_uiaccess'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--uac-uiaccess'], testdir)


def test_argv_emulation(testdir):
    """
    Make spec file with --argv-emulation option.
    """
    test_id = 'argv_emulation'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--argv-emulation'], testdir)


def test_osx_bundle_identifier(testdir):
    """
    Make spec file with --osx-bundle-identifier option.
    """
    test_id = 'osx_bundle_identifier'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    bundle_identifier = 'org.pyinstaller.test'
    run_makespec(test_id, [script, '--osx-bundle-identifier', bundle_identifier], testdir)


def test_strip(testdir):
    """
    Make spec file with --strip option.
    """
    test_id = 'strip'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--strip'], testdir)


def test_noupx(testdir):
    """
    Make spec file with --noupx option.
    """
    test_id = 'noupx'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--noupx'], testdir)


def test_python_options(testdir):
    """
    Make spec file with --python-options option.
    """
    test_id = 'python_options'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--python-option', 'u', '--python-option', 'v'], testdir)


def test_python_optimize(testdir):
    """
    Make spec file with --optimize option.
    """
    test_id = 'python_optimize'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--optimize', '2'], testdir)


def test_python_option_optimize(testdir):
    """
    Make spec file with --python-options option, using optimization flag.
    """
    test_id = 'python_option_optimize'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--python-option', 'O'], testdir)


def test_python_option_optimize_mismatch(testdir):
    """
    Make spec file with mismatched --optimize and --python-options option.
    """
    test_id = 'python_option_optimize_mismatch'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--optimize', '2', '--python-option', 'O'], testdir)


@pytest.mark.parametrize("optimize", [-1, 0, 1, 2])
def test_optimize(testdir, optimize):
    """
    Make spec file with --optimize option.
    """
    test_id = f'optimize_{optimize}'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, f'--optimize={optimize}'], testdir)


def test_add_data(testdir):
    """
    Make spec file with --add-data option.
    """
    test_id = 'add_data'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    resource = os.path.join(DATA_DIR, 'resource_file:resource_data')
    run_makespec(test_id, [script, '--add-data', resource], testdir)


def test_add_binary(testdir):
    """
    Make spec file with --add-binary option.
    """
    test_id = 'add_binary'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    resource = os.path.join(DATA_DIR, 'resource_file:resource_binary')
    run_makespec(test_id, [script, '--add-binary', resource], testdir)


def test_copy_metadata(testdir):
    """
    Make spec file with --copy-metadata option.
    """
    test_id = 'copy_metadata'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--copy-metadata', 'pytest'], testdir)


def test_recursive_copy_metadata(testdir):
    """
    Make spec file with --recursive-copy-metadata option.
    """
    test_id = 'recursive_copy_metadata'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--recursive-copy-metadata', 'pytest'], testdir)


def test_contents_directory(testdir):
    """
    Make spec file with --contents-directory option.
    """
    test_id = 'contents_directory'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--contents-directory', 'Contents'], testdir)


def test_contents_directory_dot(testdir):
    """
    Make spec file with --contents-directory option set to "."
    """
    test_id = 'contents_directory_dot'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--contents-directory', '.'], testdir)


def test_contents_directory_empty(testdir):
    """
    Make spec file with empty --contents-directory option.
    """
    test_id = 'contents_directory_empty'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--contents-directory', ''], testdir)


def test_bootloader_ignore_signals(testdir):
    """
    Make spec file with --bootloader-ignore-signals option.
    """
    test_id = 'bootloader_ignore_signals'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--bootloader-ignore-signals'], testdir)


def test_all_options(testdir):
    """
    Make spec file with all options.
    """
    test_id = 'all_options'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--onedir', '--onefile'], testdir)


def test_all_options_win(testdir):
    """
    Make spec file with all options (Windows only).
    """
    test_id = 'all_options_win'
    script = os.path.join(DATA_DIR, 'simple_script.py')
    run_makespec(test_id, [script, '--uac-admin', '--uac-uiaccess'], testdir)


def test_path_with_apostrophe(testdir):
    """
    Make spec file for a simple script with a path containing an apostrophe.
    """
    test_id = "simple_script"
    script = os.path.join(DATA_DIR, "simple_script.py")
    path = os.path.join(testdir, "path'with'apostrophe")
    os.makedirs(path)
    script = os.path.join(path, "simple_script.py")
    test_utils.copy_script(script, script)
    run_makespec(test_id, [script], testdir)