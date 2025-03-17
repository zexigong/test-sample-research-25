import io
from unittest.mock import MagicMock

import pytest
from rich.console import Console
from rich.text import Text

from rich.test_file_proxy import FileProxy


@pytest.fixture
def mock_console():
    return MagicMock(Console)


@pytest.fixture
def mock_file():
    return io.StringIO()


@pytest.fixture
def file_proxy(mock_console, mock_file):
    return FileProxy(mock_console, mock_file)


def test_write_string(file_proxy, mock_console):
    text = "Hello, World!\n"
    file_proxy.write(text)
    file_proxy.flush()
    mock_console.print.assert_called_once_with(Text("Hello, World!"))


def test_write_non_string(file_proxy):
    with pytest.raises(TypeError):
        file_proxy.write(123)


def test_write_partial_line(file_proxy, mock_console):
    text = "Hello, "
    file_proxy.write(text)
    file_proxy.flush()
    mock_console.print.assert_not_called()  # Shouldn't print until a newline is encountered


def test_flush(file_proxy, mock_console):
    text = "Hello, World!"
    file_proxy.write(text)
    file_proxy.flush()
    mock_console.print.assert_called_once_with("Hello, World!")


def test_fileno(file_proxy, mock_file):
    assert file_proxy.fileno() == mock_file.fileno()


def test_rich_proxied_file(file_proxy, mock_file):
    assert file_proxy.rich_proxied_file == mock_file


def test_write_multiple_lines(file_proxy, mock_console):
    text = "Hello\nWorld\n"
    file_proxy.write(text)
    file_proxy.flush()
    mock_console.print.assert_any_call(Text("Hello"))
    mock_console.print.assert_any_call(Text("World"))


def test_write_and_flush(file_proxy, mock_console):
    file_proxy.write("Hello, World!")
    file_proxy.flush()
    mock_console.print.assert_called_once_with("Hello, World!")