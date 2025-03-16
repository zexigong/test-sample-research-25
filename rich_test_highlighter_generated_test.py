from rich.highlighter import (
    Highlighter,
    JSONHighlighter,
    NullHighlighter,
    RegexHighlighter,
    ReprHighlighter,
    ISO8601Highlighter,
)
from rich.text import Text


def test_highlighter():
    highlighter = Highlighter()
    text = Text("Hello, World!")
    assert highlighter(text) is text


def test_null_highlighter():
    highlighter = NullHighlighter()
    text = Text("Hello, World!")
    assert highlighter(text) is text


def test_regex_highlighter():
    class MyHighlighter(RegexHighlighter):
        base_style = "foo"
        highlights = [r"(foo)"]

    highlight = MyHighlighter()
    text = highlight("foo")
    assert str(text) == "foo"
    assert len(text.spans) == 1
    assert text.spans[0].start == 0
    assert text.spans[0].end == 3
    assert text.spans[0].style == "foo"


def test_repr_highlighter():
    repr_highlighter = ReprHighlighter()

    result = repr_highlighter(
        """<foo.bar.baz object at 0x7f9e6d25c2e0> 'string', 3.14, True, 2+3j, None, ("foo",), [1,2], {1:2}, ..."""
    )
    print()
    print(result)
    assert str(result) == (
        "<foo.bar.baz object at 0x7f9e6d25c2e0> 'string', 3.14, True, 2+3j, None, ('foo',), [1,2], {1:2}, ..."
    )
    assert (
        repr_highlighter(
            """<foo.bar.baz object at 0x7f9e6d25c2e0> 'string', 3.14, True, 2+3j, None, ("foo",), [1,2], {1:2}, ..."""
        ).markup
        == "<[repr.tag_start]foo.bar.baz[repr.tag_end] object at 0x7f9e6d25c2e0> [repr.str]'string'[repr.str], [repr.number]3.14[repr.number], [repr.bool_true]True[repr.bool_true], [repr.number_complex]2+3j[repr.number_complex], [repr.none]None[repr.none], ([repr.str]'foo'[repr.str],), [repr.brace][[repr.brace][repr.number]1[repr.number],[repr.number]2[repr.number][repr.brace]][repr.brace], {[repr.number]1[repr.number]:[repr.number]2[repr.number]}, [repr.ellipsis]...[repr.ellipsis]"
    )


def test_json_highlighter():
    json_highlighter = JSONHighlighter()
    result = json_highlighter(
        """{"foo": 123, "bar": [false, true, null], "baz": {"egg": "spam"}}"""
    )
    assert (
        result.markup
        == """{[json.key]"foo"[json.key]: [json.number]123[json.number], [json.key]"bar"[json.key]: [[][json.bool_false]false[json.bool_false], [json.bool_true]true[json.bool_true], [json.null]null[json.null][json.brace]][json.brace], [json.key]"baz"[json.key]: {[json.key]"egg"[json.key]: [json.str]"spam"[json.str]}}"""
    )


def test_iso8601_highlighter():
    iso8601_highlighter = ISO8601Highlighter()
    result = iso8601_highlighter(
        """2019-10-12T07:20:50.52Z 2019-10-12T07:20:50.52+00:00 2019-10-12T07:20:50.52-07:00"""
    )
    assert (
        result.markup
        == """[iso8601.date]2019-10-12[iso8601.date][iso8601.time]T07:20:50.52[iso8601.time][iso8601.timezone]Z[iso8601.timezone] [iso8601.date]2019-10-12[iso8601.date][iso8601.time]T07:20:50.52[iso8601.time][iso8601.timezone]+00:00[iso8601.timezone] [iso8601.date]2019-10-12[iso8601.date][iso8601.time]T07:20:50.52[iso8601.time][iso8601.timezone]-07:00[iso8601.timezone]"""
    )