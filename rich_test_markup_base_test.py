import pytest
from rich.text import Text
from rich.style import Style
from rich.errors import MarkupError
from rich.console import Console
from rich.markup import render, escape, _parse, Tag


def test_escape():
    assert escape("[bold]Hello World[/bold]") == "\\[bold]Hello World\\[/bold]"
    assert escape("No markup here") == "No markup here"
    assert escape("Backslash \\\\[bold]") == "Backslash \\\\[bold]"


def test_render_basic():
    console = Console()
    text = render("[bold]Hello[/bold] World")
    assert isinstance(text, Text)
    assert text.plain == "Hello World"
    assert text.spans[0].style == "bold"


def test_render_nested():
    console = Console()
    text = render("[bold]Hello [italic]World[/italic][/bold]")
    assert isinstance(text, Text)
    assert text.plain == "Hello World"
    assert text.spans[0].style == "bold"
    assert text.spans[1].style == "italic"


def test_render_invalid_markup():
    with pytest.raises(MarkupError):
        render("[bold]Hello [italic]World[/bold]")


def test_parse_tags():
    tags = list(_parse("[bold]Hello [italic]World[/italic][/bold]"))
    assert len(tags) == 3
    assert tags[0][2] == Tag(name="bold", parameters=None)
    assert tags[1][2] == Tag(name="italic", parameters=None)
    assert tags[2][2] == Tag(name="/italic", parameters=None)


def test_parse_escaped_tags():
    parts = list(_parse(r"Look at this \[bold]bold\[bold]"))
    assert len(parts) == 2
    assert parts[0][1] == "Look at this [bold]bold"
    assert parts[1][2] == Tag(name="bold", parameters=None)


def test_parse_invalid_markup():
    with pytest.raises(MarkupError):
        list(_parse("[bold]Hello [italic]World[/bold]"))


def test_render_text_with_emoji():
    text = render("Hello :smile-emoji: World", emoji=True)
    assert ":smile-emoji:" not in text.plain


def test_render_text_without_emoji():
    text = render("Hello :smile: World", emoji=False)
    assert ":smile:" in text.plain