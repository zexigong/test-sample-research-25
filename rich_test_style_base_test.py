import pytest
from rich.style import Style, StyleStack, errors, Color, ColorParseError
from rich.color import ColorSystem

def test_style_initialization():
    style = Style(
        color="red",
        bgcolor="blue",
        bold=True,
        italic=False,
        underline=None,
        link="http://example.com"
    )
    assert style.color.name == "red"
    assert style.bgcolor.name == "blue"
    assert style.bold is True
    assert style.italic is False
    assert style.underline is None
    assert style.link == "http://example.com"

def test_style_null():
    style = Style.null()
    assert not style

def test_style_from_color():
    style = Style.from_color(Color.parse("red"), Color.parse("blue"))
    assert style.color.name == "red"
    assert style.bgcolor.name == "blue"

def test_style_from_meta():
    style = Style.from_meta({"key": "value"})
    assert style.meta == {"key": "value"}

def test_style_on():
    style = Style.on(click="handler")
    assert style.meta["@click"] == "handler"

def test_style_str():
    style = Style(color="red", bold=True)
    assert str(style) == "bold red"

def test_style_bool():
    assert bool(Style(color="red"))
    assert not bool(Style())

def test_style_make_ansi_codes():
    style = Style(bold=True)
    assert style._make_ansi_codes(ColorSystem.TRUECOLOR) == "1"

def test_style_normalize():
    assert Style.normalize("bold red") == "bold red"

def test_style_pick_first():
    assert Style.pick_first(None, "bold", None) == "bold"

def test_style_eq():
    style1 = Style(color="red", bold=True)
    style2 = Style(color="red", bold=True)
    style3 = Style(color="blue", bold=True)
    assert style1 == style2
    assert style1 != style3

def test_style_hash():
    style1 = Style(color="red", bold=True)
    style2 = Style(color="red", bold=True)
    assert hash(style1) == hash(style2)

def test_style_without_color():
    style = Style(color="red", bold=True)
    style_no_color = style.without_color
    assert style_no_color.color is None
    assert style_no_color.bold is True

def test_style_parse_valid():
    style = Style.parse("bold red on blue")
    assert style.bold is True
    assert style.color.name == "red"
    assert style.bgcolor.name == "blue"

def test_style_parse_invalid():
    with pytest.raises(errors.StyleSyntaxError):
        Style.parse("invalid style")

def test_style_get_html_style():
    style = Style(color="red", bold=True)
    html_style = style.get_html_style()
    assert "color: #ff0000" in html_style
    assert "font-weight: bold" in html_style

def test_style_combine():
    style1 = Style(bold=True)
    style2 = Style(italic=True)
    combined = Style.combine([style1, style2])
    assert combined.bold is True
    assert combined.italic is True

def test_style_chain():
    style1 = Style(bold=True)
    style2 = Style(italic=True)
    chained = Style.chain(style1, style2)
    assert chained.bold is True
    assert chained.italic is True

def test_style_copy():
    style = Style(color="red", bold=True)
    copied_style = style.copy()
    assert copied_style == style

def test_style_clear_meta_and_links():
    style = Style(color="red", link="http://example.com", meta={"key": "value"})
    cleared_style = style.clear_meta_and_links()
    assert cleared_style.link is None
    assert cleared_style.meta == {}

def test_style_update_link():
    style = Style(color="red", link="http://example.com")
    updated_style = style.update_link("http://newlink.com")
    assert updated_style.link == "http://newlink.com"

def test_style_render():
    style = Style(color="red", bold=True)
    rendered = style.render("Hello", color_system=ColorSystem.TRUECOLOR)
    assert "\x1b[1;38;2;255;0;0mHello\x1b[0m" in rendered

def test_style_stack_push_pop():
    default_style = Style(color="red")
    stack = StyleStack(default_style)
    stack.push(Style(bold=True))
    assert stack.current.bold is True
    stack.pop()
    assert stack.current.bold is not True

def test_style_stack_repr():
    default_style = Style(color="red")
    stack = StyleStack(default_style)
    assert repr(stack) == "<stylestack [Style(color=Color(name='red', type=ColorType.TRUECOLOR, triplet=ColorTriplet(red=255, green=0, blue=0)), bgcolor=None, bold=None, dim=None, italic=None, underline=None, blink=None, blink2=None, reverse=None, conceal=None, strike=None, underline2=None, frame=None, encircle=None, overline=None, link=None)]>"