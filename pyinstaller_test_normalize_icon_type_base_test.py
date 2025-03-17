import pytest
import os
from unittest.mock import patch, mock_open
from pyinstaller.test_normalize_icon_type.normalize_icon_type import normalize_icon_type, hex_signatures

@pytest.fixture
def setup_tmpdir(tmpdir):
    # Create a temporary directory for testing
    return str(tmpdir)

def test_icon_file_not_found(setup_tmpdir):
    with pytest.raises(FileNotFoundError):
        normalize_icon_type("non_existent_file.ico", ("ico", "exe"), "icns", setup_tmpdir)

def test_correct_icon_type(setup_tmpdir):
    icon_content = b'\x00\x00\x01\x00'
    icon_path = os.path.join(setup_tmpdir, "test.ico")

    # Mock the open function to simulate reading the file content
    with patch("builtins.open", mock_open(read_data=icon_content)):
        with patch("os.path.exists", return_value=True):
            result = normalize_icon_type(icon_path, ("ico", "exe"), "icns", setup_tmpdir)
            assert result == icon_path

def test_incorrect_icon_type_without_pillow(setup_tmpdir):
    icon_content = b'\x89PNG\r\n\x1A\n'
    icon_path = os.path.join(setup_tmpdir, "test.png")

    with patch("builtins.open", mock_open(read_data=icon_content)):
        with patch("os.path.exists", return_value=True):
            with patch("pyinstaller.test_normalize_icon_type.normalize_icon_type.PILImage", side_effect=ImportError):
                with pytest.raises(ValueError):
                    normalize_icon_type(icon_path, ("ico", "exe"), "icns", setup_tmpdir)

def test_incorrect_icon_type_with_pillow(setup_tmpdir):
    icon_content = b'\x89PNG\r\n\x1A\n'
    icon_path = os.path.join(setup_tmpdir, "test.png")

    with patch("builtins.open", mock_open(read_data=icon_content)):
        with patch("os.path.exists", return_value=True):
            with patch("pyinstaller.test_normalize_icon_type.normalize_icon_type.PILImage.open") as mock_open:
                mock_image = mock_open.return_value.__enter__.return_value
                mock_image.mode = "RGB"
                mock_image.info = {}
                
                result = normalize_icon_type(icon_path, ("ico", "exe"), "icns", setup_tmpdir)
                assert result.startswith(setup_tmpdir)
                assert result.endswith(".icns")

def test_conversion_failure_with_pillow(setup_tmpdir):
    icon_content = b'\x89PNG\r\n\x1A\n'
    icon_path = os.path.join(setup_tmpdir, "test.png")

    with patch("builtins.open", mock_open(read_data=icon_content)):
        with patch("os.path.exists", return_value=True):
            with patch("pyinstaller.test_normalize_icon_type.normalize_icon_type.PILImage.open", side_effect=ValueError):
                with pytest.raises(ValueError):
                    normalize_icon_type(icon_path, ("ico", "exe"), "icns", setup_tmpdir)