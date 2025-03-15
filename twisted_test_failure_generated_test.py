# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.python.failure}.
"""

import os
import sys
import traceback
import types
from collections import namedtuple
from io import StringIO
from typing import List
from unittest import TestCase

import pytest

from twisted.python.failure import Failure, NoCurrentExceptionError, format_frames

try:
    import exceptions

    BaseException = exceptions.BaseException
except ImportError:
    BaseException = object


def assertSubstring(substring, astring, *args):
    """
    Fail if the given substring does not exist within the given string.
    """
    if substring not in astring:
        raise AssertionError(
            f"{substring!r} not in {astring!r} -- {args!r} --"
        )


def assertNotSubstring(substring, astring, *args):
    """
    Fail if the given substring exists within the given string.
    """
    if substring in astring:
        raise AssertionError(
            f"{substring!r} in {astring!r} -- {args!r} --"
        )


class FailureTests(TestCase):
    """
    Tests for L{twisted.python.failure.Failure}.
    """

    def testConstruction(self):
        """
        Test that the constructor captures stack frames.
        """
        f = Failure()
        assert f.frames is not None
        assert len(f.frames) > 0

    def testFailure(self):
        """
        Test that exceptions are instantiated correctly.
        """
        try:
            1 / 0
        except Exception:
            f = Failure()
            assert f.type is ZeroDivisionError
            assert f.value.__class__ is ZeroDivisionError

    def testRaise(self):
        """
        Test that exceptions are raised correctly.
        """
        try:
            1 / 0
        except Exception:
            f = Failure()
            try:
                f.raiseException()
            except Exception as e:
                assert isinstance(e, ZeroDivisionError)
            else:
                assert False, "should have raised"

    def testRaiseExplicit(self):
        """
        Test that explicitly constructed failures can be raised.
        """
        f = Failure(ZeroDivisionError("explicit"))
        try:
            f.raiseException()
        except Exception as e:
            assert isinstance(e, ZeroDivisionError)
        else:
            assert False, "should have raised"

    def testRaiseExplicitInstance(self):
        """
        Test that explicitly constructed failures can be raised.
        """
        f = Failure(ZeroDivisionError("explicit"))
        try:
            f.raiseException()
        except Exception as e:
            assert isinstance(e, ZeroDivisionError)
        else:
            assert False, "should have raised"

    def testRaiseExplicitInstanceNoTrace(self):
        """
        Test that explicitly constructed failures can be raised.
        """
        f = Failure(ZeroDivisionError("explicit"))
        try:
            f.raiseException()
        except Exception as e:
            assert isinstance(e, ZeroDivisionError)
        else:
            assert False, "should have raised"

    def testCopy(self):
        """
        Test that L{Failure} copies can be raised.
        """
        try:
            1 / 0
        except Exception:
            f = Failure()
        g = f.copy()
        try:
            g.raiseException()
        except Exception as e:
            assert isinstance(e, ZeroDivisionError)
        else:
            assert False, "should have raised"

    def testGetTraceback(self):
        """
        Test that tracebacks are formatted correctly.
        """
        try:
            1 / 0
        except Exception:
            f = Failure()
            assertSubstring(
                "ZeroDivisionError",
                f.getTraceback(),
            )

    def testTracebackNoVars(self):
        """
        Test that tracebacks are formatted correctly.
        """
        try:
            1 / 0
        except Exception:
            f = Failure()
            tb = f.getTraceback(detail="verbose")
            assertSubstring(
                "ZeroDivisionError",
                tb,
            )
            assertNotSubstring("Locals", tb)

    def testDetailedTraceback(self):
        """
        Test that detailed tracebacks are formatted correctly.
        """
        try:
            1 / 0
        except Exception:
            f = Failure(captureVars=True)
            tb = f.getTraceback(detail="verbose")
            assertSubstring(
                "ZeroDivisionError",
                tb,
            )
            assertSubstring("Locals", tb)

    def testGetBriefTraceback(self):
        """
        Test that brief tracebacks are formatted correctly.
        """
        try:
            1 / 0
        except Exception:
            f = Failure()
            assertSubstring("ZeroDivisionError", f.getBriefTraceback())

    def testPickle(self):
        """
        Test that L{Failure} can be pickled.
        """
        import pickle

        try:
            1 / 0
        except Exception:
            f = Failure()
        p = pickle.dumps(f)
        f = pickle.loads(p)
        assertSubstring(
            "ZeroDivisionError",
            f.getBriefTraceback(),
        )

    def testPickleWithVars(self):
        """
        Test that L{Failure} can be pickled.
        """
        import pickle

        try:
            1 / 0
        except Exception:
            f = Failure(captureVars=True)
        p = pickle.dumps(f)
        f = pickle.loads(p)
        assertSubstring(
            "ZeroDivisionError",
            f.getBriefTraceback(),
        )

    def testPickleExplicit(self):
        """
        Test that explicitly constructed L{Failure}s can be pickled.
        """
        import pickle

        f = Failure(ZeroDivisionError("explicit"))
        p = pickle.dumps(f)
        f = pickle.loads(p)
        assertSubstring(
            "ZeroDivisionError",
            f.getBriefTraceback(),
        )
        assertSubstring(
            "explicit",
            f.getBriefTraceback(),
        )

    def testPickleExplicitInstance(self):
        """
        Test that explicitly constructed L{Failure}s can be pickled.
        """
        import pickle

        f = Failure(ZeroDivisionError("explicit"))
        p = pickle.dumps(f)
        f = pickle.loads(p)
        assertSubstring(
            "ZeroDivisionError",
            f.getBriefTraceback(),
        )
        assertSubstring(
            "explicit",
            f.getBriefTraceback(),
        )

    def testPickleExplicitInstanceNoTrace(self):
        """
        Test that explicitly constructed L{Failure}s can be pickled.
        """
        import pickle

        f = Failure(ZeroDivisionError("explicit"))
        p = pickle.dumps(f)
        f = pickle.loads(p)
        assertSubstring(
            "ZeroDivisionError",
            f.getBriefTraceback(),
        )
        assertSubstring(
            "explicit",
            f.getBriefTraceback(),
        )

    def testPickleCopy(self):
        """
        Test that L{Failure} copies can be pickled.
        """
        import pickle

        try:
            1 / 0
        except Exception:
            f = Failure()
        g = f.copy()
        p = pickle.dumps(g)
        g = pickle.loads(p)
        assertSubstring(
            "ZeroDivisionError",
            g.getBriefTraceback(),
        )

    def testRaisePickle(self):
        """
        Test that L{Failure} copies can be pickled.
        """
        import pickle

        try:
            1 / 0
        except Exception:
            f = Failure()
        g = f.copy()
        g.cleanFailure()
        p = pickle.dumps(g)
        g = pickle.loads(p)
        try:
            g.raiseException()
        except Exception as e:
            assert isinstance(e, ZeroDivisionError)
        else:
            assert False, "should have raised"

    def testRaisePickleExplicit(self):
        """
        Test that explicitly constructed L{Failure}s can be pickled.
        """
        import pickle

        f = Failure(ZeroDivisionError("explicit"))
        p = pickle.dumps(f)
        f = pickle.loads(p)
        try:
            f.raiseException()
        except Exception as e:
            assert isinstance(e, ZeroDivisionError)
        else:
            assert False, "should have raised"

    def testRaisePickleExplicitInstance(self):
        """
        Test that explicitly constructed L{Failure}s can be pickled.
        """
        import pickle

        f = Failure(ZeroDivisionError("explicit"))
        p = pickle.dumps(f)
        f = pickle.loads(p)
        try:
            f.raiseException()
        except Exception as e:
            assert isinstance(e, ZeroDivisionError)
        else:
            assert False, "should have raised"

    def testRaisePickleExplicitInstanceNoTrace(self):
        """
        Test that explicitly constructed L{Failure}s can be pickled.
        """
        import pickle

        f = Failure(ZeroDivisionError("explicit"))
        p = pickle.dumps(f)
        f = pickle.loads(p)
        try:
            f.raiseException()
        except Exception as e:
            assert isinstance(e, ZeroDivisionError)
        else:
            assert False, "should have raised"

    def testRaisePickleCopy(self):
        """
        Test that L{Failure} copies can be pickled.
        """
        import pickle

        try:
            1 / 0
        except Exception:
            f = Failure()
        g = f.copy()
        p = pickle.dumps(g)
        g = pickle.loads(p)
        try:
            g.raiseException()
        except Exception as e:
            assert isinstance(e, ZeroDivisionError)
        else:
            assert False, "should have raised"

    def testFormatFramesDefault(self):
        """
        Test that L{format_frames} defaults to the expected format.
        """

        frames = [
            ("method1", "file1.py", 1, [], []),
            ("method2", "file2.py", 2, [], []),
        ]
        io = StringIO()
        format_frames(frames, io.write)
        assert io.getvalue() == (
            '  File "file1.py", line 1, in method1\n'
            "    \n"
            '  File "file2.py", line 2, in method2\n'
            "    \n"
        )

    def testFormatFramesBrief(self):
        """
        Test that L{format_frames} produces the expected format.
        """

        frames = [
            ("method1", "file1.py", 1, [], []),
            ("method2", "file2.py", 2, [], []),
        ]
        io = StringIO()
        format_frames(frames, io.write, detail="brief")
        assert io.getvalue() == (
            "file1.py:1:method1\n"
            "file2.py:2:method2\n"
        )

    def testFormatFramesVerbose(self):
        """
        Test that L{format_frames} produces the expected format.
        """

        frames = [
            ("method1", "file1.py", 1, [], []),
            ("method2", "file2.py", 2, [], []),
        ]
        io = StringIO()
        format_frames(frames, io.write, detail="verbose")
        assert io.getvalue() == (
            "file1.py:1: method1(...)\n"
            " [ Locals ]\n"
            " ( Globals )\n"
            "file2.py:2: method2(...)\n"
            " [ Locals ]\n"
            " ( Globals )\n"
        )

    def testFormatFramesVerboseVarsNotCaptured(self):
        """
        Test that L{format_frames} produces the expected format.
        """

        frames = [
            ("method1", "file1.py", 1, [], []),
            ("method2", "file2.py", 2, [], []),
        ]
        io = StringIO()
        format_frames(frames, io.write, detail="verbose-vars-not-captured")
        assert io.getvalue() == (
            "file1.py:1: method1(...)\n"
            "file2.py:2: method2(...)\n"
            " [Capture of Locals and Globals disabled (use captureVars=True)]\n"
        )

    def testFormatFramesInvalidDetail(self):
        """
        Test that L{format_frames} produces the expected format.
        """

        frames = [
            ("method1", "file1.py", 1, [], []),
            ("method2", "file2.py", 2, [], []),
        ]
        io = StringIO()
        with pytest.raises(ValueError):
            format_frames(frames, io.write, detail="invalid")

    def testFormatFramesWithCode(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write)
        assertSubstring(
            '  File "',
            io.getvalue(),
        )
        assertSubstring(
            f", line {frames[0][2]}, in ",
            io.getvalue(),
        )

    def testTrap(self):
        """
        Test that L{Failure.trap} can be used to trap exceptions.
        """
        try:
            1 / 0
        except Exception:
            f = Failure()
        assert f.trap(ZeroDivisionError) is ZeroDivisionError

    def testStringException(self):
        """
        Test that L{Failure} can trap string exceptions.
        """
        try:
            raise "string exception"
        except Exception:
            f = Failure()
        assert f.trap("string exception") == "string exception"

    def testTrapUnexpected(self):
        """
        Test that L{Failure.trap} raises unexpected exceptions.
        """
        try:
            1 / 0
        except Exception:
            f = Failure()
        with pytest.raises(ZeroDivisionError):
            f.trap(NotImplementedError)

    def testStringExceptionTrapUnexpected(self):
        """
        Test that L{Failure.trap} raises unexpected string exceptions.
        """
        try:
            raise "string exception"
        except Exception:
            f = Failure()
        with pytest.raises("string exception"):
            f.trap("string exception 2")

    def testCheck(self):
        """
        Test that L{Failure.check} can be used to check exceptions.
        """
        try:
            1 / 0
        except Exception:
            f = Failure()
        assert f.check(ZeroDivisionError) is ZeroDivisionError

    def testCheckUnexpected(self):
        """
        Test that L{Failure.check} can be used to check unexpected exceptions.
        """
        try:
            1 / 0
        except Exception:
            f = Failure()
        assert f.check(NotImplementedError) is None

    def testCheckStringException(self):
        """
        Test that L{Failure.check} can be used to check string exceptions.
        """
        try:
            raise "string exception"
        except Exception:
            f = Failure()
        assert f.check("string exception") == "string exception"

    def testCheckStringExceptionUnexpected(self):
        """
        Test that L{Failure.check} can be used to check unexpected string
        exceptions.
        """
        try:
            raise "string exception"
        except Exception:
            f = Failure()
        assert f.check("string exception 2") is None

    def testGetErrorMessage(self):
        """
        Test that L{Failure.getErrorMessage} returns the error message.
        """
        try:
            raise RuntimeError("test")
        except Exception:
            f = Failure()
        assert f.getErrorMessage() == "test"

    def testGetErrorMessageMultiLine(self):
        """
        Test that L{Failure.getErrorMessage} returns the error message.
        """
        try:
            raise RuntimeError("test\nfoo")
        except Exception:
            f = Failure()
        assert f.getErrorMessage() == "test\nfoo"

    def testGetErrorMessageUnicode(self):
        """
        Test that L{Failure.getErrorMessage} returns the error message.
        """
        try:
            raise RuntimeError("test \u1234")
        except Exception:
            f = Failure()
        assert f.getErrorMessage() == "test \u1234"

    def testGetErrorMessageUnicodeMultiLine(self):
        """
        Test that L{Failure.getErrorMessage} returns the error message.
        """
        try:
            raise RuntimeError("test \u1234\nfoo")
        except Exception:
            f = Failure()
        assert f.getErrorMessage() == "test \u1234\nfoo"

    def testNoCurrentException(self):
        """
        Test that L{Failure} raises L{NoCurrentExceptionError} when no current
        exception exists.
        """
        with pytest.raises(NoCurrentExceptionError):
            Failure()

    def testCopyWithTB(self):
        """
        Test that L{Failure.copy} copies tracebacks.
        """
        try:
            1 / 0
        except Exception:
            f = Failure()
        assert f.tb is not None
        g = f.copy()
        assert g.tb is not None

    def testCopyWithoutTB(self):
        """
        Test that L{Failure.copy} copies tracebacks.
        """
        try:
            1 / 0
        except Exception:
            f = Failure()
        f.tb = None
        g = f.copy()
        assert g.tb is None

    def testCopyWithFrames(self):
        """
        Test that L{Failure.copy} copies frames.
        """
        try:
            1 / 0
        except Exception:
            f = Failure()
        assert f.frames is not None
        assert len(f.frames) > 0
        g = f.copy()
        assert g.frames is not None
        assert len(g.frames) > 0

    def testCopyWithoutFrames(self):
        """
        Test that L{Failure.copy} copies frames.
        """
        try:
            1 / 0
        except Exception:
            f = Failure()
        f.frames = None
        g = f.copy()
        assert g.frames is None

    def testCopyWithCaptureVars(self):
        """
        Test that L{Failure.copy} copies captureVars.
        """
        try:
            1 / 0
        except Exception:
            f = Failure(captureVars=True)
        assert f.captureVars is True
        g = f.copy()
        assert g.captureVars is True

    def testCopyWithoutCaptureVars(self):
        """
        Test that L{Failure.copy} copies captureVars.
        """
        try:
            1 / 0
        except Exception:
            f = Failure()
        f.captureVars = False
        g = f.copy()
        assert g.captureVars is False

    def testCopyWithValue(self):
        """
        Test that L{Failure.copy} copies value.
        """
        try:
            1 / 0
        except Exception:
            f = Failure()
        assert f.value is not None
        g = f.copy()
        assert g.value is not None

    def testCopyWithoutValue(self):
        """
        Test that L{Failure.copy} copies value.
        """
        try:
            1 / 0
        except Exception:
            f = Failure()
        f.value = None
        g = f.copy()
        assert g.value is None

    def testCopyWithType(self):
        """
        Test that L{Failure.copy} copies type.
        """
        try:
            1 / 0
        except Exception:
            f = Failure()
        assert f.type is ZeroDivisionError
        g = f.copy()
        assert g.type is ZeroDivisionError

    def testCopyWithoutType(self):
        """
        Test that L{Failure.copy} copies type.
        """
        try:
            1 / 0
        except Exception:
            f = Failure()
        f.type = None
        g = f.copy()
        assert g.type is None

    def testCopyWithParents(self):
        """
        Test that L{Failure.copy} copies parents.
        """
        try:
            1 / 0
        except Exception:
            f = Failure()
        assert f.parents is not None
        g = f.copy()
        assert g.parents is not None

    def testCopyWithoutParents(self):
        """
        Test that L{Failure.copy} copies parents.
        """
        try:
            1 / 0
        except Exception:
            f = Failure()
        f.parents = None
        g = f.copy()
        assert g.parents is None

    def testWithoutTraceback(self):
        """
        Test that L{Failure._withoutTraceback} returns a failure without a
        traceback.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))
        assert f.tb is None
        assert f.frames == []

    def testPickleWithoutTraceback(self):
        """
        Test that L{Failure._withoutTraceback} can be pickled.
        """
        import pickle

        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))
        p = pickle.dumps(f)
        f = pickle.loads(p)
        assertSubstring(
            "ZeroDivisionError",
            f.getBriefTraceback(),
        )
        assertSubstring(
            "explicit",
            f.getBriefTraceback(),
        )
        assert f.tb is None
        assert f.frames == []

    def testRaiseWithoutTraceback(self):
        """
        Test that L{Failure._withoutTraceback} can be raised.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))
        try:
            f.raiseException()
        except Exception as e:
            assert isinstance(e, ZeroDivisionError)
        else:
            assert False, "should have raised"

    def testRaisePickleWithoutTraceback(self):
        """
        Test that L{Failure._withoutTraceback} can be pickled and raised.
        """
        import pickle

        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))
        p = pickle.dumps(f)
        f = pickle.loads(p)
        try:
            f.raiseException()
        except Exception as e:
            assert isinstance(e, ZeroDivisionError)
        else:
            assert False, "should have raised"

    def testRaisePickleExplicitWithoutTraceback(self):
        """
        Test that L{Failure._withoutTraceback} can be pickled and raised.
        """
        import pickle

        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))
        p = pickle.dumps(f)
        f = pickle.loads(p)
        try:
            f.raiseException()
        except Exception as e:
            assert isinstance(e, ZeroDivisionError)
        else:
            assert False, "should have raised"

    def testRaisePickleExplicitInstanceWithoutTraceback(self):
        """
        Test that L{Failure._withoutTraceback} can be pickled and raised.
        """
        import pickle

        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))
        p = pickle.dumps(f)
        f = pickle.loads(p)
        try:
            f.raiseException()
        except Exception as e:
            assert isinstance(e, ZeroDivisionError)
        else:
            assert False, "should have raised"

    def testRaisePickleCopyWithoutTraceback(self):
        """
        Test that L{Failure._withoutTraceback} can be pickled and raised.
        """
        import pickle

        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))
        g = f.copy()
        p = pickle.dumps(g)
        g = pickle.loads(p)
        try:
            g.raiseException()
        except Exception as e:
            assert isinstance(e, ZeroDivisionError)
        else:
            assert False, "should have raised"

    def testRaisePickleCopyExplicitWithoutTraceback(self):
        """
        Test that L{Failure._withoutTraceback} can be pickled and raised.
        """
        import pickle

        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))
        g = f.copy()
        p = pickle.dumps(g)
        g = pickle.loads(p)
        try:
            g.raiseException()
        except Exception as e:
            assert isinstance(e, ZeroDivisionError)
        else:
            assert False, "should have raised"

    def testRaisePickleCopyExplicitInstanceWithoutTraceback(self):
        """
        Test that L{Failure._withoutTraceback} can be pickled and raised.
        """
        import pickle

        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))
        g = f.copy()
        p = pickle.dumps(g)
        g = pickle.loads(p)
        try:
            g.raiseException()
        except Exception as e:
            assert isinstance(e, ZeroDivisionError)
        else:
            assert False, "should have raised"

    def testThrowExceptionIntoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} throws the exception
        into the generator and returns the next value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            try:
                yield 1
            except ZeroDivisionError:
                yield 2

        g = generator()
        assert next(g) == 1
        assert f.throwExceptionIntoGenerator(g) == 2

    def testThrowExceptionIntoGeneratorRaises(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises the exception
        into the generator if not caught.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            try:
                yield 1
            except ZeroDivisionError:
                pass

        g = generator()
        assert next(g) == 1
        with pytest.raises(ZeroDivisionError):
            f.throwExceptionIntoGenerator(g)

    def testThrowExceptionIntoGeneratorStopIteration(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} if the generator has no more items.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration):
            f.throwExceptionIntoGenerator(g)

    def testThrowExceptionIntoGeneratorStopIterationRaises(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} if the generator has no more items.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration):
            f.throwExceptionIntoGenerator(g)

    def testThrowExceptionIntoGeneratorReturnValue(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaises(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIteration(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValue(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaises(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValue(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIteration(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValue(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGeneratorNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2

    def testThrowExceptionIntoGeneratorReturnValueRaisesStopIterationNoValueNoRaisesNoReturnValueNoGeneratorNoStopIterationNoReturnValueNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGeneratorNoGenerator(self):
        """
        Test that L{Failure.throwExceptionIntoGenerator} raises
        L{StopIteration} with the return value.
        """
        f = Failure._withoutTraceback(ZeroDivisionError("explicit"))

        def generator():
            yield 1
            return 2

        g = generator()
        assert next(g) == 1
        with pytest.raises(StopIteration) as excinfo:
            f.throwExceptionIntoGenerator(g)
        assert excinfo.value.value == 2


class FormatFramesTests(TestCase):
    """
    Tests for L{twisted.python.failure.format_frames}.
    """

    def testDefault(self):
        """
        Test that L{format_frames} defaults to the expected format.
        """
        frames = [
            ("method1", "file1.py", 1, [], []),
            ("method2", "file2.py", 2, [], []),
        ]
        io = StringIO()
        format_frames(frames, io.write)
        assert io.getvalue() == (
            '  File "file1.py", line 1, in method1\n'
            "    \n"
            '  File "file2.py", line 2, in method2\n'
            "    \n"
        )

    def testBrief(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        frames = [
            ("method1", "file1.py", 1, [], []),
            ("method2", "file2.py", 2, [], []),
        ]
        io = StringIO()
        format_frames(frames, io.write, detail="brief")
        assert io.getvalue() == (
            "file1.py:1:method1\n"
            "file2.py:2:method2\n"
        )

    def testVerbose(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        frames = [
            ("method1", "file1.py", 1, [], []),
            ("method2", "file2.py", 2, [], []),
        ]
        io = StringIO()
        format_frames(frames, io.write, detail="verbose")
        assert io.getvalue() == (
            "file1.py:1: method1(...)\n"
            " [ Locals ]\n"
            " ( Globals )\n"
            "file2.py:2: method2(...)\n"
            " [ Locals ]\n"
            " ( Globals )\n"
        )

    def testVerboseVarsNotCaptured(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        frames = [
            ("method1", "file1.py", 1, [], []),
            ("method2", "file2.py", 2, [], []),
        ]
        io = StringIO()
        format_frames(frames, io.write, detail="verbose-vars-not-captured")
        assert io.getvalue() == (
            "file1.py:1: method1(...)\n"
            "file2.py:2: method2(...)\n"
            " [Capture of Locals and Globals disabled (use captureVars=True)]\n"
        )

    def testInvalidDetail(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        frames = [
            ("method1", "file1.py", 1, [], []),
            ("method2", "file2.py", 2, [], []),
        ]
        io = StringIO()
        with pytest.raises(ValueError):
            format_frames(frames, io.write, detail="invalid")

    def testWithCode(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write)
        assertSubstring(
            '  File "',
            io.getvalue(),
        )
        assertSubstring(
            f", line {frames[0][2]}, in ",
            io.getvalue(),
        )


class FormatFramesWithCodeTests(TestCase):
    """
    Tests for L{twisted.python.failure.format_frames} with code.
    """

    def testDefault(self):
        """
        Test that L{format_frames} defaults to the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write)
        assertSubstring(
            '  File "',
            io.getvalue(),
        )
        assertSubstring(
            f", line {frames[0][2]}, in ",
            io.getvalue(),
        )

    def testBrief(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write, detail="brief")
        assertSubstring(
            "test_failure.py:",
            io.getvalue(),
        )
        assertSubstring(
            f":{frames[0][2]}:",
            io.getvalue(),
        )

    def testVerbose(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write, detail="verbose")
        assertSubstring(
            "test_failure.py:",
            io.getvalue(),
        )
        assertSubstring(
            f":{frames[0][2]}: ",
            io.getvalue(),
        )

    def testVerboseVarsNotCaptured(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write, detail="verbose-vars-not-captured")
        assertSubstring(
            "test_failure.py:",
            io.getvalue(),
        )
        assertSubstring(
            f":{frames[0][2]}: ",
            io.getvalue(),
        )

    def testInvalidDetail(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        with pytest.raises(ValueError):
            format_frames(frames, io.write, detail="invalid")

    def testWithCode(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write)
        assertSubstring(
            '  File "',
            io.getvalue(),
        )
        assertSubstring(
            f", line {frames[0][2]}, in ",
            io.getvalue(),
        )


class FormatFramesWithCodeVerboseTests(TestCase):
    """
    Tests for L{twisted.python.failure.format_frames} with code.
    """

    def testDefault(self):
        """
        Test that L{format_frames} defaults to the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write)
        assertSubstring(
            '  File "',
            io.getvalue(),
        )
        assertSubstring(
            f", line {frames[0][2]}, in ",
            io.getvalue(),
        )

    def testBrief(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write, detail="brief")
        assertSubstring(
            "test_failure.py:",
            io.getvalue(),
        )
        assertSubstring(
            f":{frames[0][2]}:",
            io.getvalue(),
        )

    def testVerbose(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write, detail="verbose")
        assertSubstring(
            "test_failure.py:",
            io.getvalue(),
        )
        assertSubstring(
            f":{frames[0][2]}: ",
            io.getvalue(),
        )

    def testVerboseVarsNotCaptured(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write, detail="verbose-vars-not-captured")
        assertSubstring(
            "test_failure.py:",
            io.getvalue(),
        )
        assertSubstring(
            f":{frames[0][2]}: ",
            io.getvalue(),
        )

    def testInvalidDetail(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        with pytest.raises(ValueError):
            format_frames(frames, io.write, detail="invalid")

    def testWithCode(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write)
        assertSubstring(
            '  File "',
            io.getvalue(),
        )
        assertSubstring(
            f", line {frames[0][2]}, in ",
            io.getvalue(),
        )


class FormatFramesWithCodeVerboseVarsNotCapturedTests(TestCase):
    """
    Tests for L{twisted.python.failure.format_frames} with code.
    """

    def testDefault(self):
        """
        Test that L{format_frames} defaults to the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write)
        assertSubstring(
            '  File "',
            io.getvalue(),
        )
        assertSubstring(
            f", line {frames[0][2]}, in ",
            io.getvalue(),
        )

    def testBrief(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write, detail="brief")
        assertSubstring(
            "test_failure.py:",
            io.getvalue(),
        )
        assertSubstring(
            f":{frames[0][2]}:",
            io.getvalue(),
        )

    def testVerbose(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write, detail="verbose")
        assertSubstring(
            "test_failure.py:",
            io.getvalue(),
        )
        assertSubstring(
            f":{frames[0][2]}: ",
            io.getvalue(),
        )

    def testVerboseVarsNotCaptured(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write, detail="verbose-vars-not-captured")
        assertSubstring(
            "test_failure.py:",
            io.getvalue(),
        )
        assertSubstring(
            f":{frames[0][2]}: ",
            io.getvalue(),
        )

    def testInvalidDetail(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        with pytest.raises(ValueError):
            format_frames(frames, io.write, detail="invalid")

    def testWithCode(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write)
        assertSubstring(
            '  File "',
            io.getvalue(),
        )
        assertSubstring(
            f", line {frames[0][2]}, in ",
            io.getvalue(),
        )


class FormatFramesWithCodeInvalidDetailTests(TestCase):
    """
    Tests for L{twisted.python.failure.format_frames} with code.
    """

    def testDefault(self):
        """
        Test that L{format_frames} defaults to the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write)
        assertSubstring(
            '  File "',
            io.getvalue(),
        )
        assertSubstring(
            f", line {frames[0][2]}, in ",
            io.getvalue(),
        )

    def testBrief(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write, detail="brief")
        assertSubstring(
            "test_failure.py:",
            io.getvalue(),
        )
        assertSubstring(
            f":{frames[0][2]}:",
            io.getvalue(),
        )

    def testVerbose(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write, detail="verbose")
        assertSubstring(
            "test_failure.py:",
            io.getvalue(),
        )
        assertSubstring(
            f":{frames[0][2]}: ",
            io.getvalue(),
        )

    def testVerboseVarsNotCaptured(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write, detail="verbose-vars-not-captured")
        assertSubstring(
            "test_failure.py:",
            io.getvalue(),
        )
        assertSubstring(
            f":{frames[0][2]}: ",
            io.getvalue(),
        )

    def testInvalidDetail(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        with pytest.raises(ValueError):
            format_frames(frames, io.write, detail="invalid")

    def testWithCode(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write)
        assertSubstring(
            '  File "',
            io.getvalue(),
        )
        assertSubstring(
            f", line {frames[0][2]}, in ",
            io.getvalue(),
        )


class FormatFramesWithCodeInvalidDetailWithCodeTests(TestCase):
    """
    Tests for L{twisted.python.failure.format_frames} with code.
    """

    def testDefault(self):
        """
        Test that L{format_frames} defaults to the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write)
        assertSubstring(
            '  File "',
            io.getvalue(),
        )
        assertSubstring(
            f", line {frames[0][2]}, in ",
            io.getvalue(),
        )

    def testBrief(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write, detail="brief")
        assertSubstring(
            "test_failure.py:",
            io.getvalue(),
        )
        assertSubstring(
            f":{frames[0][2]}:",
            io.getvalue(),
        )

    def testVerbose(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write, detail="verbose")
        assertSubstring(
            "test_failure.py:",
            io.getvalue(),
        )
        assertSubstring(
            f":{frames[0][2]}: ",
            io.getvalue(),
        )

    def testVerboseVarsNotCaptured(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write, detail="verbose-vars-not-captured")
        assertSubstring(
            "test_failure.py:",
            io.getvalue(),
        )
        assertSubstring(
            f":{frames[0][2]}: ",
            io.getvalue(),
        )

    def testInvalidDetail(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        with pytest.raises(ValueError):
            format_frames(frames, io.write, detail="invalid")

    def testWithCode(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write)
        assertSubstring(
            '  File "',
            io.getvalue(),
        )
        assertSubstring(
            f", line {frames[0][2]}, in ",
            io.getvalue(),
        )


class FormatFramesWithCodeInvalidDetailWithCodeVerboseTests(TestCase):
    """
    Tests for L{twisted.python.failure.format_frames} with code.
    """

    def testDefault(self):
        """
        Test that L{format_frames} defaults to the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write)
        assertSubstring(
            '  File "',
            io.getvalue(),
        )
        assertSubstring(
            f", line {frames[0][2]}, in ",
            io.getvalue(),
        )

    def testBrief(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write, detail="brief")
        assertSubstring(
            "test_failure.py:",
            io.getvalue(),
        )
        assertSubstring(
            f":{frames[0][2]}:",
            io.getvalue(),
        )

    def testVerbose(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write, detail="verbose")
        assertSubstring(
            "test_failure.py:",
            io.getvalue(),
        )
        assertSubstring(
            f":{frames[0][2]}: ",
            io.getvalue(),
        )

    def testVerboseVarsNotCaptured(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write, detail="verbose-vars-not-captured")
        assertSubstring(
            "test_failure.py:",
            io.getvalue(),
        )
        assertSubstring(
            f":{frames[0][2]}: ",
            io.getvalue(),
        )

    def testInvalidDetail(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        with pytest.raises(ValueError):
            format_frames(frames, io.write, detail="invalid")

    def testWithCode(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write)
        assertSubstring(
            '  File "',
            io.getvalue(),
        )
        assertSubstring(
            f", line {frames[0][2]}, in ",
            io.getvalue(),
        )


class FormatFramesWithCodeInvalidDetailWithCodeVerboseVarsNotCapturedTests(TestCase):
    """
    Tests for L{twisted.python.failure.format_frames} with code.
    """

    def testDefault(self):
        """
        Test that L{format_frames} defaults to the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write)
        assertSubstring(
            '  File "',
            io.getvalue(),
        )
        assertSubstring(
            f", line {frames[0][2]}, in ",
            io.getvalue(),
        )

    def testBrief(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write, detail="brief")
        assertSubstring(
            "test_failure.py:",
            io.getvalue(),
        )
        assertSubstring(
            f":{frames[0][2]}:",
            io.getvalue(),
        )

    def testVerbose(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write, detail="verbose")
        assertSubstring(
            "test_failure.py:",
            io.getvalue(),
        )
        assertSubstring(
            f":{frames[0][2]}: ",
            io.getvalue(),
        )

    def testVerboseVarsNotCaptured(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write, detail="verbose-vars-not-captured")
        assertSubstring(
            "test_failure.py:",
            io.getvalue(),
        )
        assertSubstring(
            f":{frames[0][2]}: ",
            io.getvalue(),
        )

    def testInvalidDetail(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        with pytest.raises(ValueError):
            format_frames(frames, io.write, detail="invalid")

    def testWithCode(self):
        """
        Test that L{format_frames} produces the expected format.
        """
        f = Failure()
        frames = f.frames
        io = StringIO()
        format_frames(frames, io.write)
        assertSubstring(
            '  File "',
            io.getvalue(),
        )
        assertSubstring(
            f", line {frames[0][2]}, in ",
            io.getvalue(),
        )