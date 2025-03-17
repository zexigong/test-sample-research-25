import pytest
from twisted.test_failure import Failure, NoCurrentExceptionError, format_frames

def test_format_frames_invalid_detail():
    with pytest.raises(ValueError):
        format_frames([], print, detail="invalid")


def test_format_frames_brief():
    frames = [
        ("func1", "file1", 10, [("var1", "value1")], [("gvar1", "gvalue1")]),
        ("func2", "file2", 20, [("var2", "value2")], [("gvar2", "gvalue2")]),
    ]
    output = []
    format_frames(frames, output.append, detail="brief")
    assert output == ["file1:10:func1\n", "file2:20:func2\n"]


def test_format_frames_default():
    frames = [
        ("func1", "file1", 10, [("var1", "value1")], [("gvar1", "gvalue1")]),
    ]
    output = []
    format_frames(frames, output.append, detail="default")
    assert output[0] == '  File "file1", line 10, in func1\n'


def test_format_frames_verbose():
    frames = [
        ("func1", "file1", 10, [("var1", "value1")], [("gvar1", "gvalue1")]),
    ]
    output = []
    format_frames(frames, output.append, detail="verbose")
    assert "func1(...)\n" in output[0]
    assert "  var1 : 'value1'\n" in output
    assert "  gvar1 : 'gvalue1'\n" in output


def test_format_frames_verbose_vars_not_captured():
    frames = [
        ("func1", "file1", 10, [], []),
    ]
    output = []
    format_frames(frames, output.append, detail="verbose-vars-not-captured")
    assert "func1(...)\n" in output[0]
    assert " [Capture of Locals and Globals disabled" in output[1]


def test_failure_init_no_exception():
    with pytest.raises(NoCurrentExceptionError):
        Failure()


def test_failure_init_with_exception():
    try:
        raise ValueError("test error")
    except ValueError:
        f = Failure()
    assert f.type is ValueError
    assert str(f.value) == "test error"


def test_failure_frames():
    try:
        raise ValueError("test error")
    except ValueError:
        f = Failure()
    assert f.frames[0][0] == "test_failure_frames"


def test_failure_trap():
    try:
        raise ValueError("test error")
    except ValueError:
        f = Failure()
    assert f.trap(ValueError) is ValueError


def test_failure_trap_unexpected():
    try:
        raise ValueError("test error")
    except ValueError:
        f = Failure()
    with pytest.raises(ValueError):
        f.trap(KeyError)


def test_failure_check():
    try:
        raise ValueError("test error")
    except ValueError:
        f = Failure()
    assert f.check(ValueError) is ValueError
    assert f.check(KeyError) is None


def test_failure_raise_exception():
    try:
        raise ValueError("test error")
    except ValueError:
        f = Failure()
    with pytest.raises(ValueError):
        f.raiseException()


def test_failure_repr():
    try:
        raise ValueError("test error")
    except ValueError:
        f = Failure()
    assert "Failure" in repr(f)
    assert "ValueError" in repr(f)


def test_failure_str():
    try:
        raise ValueError("test error")
    except ValueError:
        f = Failure()
    assert "Failure instance" in str(f)


def test_failure_clean_failure():
    try:
        raise ValueError("test error")
    except ValueError:
        f = Failure()
    f.cleanFailure()
    assert f.value.__traceback__ is None


def test_failure_get_traceback_object():
    try:
        raise ValueError("test error")
    except ValueError:
        f = Failure()
    assert f.getTracebackObject() is not None


def test_failure_get_error_message():
    try:
        raise ValueError("test error")
    except ValueError:
        f = Failure()
    assert f.getErrorMessage() == "test error"


def test_failure_get_brief_traceback():
    try:
        raise ValueError("test error")
    except ValueError:
        f = Failure()
    brief_tb = f.getBriefTraceback()
    assert "ValueError" in brief_tb


def test_failure_get_traceback():
    try:
        raise ValueError("test error")
    except ValueError:
        f = Failure()
    tb = f.getTraceback()
    assert "ValueError" in tb


def test_failure_print_traceback(capsys):
    try:
        raise ValueError("test error")
    except ValueError:
        f = Failure()
    f.printTraceback()
    captured = capsys.readouterr()
    assert "ValueError" in captured.out


def test_failure_print_brief_traceback(capsys):
    try:
        raise ValueError("test error")
    except ValueError:
        f = Failure()
    f.printBriefTraceback()
    captured = capsys.readouterr()
    assert "ValueError" in captured.out


def test_failure_print_detailed_traceback(capsys):
    try:
        raise ValueError("test error")
    except ValueError:
        f = Failure()
    f.printDetailedTraceback()
    captured = capsys.readouterr()
    assert "ValueError" in captured.out