import pytest

from rich.style import Style


def test_parse():
    assert Style.parse("bold underline red on black blink") == Style(
        bold=True, underline=True, color="red", bgcolor="black", blink=True
    )
    assert Style.parse("red on black blink") == Style(
        bold=None, underline=None, color="red", bgcolor="black", blink=True
    )
    assert Style.parse("not bold red on black blink") == Style(
        bold=False, underline=None, color="red", bgcolor="black", blink=True
    )
    assert Style.parse("not bold not underline red on black blink") == Style(
        bold=False, underline=False, color="red", bgcolor="black", blink=True
    )
    assert Style.parse("default") == Style.null()
    assert Style.parse("") == Style.null()


def test_parse_with_link():
    assert Style.parse("link https://example.org") == Style(link="https://example.org")
    assert Style.parse("bold link https://example.org") == Style(
        bold=True, link="https://example.org"
    )


def test_parse_with_space_in_link():
    assert Style.parse("bold link https://example.org/with%20spaces") == Style(
        bold=True, link="https://example.org/with%20spaces"
    )


def test_parse_with_meta():
    style = Style.parse("bold link https://example.org")
    assert style == Style(bold=True, link="https://example.org")
    assert style.link == "https://example.org"
    assert style.meta == {}


def test_copy():
    style = Style.parse("bold link https://example.org")
    style_copy = style.copy()
    assert style_copy == style


def test_parse_none():
    assert Style.parse("none") == Style.null()


def test_parse_invalid():
    with pytest.raises(Exception):
        Style.parse("not a valid style")


def test_parse_invalid_not():
    with pytest.raises(Exception):
        Style.parse("not bold not")


def test_parse_rgb():
    assert Style.parse("rgb(255, 0, 0) on rgb(0, 255, 0)") == Style(
        color="rgb(255, 0, 0)", bgcolor="rgb(0, 255, 0)"
    )


def test_parse_none_equivalent():
    assert Style.parse("none") == Style.null()


def test_null():
    assert Style.null() is Style.null()


def test_add():
    style1 = Style(bold=True, color="red")
    style2 = Style(underline=True, bgcolor="black")
    style3 = style1 + style2
    assert style3.bold is True
    assert style3.underline is True
    assert style3.color.name == "red"
    assert style3.bgcolor.name == "black"


def test_add_null():
    style1 = Style(bold=True, color="red")
    style2 = Style.null()
    style3 = style1 + style2
    assert style3.bold is True
    assert style3.color.name == "red"


def test_add_none():
    style1 = Style(bold=True, color="red")
    style2 = None
    style3 = style1 + style2
    assert style3.bold is True
    assert style3.color.name == "red"


def test_parse_empty():
    assert Style.parse("") == Style.null()


def test_style_repr():
    assert repr(Style(bold=True, color="red", bgcolor="black", link="foo")) == (
        "Style(color=Color('red', ColorType.STANDARD, number=1), "
        "bgcolor=Color('black', ColorType.STANDARD, number=0), "
        "bold=True, link='foo')"
    )


def test_get_html_style():
    style = Style(bold=True, color="red", bgcolor="black")
    assert style.get_html_style() == "color: #af0000; text-decoration-color: #af0000; background-color: #000000; font-weight: bold"


def test_clear_links_and_meta():
    style = Style(bold=True, link="foo", meta={"@click": "foo"})
    style_no_links = style.clear_meta_and_links()
    assert style_no_links.bold is True
    assert style_no_links.link is None
    assert style_no_links.meta == {}


def test_style_equality():
    style = Style(bold=True, link="foo", meta={"@click": "foo"})
    assert style != Style(bold=True)
    assert style != object()
    assert style == style
    assert style.copy() == style
    assert style == style.copy()


def test_style_hash():
    style = Style(bold=True, link="foo", meta={"@click": "foo"})
    assert hash(style) == hash(style.copy())
    assert hash(style) == hash(style)


def test_style_equality_colors():
    assert Style(color="red") == Style(color="red")
    assert Style(color="red") != Style(color="blue")
    assert Style(bgcolor="red") == Style(bgcolor="red")
    assert Style(bgcolor="red") != Style(bgcolor="blue")


def test_combine():
    style1 = Style(bold=True, color="red")
    style2 = Style(underline=True, bgcolor="black")
    style3 = Style.combine([style1, style2])
    assert style3.bold is True
    assert style3.underline is True
    assert style3.color.name == "red"
    assert style3.bgcolor.name == "black"


def test_chain():
    style1 = Style(bold=True, color="red")
    style2 = Style(underline=True, bgcolor="black")
    style3 = Style.chain(style1, style2)
    assert style3.bold is True
    assert style3.underline is True
    assert style3.color.name == "red"
    assert style3.bgcolor.name == "black"


def test_pick_first():
    assert Style.pick_first(None, None, "foo", "bar") == "foo"
    assert Style.pick_first(None, None, Style(color="red"), "bar") == Style(
        color="red"
    )


def test_pick_first_invalid():
    with pytest.raises(ValueError):
        assert Style.pick_first(None, None)


def test_parsing_normalizes():
    assert Style.parse("bold") == Style(bold=True)
    assert Style.parse("bold") == Style.parse("bold")


def test_is():
    assert Style(bold=True) is Style(bold=True)
    assert Style(bold=True, color="red") is Style(bold=True, color="red")


def test_parsing_normalizes_link():
    assert Style.parse("link foo") == Style(link="foo")
    assert Style.parse("link foo") == Style.parse("link foo")


def test_update_link():
    style = Style(bold=True, link="foo", meta={"@click": "foo"})
    style2 = style.update_link("bar")
    assert style2.link == "bar"
    assert style2.meta == style.meta
    assert style.link == "foo"


def test_without_color():
    style = Style(bold=True, color="red", link="foo")
    style_without_color = style.without_color
    assert style_without_color.bold is True
    assert style_without_color.color is None
    assert style_without_color.link == "foo"