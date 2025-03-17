import pytest
from rich.text import Text, Span
from rich.highlighter import (
    Highlighter,
    NullHighlighter,
    RegexHighlighter,
    ReprHighlighter,
    JSONHighlighter,
    ISO8601Highlighter,
)


class TestHighlighter:
    def test_highlighter_abstract(self):
        with pytest.raises(TypeError):
            Highlighter()

    def test_null_highlighter(self):
        null_highlighter = NullHighlighter()
        text = Text("Hello, World!")
        result = null_highlighter(text)
        assert result.plain == "Hello, World!"
        assert result.spans == []

    def test_regex_highlighter(self):
        class TestRegexHighlighter(RegexHighlighter):
            highlights = [r"World", r"Hello"]

        regex_highlighter = TestRegexHighlighter()
        text = Text("Hello, World!")
        result = regex_highlighter(text)
        assert result.plain == "Hello, World!"
        assert len(result.spans) == 2
        assert result.spans[0] == Span(0, 5, "")
        assert result.spans[1] == Span(7, 12, "")

    def test_repr_highlighter(self):
        repr_highlighter = ReprHighlighter()
        text = Text("<tag attrib='value'>")
        result = repr_highlighter(text)
        assert result.plain == "<tag attrib='value'>"
        assert len(result.spans) > 0

    def test_json_highlighter(self):
        json_highlighter = JSONHighlighter()
        text = Text('{"key": "value", "number": 123}')
        result = json_highlighter(text)
        assert result.plain == '{"key": "value", "number": 123}'
        assert len(result.spans) > 0

    def test_iso8601_highlighter(self):
        iso8601_highlighter = ISO8601Highlighter()
        text = Text("2023-03-17T01:50:23Z")
        result = iso8601_highlighter(text)
        assert result.plain == "2023-03-17T01:50:23Z"
        assert len(result.spans) > 0

    def test_highlighter_with_string(self):
        null_highlighter = NullHighlighter()
        result = null_highlighter("Hello, World!")
        assert result.plain == "Hello, World!"
        assert result.spans == []

    def test_highlighter_invalid_type(self):
        class TestHighlighter(Highlighter):
            def highlight(self, text: Text) -> None:
                pass

        with pytest.raises(TypeError):
            highlighter = TestHighlighter()
            highlighter(123)