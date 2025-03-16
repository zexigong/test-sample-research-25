import io
import os
import threading
from time import sleep
from typing import List

import pytest

from rich.console import Console
from rich.file_proxy import FileProxy
from rich.text import Text


class MockIO(io.StringIO):
    def __init__(self, output_list: List[str]) -> None:
        super().__init__()
        self.output_list = output_list

    def flush(self) -> None:
        super().flush()
        self.output_list.append(self.getvalue())
        self.seek(0)
        self.truncate()


def test_file_proxy() -> None:
    console = Console(record=True)
    output_list: List[str] = []
    mock_io = MockIO(output_list)
    proxy = FileProxy(console, mock_io)
    proxy.write("foo\nbar\nbaz\n")
    assert output_list == ["foo\nbar\nbaz\n"]
    console_output = console.export_text()
    assert console_output == "foo\nbar\nbaz\n"
    proxy.write("foo\nbar\nbaz")
    proxy.flush()
    console_output = console.export_text()
    assert console_output == "foo\nbar\nbaz\nfoo\nbar\nbaz\n"


def test_file_proxy_write_bytes() -> None:
    console = Console()
    proxy = FileProxy(console, io.StringIO())
    with pytest.raises(TypeError):
        proxy.write(b"bytes")


def test_file_proxy_write_with_color() -> None:
    console = Console(record=True)
    output_list: List[str] = []
    mock_io = MockIO(output_list)
    proxy = FileProxy(console, mock_io)
    proxy.write("\x1b[31mfoo\n\x1b[32mbar\n")
    assert output_list == ["foo\nbar\n"]
    console_output = console.export_text(styles=True)
    assert console_output == "\x1b[31mfoo\x1b[0m\n\x1b[32mbar\x1b[0m\n"


def test_file_proxy_write_with_utf8() -> None:
    console = Console(record=True)
    output_list: List[str] = []
    mock_io = MockIO(output_list)
    proxy = FileProxy(console, mock_io)
    proxy.write("😄\n")
    assert output_list == ["😄\n"]
    console_output = console.export_text(styles=True)
    assert console_output == "😄\n"


def test_proxied_file() -> None:
    console = Console(record=True)
    mock_io = io.StringIO()
    proxy = FileProxy(console, mock_io)
    assert proxy.rich_proxied_file is mock_io


def test_proxy_fileno() -> None:
    console = Console(record=True)
    mock_io = io.StringIO()
    proxy = FileProxy(console, mock_io)
    with pytest.raises(OSError):
        proxy.fileno()


def test_stdout_proxy() -> None:
    console = Console()
    proxy = FileProxy(console, io.StringIO())
    assert proxy.write("bar") == 3


def test_proxy_write() -> None:
    console = Console(record=True)
    mock_io = io.StringIO()
    proxy = FileProxy(console, mock_io)
    assert proxy.write("foo") == 3


def test_file_proxy_write_flush() -> None:
    console = Console(record=True)
    mock_io = io.StringIO()
    proxy = FileProxy(console, mock_io)
    proxy.write("foo")
    proxy.flush()
    console_output = console.export_text()
    assert console_output == "foo\n"


def test_file_proxy_multithread() -> None:
    console = Console(record=True)
    mock_io = io.StringIO()
    proxy = FileProxy(console, mock_io)

    def write_text():
        for _ in range(100):
            proxy.write("foo\n")
            proxy.write("bar\n")
            proxy.write("baz\n")
            proxy.flush()

    threads = [threading.Thread(target=write_text) for _ in range(100)]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    console_output = console.export_text()
    assert console_output.count("foo\nbar\nbaz\n") == 100 * 100


@pytest.mark.skipif(
    os.name == "nt", reason="CI Windows VMs appear to be too slow for this test"
)
def test_file_proxy_multithread_color() -> None:
    console = Console(record=True)
    mock_io = io.StringIO()
    proxy = FileProxy(console, mock_io)

    def write_text():
        for _ in range(100):
            proxy.write("[red]foo\n")
            proxy.write("[green]bar\n")
            proxy.write("[blue]baz\n")
            proxy.flush()

    threads = [threading.Thread(target=write_text) for _ in range(100)]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    console_output = console.export_text()
    assert console_output.count("foo\nbar\nbaz\n") == 100 * 100