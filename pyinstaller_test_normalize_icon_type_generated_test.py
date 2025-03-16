#-----------------------------------------------------------------------------
# Copyright (c) 2022-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

import os
import pytest

from pyinstaller.test_utils import clean_workpath

from pyinstaller.normalize_icon_type import normalize_icon_type


def test_normalize_icon_type_unsupported_file_format(tmp_path, caplog):
    test_path = tmp_path / "empty.txt"
    with open(test_path, "w") as f:
        f.write("")
    with pytest.raises(ValueError, match=r"Received icon image '.*empty.txt' which exists but is not in the correct "
                                         r"format. On this platform, only \('icns',\) images may be used as icons. "
                                         r"If Pillow is installed, automatic conversion will be attempted. Please "
                                         r"install Pillow or convert your 'txt' file to one of \('icns',\) and try "
                                         r"again.") as e:
        normalize_icon_type(
            icon_path=str(test_path),
            allowed_types=("icns",),
            convert_type="icns",
            workpath=tmp_path
        )


@pytest.mark.parametrize(
    ("icon_file", "allowed_types", "convert_type", "expected"),
    (
        pytest.param(
            "pyinstaller/test_normalize_icon_type/data/pyinstaller.icns",
            ("icns",),
            "icns",
            "pyinstaller/test_normalize_icon_type/data/pyinstaller.icns",
            id="icns_file"
        ),
        pytest.param(
            "pyinstaller/test_normalize_icon_type/data/pyinstaller.ico",
            ("ico",),
            "icns",
            "pyinstaller/test_normalize_icon_type/data/pyinstaller.ico",
            id="ico_file"
        ),
        pytest.param(
            "pyinstaller/test_normalize_icon_type/data/pyinstaller.png",
            ("icns",),
            "icns",
            "pyinstaller/test_normalize_icon_type/data/pyinstaller.icns",
            id="png_file"
        ),
    )
)
@pytest.mark.usefixtures("clean_workpath")
def test_normalize_icon_type(icon_file, allowed_types, convert_type, expected, tmp_path):
    result = normalize_icon_type(
        icon_path=icon_file,
        allowed_types=allowed_types,
        convert_type=convert_type,
        workpath=tmp_path
    )
    assert os.path.basename(result) == os.path.basename(expected)