# -*- test-case-name: twisted.test.test_failure -*-
# See also test suite twisted.test.test_pbfailure

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.python.failure}.
"""

import sys
import traceback
from typing import List, Optional, Type

from twisted.python.failure import Failure, DefaultException, NoCurrentExceptionError
from twisted.trial import unittest
from twisted.trial.unittest import TestCase


class LeafException(Exception):
    """
    A leaf in the exception hierarchy.
    """


class BranchException(LeafException):
    """
    A branch in the exception hierarchy.
    """


class FailureTestCase(TestCase):
    def assertStartsWith(self, first: str, second: str) -> None:
        """
        Fail if C{first} does not start with C{second}.
        """
        if not first.startswith(second):
            raise self.failureException(f"{first!r} does not start with {second!r}")

    def testDefaultArgs(self) -> None:
        """
        If no arguments are passed to L{Failure.__init__}, it will use the
        information from the current exception.
        """
        try:
            1 // 0
        except:
            f = Failure()
        self.assertEqual(f.type, ZeroDivisionError)

    def testNoCurrentException(self) -> None:
        """
        L{Failure.__init__} raises L{NoCurrentExceptionError} if there is no
        current exception state and no exception instance is passed to it.
        """
        self.assertRaises(NoCurrentExceptionError, Failure)

    def testGetTraceback(self) -> None:
        """
        L{Failure.getTraceback} returns a string starting with C{"Traceback"}
        and ending with the error message.
        """
        try:
            1 // 0
        except:
            f = Failure()
        traceback = f.getTraceback()
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("in testGetTraceback\n1 // 0\nZeroDivisionError: division by zero\n"))

    def testGetTracebackWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns the string representation of the
        wrapped L{Failure} if the exception is a L{Failure}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        traceback = g.getTraceback()
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("in testGetTracebackWithFailure\n1 // 0\nZeroDivisionError: division by zero\n"))

    def testGetBriefTraceback(self) -> None:
        """
        L{Failure.getBriefTraceback} returns a string starting with C{"Traceback"}
        and ending with the error message.
        """
        try:
            1 // 0
        except:
            f = Failure()
        traceback = f.getBriefTraceback()
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("ZeroDivisionError: division by zero\n"))

    def testGetBriefTracebackWithFailure(self) -> None:
        """
        L{Failure.getBriefTraceback} returns the string representation of the
        wrapped L{Failure} if the exception is a L{Failure}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        traceback = g.getBriefTraceback()
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("ZeroDivisionError: division by zero\n"))

    def testGetTracebackObject(self) -> None:
        """
        L{Failure.getTracebackObject} returns a traceback object that can be
        passed to L{traceback.extract_tb}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        tb = f.getTracebackObject()
        self.assertEqual(traceback.extract_tb(tb), traceback.extract_tb(sys.exc_info()[2]))

    def testGetTracebackObjectWithFailure(self) -> None:
        """
        L{Failure.getTracebackObject} returns a fake traceback object if the
        exception is a L{Failure} and no traceback object is present.
        """
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        tb = g.getTracebackObject()
        self.assertEqual(traceback.extract_tb(tb), traceback.extract_tb(sys.exc_info()[2]))

    def testNoFrames(self) -> None:
        """
        L{Failure.frames} is an empty list if no frames are captured.
        """
        try:
            1 // 0
        except:
            f = Failure()
        f.frames = []
        self.assertEqual(f.frames, [])

    def testNoFramesWithFailure(self) -> None:
        """
        L{Failure.frames} is an empty list if no frames are captured and the
        exception is a L{Failure}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        g.frames = []
        self.assertEqual(g.frames, [])

    def testNoParents(self) -> None:
        """
        L{Failure.parents} is an empty list if no frames are captured.
        """
        try:
            1 // 0
        except:
            f = Failure()
        f.parents = []
        self.assertEqual(f.parents, [])

    def testNoParentsWithFailure(self) -> None:
        """
        L{Failure.parents} is an empty list if no frames are captured and the
        exception is a L{Failure}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        g.parents = []
        self.assertEqual(g.parents, [])

    def testThrowExceptionIntoGenerator(self) -> None:
        """
        L{Failure.throwExceptionIntoGenerator} throws the exception into the
        generator and returns the next yielded value.
        """
        def generator() -> int:
            try:
                yield 1
            except ZeroDivisionError:
                yield 2
            yield 3
        gen = generator()
        try:
            1 // 0
        except:
            f = Failure()
        next(gen)
        self.assertEqual(f.throwExceptionIntoGenerator(gen), 2)
        self.assertEqual(next(gen), 3)
        self.assertRaises(StopIteration, next, gen)

    def testThrowExceptionIntoGeneratorWithFailure(self) -> None:
        """
        L{Failure.throwExceptionIntoGenerator} throws the exception into the
        generator and returns the next yielded value if the exception is a
        L{Failure}.
        """
        def generator() -> int:
            try:
                yield 1
            except ZeroDivisionError:
                yield 2
            yield 3
        gen = generator()
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        next(gen)
        self.assertEqual(g.throwExceptionIntoGenerator(gen), 2)
        self.assertEqual(next(gen), 3)
        self.assertRaises(StopIteration, next, gen)

    def testCleanFailure(self) -> None:
        """
        L{Failure.cleanFailure} removes references to other objects and sets
        C{__traceback__} to C{None}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        f.cleanFailure()
        self.assertIsNone(f.tb)
        self.assertIsNone(f.value.__traceback__)

    def testCleanFailureWithFailure(self) -> None:
        """
        L{Failure.cleanFailure} removes references to other objects and sets
        C{__traceback__} to C{None} if the exception is a L{Failure}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        g.cleanFailure()
        self.assertIsNone(g.tb)
        self.assertIsNone(g.value.__traceback__)

    def testFramesCaptureVars(self) -> None:
        """
        L{Failure.frames} captures local and global variables if C{captureVars}
        is C{True}.
        """
        try:
            1 // 0
        except:
            f = Failure(captureVars=True)
        frames = f.frames
        self.assertEqual(frames[0][3], list(locals().items()))
        self.assertEqual(frames[0][4], list(globals().items()))

    def testFramesCaptureVarsWithFailure(self) -> None:
        """
        L{Failure.frames} captures local and global variables if C{captureVars}
        is C{True} and the exception is a L{Failure}.
        """
        try:
            1 // 0
        except:
            f = Failure(captureVars=True)
        g = Failure(f)
        frames = g.frames
        self.assertEqual(frames[0][3], list(locals().items()))
        self.assertEqual(frames[0][4], list(globals().items()))

    def testGetErrorMessage(self) -> None:
        """
        L{Failure.getErrorMessage} returns the error message of the exception.
        """
        try:
            1 // 0
        except:
            f = Failure()
        self.assertEqual(f.getErrorMessage(), "division by zero")

    def testGetErrorMessageWithFailure(self) -> None:
        """
        L{Failure.getErrorMessage} returns the error message of the exception
        if the exception is a L{Failure}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        self.assertEqual(g.getErrorMessage(), "division by zero")

    def testCheck(self) -> None:
        """
        L{Failure.check} returns the exception type if the exception is an
        instance of any of the given types.
        """
        try:
            1 // 0
        except:
            f = Failure()
        self.assertEqual(f.check(ZeroDivisionError, ValueError), ZeroDivisionError)

    def testCheckWithFailure(self) -> None:
        """
        L{Failure.check} returns the exception type if the exception is an
        instance of any of the given types and the exception is a L{Failure}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        self.assertEqual(g.check(ZeroDivisionError, ValueError), ZeroDivisionError)

    def testTrap(self) -> None:
        """
        L{Failure.trap} raises the exception if the exception is not an
        instance of any of the given types.
        """
        try:
            1 // 0
        except:
            f = Failure()
        self.assertEqual(f.trap(ZeroDivisionError, ValueError), ZeroDivisionError)
        self.assertRaises(ZeroDivisionError, f.trap, ValueError)

    def testTrapWithFailure(self) -> None:
        """
        L{Failure.trap} raises the exception if the exception is not an
        instance of any of the given types and the exception is a L{Failure}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        self.assertEqual(g.trap(ZeroDivisionError, ValueError), ZeroDivisionError)
        self.assertRaises(ZeroDivisionError, g.trap, ValueError)

    def testRaiseException(self) -> None:
        """
        L{Failure.raiseException} raises the exception.
        """
        try:
            1 // 0
        except:
            f = Failure()
        self.assertRaises(ZeroDivisionError, f.raiseException)

    def testRaiseExceptionWithFailure(self) -> None:
        """
        L{Failure.raiseException} raises the exception if the exception is a
        L{Failure}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        self.assertRaises(ZeroDivisionError, g.raiseException)

    def testGetTracebackWithDetail(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level.
        """
        try:
            1 // 0
        except:
            f = Failure()
        traceback = f.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("ZeroDivisionError: division by zero\n"))

    def testGetTracebackWithDetailWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level if
        the exception is a L{Failure}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        traceback = g.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("ZeroDivisionError: division by zero\n"))

    def testGetTracebackWithDetailAndFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        traceback = g.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("ZeroDivisionError: division by zero\n"))

    def testGetTracebackWithDetailAndFailureWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure} and the exception is a L{Failure}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        traceback = h.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("ZeroDivisionError: division by zero\n"))

    def testGetTracebackWithDetailAndFailureWithFailureWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure} and the exception is a L{Failure} and
        the exception is a L{Failure}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        traceback = i.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("ZeroDivisionError: division by zero\n"))

    def testGetTracebackWithDetailAndFailureWithFailureWithFailureWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure} and the exception is a L{Failure} and
        the exception is a L{Failure} and the exception is a L{Failure}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        traceback = j.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("ZeroDivisionError: division by zero\n"))

    def testGetTracebackWithDetailAndFailureWithFailureWithFailureWithFailureWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure} and the exception is a L{Failure} and
        the exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        traceback = k.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("ZeroDivisionError: division by zero\n"))

    def testGetTracebackWithDetailAndFailureWithFailureWithFailureWithFailureWithFailureWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure} and the exception is a L{Failure} and
        the exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        l = Failure(k)
        traceback = l.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("ZeroDivisionError: division by zero\n"))

    def testGetTracebackWithDetailAndFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure} and the exception is a L{Failure} and
        the exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        l = Failure(k)
        m = Failure(l)
        traceback = m.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("ZeroDivisionError: division by zero\n"))

    def testGetTracebackWithDetailAndFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure} and the exception is a L{Failure} and
        the exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        l = Failure(k)
        m = Failure(l)
        n = Failure(m)
        traceback = n.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("ZeroDivisionError: division by zero\n"))

    def testGetTracebackWithDetailAndFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure} and the exception is a L{Failure} and
        the exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        l = Failure(k)
        m = Failure(l)
        n = Failure(m)
        o = Failure(n)
        traceback = o.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("ZeroDivisionError: division by zero\n"))

    def testGetTracebackWithDetailAndFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure} and the exception is a L{Failure} and
        the exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        l = Failure(k)
        m = Failure(l)
        n = Failure(m)
        o = Failure(n)
        p = Failure(o)
        traceback = p.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("ZeroDivisionError: division by zero\n"))

    def testGetTracebackWithDetailAndFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure} and the exception is a L{Failure} and
        the exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure}.
        """
        try:
            1 // 0
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        l = Failure(k)
        m = Failure(l)
        n = Failure(m)
        o = Failure(n)
        p = Failure(o)
        q = Failure(p)
        traceback = q.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("ZeroDivisionError: division by zero\n"))


class FailureTests(unittest.TestCase):
    """
    Tests for L{twisted.python.failure.Failure}.
    """

    def setUp(self) -> None:
        """
        Create a new L{Failure} with a new exception type for testing.
        """
        self.error = Exception("test error")
        self.failure = Failure(self.error)

    def testGetTraceback(self) -> None:
        """
        L{Failure.getTraceback} returns a string starting with C{"Traceback"}
        and ending with the error message.
        """
        traceback = self.failure.getTraceback()
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("Exception: test error\n"))

    def testGetTracebackWithDetail(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level.
        """
        traceback = self.failure.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("Exception: test error\n"))

    def testGetTracebackWithDetailAndFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure}.
        """
        f = Failure(self.failure)
        traceback = f.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("Exception: test error\n"))

    def testGetTracebackWithDetailAndFailureWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure} and the exception is a L{Failure}.
        """
        f = Failure(self.failure)
        g = Failure(f)
        traceback = g.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("Exception: test error\n"))

    def testGetTracebackWithDetailAndFailureWithFailureWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure} and the exception is a L{Failure} and
        the exception is a L{Failure}.
        """
        f = Failure(self.failure)
        g = Failure(f)
        h = Failure(g)
        traceback = h.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("Exception: test error\n"))

    def testGetTracebackWithDetailAndFailureWithFailureWithFailureWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure} and the exception is a L{Failure} and
        the exception is a L{Failure} and the exception is a L{Failure}.
        """
        f = Failure(self.failure)
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        traceback = i.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("Exception: test error\n"))

    def testGetTracebackWithDetailAndFailureWithFailureWithFailureWithFailureWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure} and the exception is a L{Failure} and
        the exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure}.
        """
        f = Failure(self.failure)
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        traceback = j.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("Exception: test error\n"))

    def testGetTracebackWithDetailAndFailureWithFailureWithFailureWithFailureWithFailureWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure} and the exception is a L{Failure} and
        the exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure}.
        """
        f = Failure(self.failure)
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        traceback = k.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("Exception: test error\n"))

    def testGetTracebackWithDetailAndFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure} and the exception is a L{Failure} and
        the exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure}.
        """
        f = Failure(self.failure)
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        l = Failure(k)
        traceback = l.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("Exception: test error\n"))

    def testGetTracebackWithDetailAndFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure} and the exception is a L{Failure} and
        the exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure}.
        """
        f = Failure(self.failure)
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        l = Failure(k)
        m = Failure(l)
        traceback = m.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("Exception: test error\n"))

    def testGetTracebackWithDetailAndFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure} and the exception is a L{Failure} and
        the exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure}.
        """
        f = Failure(self.failure)
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        l = Failure(k)
        m = Failure(l)
        n = Failure(m)
        traceback = n.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("Exception: test error\n"))

    def testGetTracebackWithDetailAndFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure} and the exception is a L{Failure} and
        the exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure}.
        """
        f = Failure(self.failure)
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        l = Failure(k)
        m = Failure(l)
        n = Failure(m)
        o = Failure(n)
        traceback = o.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("Exception: test error\n"))

    def testGetTracebackWithDetailAndFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure} and the exception is a L{Failure} and
        the exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure}.
        """
        f = Failure(self.failure)
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        l = Failure(k)
        m = Failure(l)
        n = Failure(m)
        o = Failure(n)
        p = Failure(o)
        traceback = p.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("Exception: test error\n"))

    def testGetTracebackWithDetailAndFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailure(self) -> None:
        """
        L{Failure.getTraceback} returns a string with the given detail level
        and the exception is a L{Failure} and the exception is a L{Failure} and
        the exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure} and the exception is a L{Failure}.
        """
        f = Failure(self.failure)
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        l = Failure(k)
        m = Failure(l)
        n = Failure(m)
        o = Failure(n)
        p = Failure(o)
        q = Failure(p)
        traceback = q.getTraceback(detail="brief")
        self.assertStartsWith(traceback, "Traceback")
        self.assertTrue(traceback.endswith("Exception: test error\n"))


class FormatFramesTests(unittest.TestCase):
    """
    Tests for L{twisted.python.failure.format_frames}.
    """

    def testFormatFrames(self) -> None:
        """
        L{twisted.python.failure.format_frames} formats frames in different
        levels of detail.
        """
        exc = Exception("test exception")
        try:
            raise exc
        except:
            f = Failure()
        frames = f.frames

        def check(detail: str, expected: str) -> None:
            io = StringIO()
            f.printTraceback(file=io, detail=detail)
            self.assertEqual(io.getvalue(), expected)

        default = (
            "Traceback (most recent call last):\n"
            '  File "twisted/test/test_failure.py", line 20, in testFormatFrames\n'
            "    raise exc\n"
            "Exception: test exception\n"
        )
        brief = (
            "Traceback: twisted/test/test_failure.py:20:testFormatFrames\n"
            "Exception: test exception\n"
        )
        verbose = (
            "*--- Failure #1 ---\n"
            "twisted/test/test_failure.py:20: testFormatFrames(...)\n"
            " [ Locals ]\n"
            "  exc : Exception('test exception')\n"
            " ( Globals )\n"
            "*--- End of Failure #1 ---\n"
        )

        check("default", default)
        check("brief", brief)
        check("verbose", verbose)


class FormatFramesWithFailureTests(unittest.TestCase):
    """
    Tests for L{twisted.python.failure.format_frames} when the exception is a
    L{Failure}.
    """

    def testFormatFrames(self) -> None:
        """
        L{twisted.python.failure.format_frames} formats frames in different
        levels of detail when the exception is a L{Failure}.
        """
        exc = Exception("test exception")
        try:
            raise exc
        except:
            f = Failure()
        g = Failure(f)
        frames = g.frames

        def check(detail: str, expected: str) -> None:
            io = StringIO()
            f.printTraceback(file=io, detail=detail)
            self.assertEqual(io.getvalue(), expected)

        default = (
            "Traceback (most recent call last):\n"
            '  File "twisted/test/test_failure.py", line 20, in testFormatFrames\n'
            "    raise exc\n"
            "Exception: test exception\n"
        )
        brief = (
            "Traceback: twisted/test/test_failure.py:20:testFormatFrames\n"
            "Exception: test exception\n"
        )
        verbose = (
            "*--- Failure #1 ---\n"
            "twisted/test/test_failure.py:20: testFormatFrames(...)\n"
            " [ Locals ]\n"
            "  exc : Exception('test exception')\n"
            " ( Globals )\n"
            "*--- End of Failure #1 ---\n"
        )

        check("default", default)
        check("brief", brief)
        check("verbose", verbose)


class FormatFramesWithFailureWithFailureTests(unittest.TestCase):
    """
    Tests for L{twisted.python.failure.format_frames} when the exception is a
    L{Failure} and the exception is a L{Failure}.
    """

    def testFormatFrames(self) -> None:
        """
        L{twisted.python.failure.format_frames} formats frames in different
        levels of detail when the exception is a L{Failure} and the exception
        is a L{Failure}.
        """
        exc = Exception("test exception")
        try:
            raise exc
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        frames = h.frames

        def check(detail: str, expected: str) -> None:
            io = StringIO()
            f.printTraceback(file=io, detail=detail)
            self.assertEqual(io.getvalue(), expected)

        default = (
            "Traceback (most recent call last):\n"
            '  File "twisted/test/test_failure.py", line 20, in testFormatFrames\n'
            "    raise exc\n"
            "Exception: test exception\n"
        )
        brief = (
            "Traceback: twisted/test/test_failure.py:20:testFormatFrames\n"
            "Exception: test exception\n"
        )
        verbose = (
            "*--- Failure #1 ---\n"
            "twisted/test/test_failure.py:20: testFormatFrames(...)\n"
            " [ Locals ]\n"
            "  exc : Exception('test exception')\n"
            " ( Globals )\n"
            "*--- End of Failure #1 ---\n"
        )

        check("default", default)
        check("brief", brief)
        check("verbose", verbose)


class FormatFramesWithFailureWithFailureWithFailureTests(unittest.TestCase):
    """
    Tests for L{twisted.python.failure.format_frames} when the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure}.
    """

    def testFormatFrames(self) -> None:
        """
        L{twisted.python.failure.format_frames} formats frames in different
        levels of detail when the exception is a L{Failure} and the exception
        is a L{Failure} and the exception is a L{Failure}.
        """
        exc = Exception("test exception")
        try:
            raise exc
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        frames = i.frames

        def check(detail: str, expected: str) -> None:
            io = StringIO()
            f.printTraceback(file=io, detail=detail)
            self.assertEqual(io.getvalue(), expected)

        default = (
            "Traceback (most recent call last):\n"
            '  File "twisted/test/test_failure.py", line 20, in testFormatFrames\n'
            "    raise exc\n"
            "Exception: test exception\n"
        )
        brief = (
            "Traceback: twisted/test/test_failure.py:20:testFormatFrames\n"
            "Exception: test exception\n"
        )
        verbose = (
            "*--- Failure #1 ---\n"
            "twisted/test/test_failure.py:20: testFormatFrames(...)\n"
            " [ Locals ]\n"
            "  exc : Exception('test exception')\n"
            " ( Globals )\n"
            "*--- End of Failure #1 ---\n"
        )

        check("default", default)
        check("brief", brief)
        check("verbose", verbose)


class FormatFramesWithFailureWithFailureWithFailureWithFailureTests(unittest.TestCase):
    """
    Tests for L{twisted.python.failure.format_frames} when the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure}.
    """

    def testFormatFrames(self) -> None:
        """
        L{twisted.python.failure.format_frames} formats frames in different
        levels of detail when the exception is a L{Failure} and the exception
        is a L{Failure} and the exception is a L{Failure} and the exception is
        a L{Failure}.
        """
        exc = Exception("test exception")
        try:
            raise exc
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        frames = j.frames

        def check(detail: str, expected: str) -> None:
            io = StringIO()
            f.printTraceback(file=io, detail=detail)
            self.assertEqual(io.getvalue(), expected)

        default = (
            "Traceback (most recent call last):\n"
            '  File "twisted/test/test_failure.py", line 20, in testFormatFrames\n'
            "    raise exc\n"
            "Exception: test exception\n"
        )
        brief = (
            "Traceback: twisted/test/test_failure.py:20:testFormatFrames\n"
            "Exception: test exception\n"
        )
        verbose = (
            "*--- Failure #1 ---\n"
            "twisted/test/test_failure.py:20: testFormatFrames(...)\n"
            " [ Locals ]\n"
            "  exc : Exception('test exception')\n"
            " ( Globals )\n"
            "*--- End of Failure #1 ---\n"
        )

        check("default", default)
        check("brief", brief)
        check("verbose", verbose)


class FormatFramesWithFailureWithFailureWithFailureWithFailureWithFailureTests(unittest.TestCase):
    """
    Tests for L{twisted.python.failure.format_frames} when the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure}.
    """

    def testFormatFrames(self) -> None:
        """
        L{twisted.python.failure.format_frames} formats frames in different
        levels of detail when the exception is a L{Failure} and the exception
        is a L{Failure} and the exception is a L{Failure} and the exception is
        a L{Failure} and the exception is a L{Failure}.
        """
        exc = Exception("test exception")
        try:
            raise exc
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        frames = k.frames

        def check(detail: str, expected: str) -> None:
            io = StringIO()
            f.printTraceback(file=io, detail=detail)
            self.assertEqual(io.getvalue(), expected)

        default = (
            "Traceback (most recent call last):\n"
            '  File "twisted/test/test_failure.py", line 20, in testFormatFrames\n'
            "    raise exc\n"
            "Exception: test exception\n"
        )
        brief = (
            "Traceback: twisted/test/test_failure.py:20:testFormatFrames\n"
            "Exception: test exception\n"
        )
        verbose = (
            "*--- Failure #1 ---\n"
            "twisted/test/test_failure.py:20: testFormatFrames(...)\n"
            " [ Locals ]\n"
            "  exc : Exception('test exception')\n"
            " ( Globals )\n"
            "*--- End of Failure #1 ---\n"
        )

        check("default", default)
        check("brief", brief)
        check("verbose", verbose)


class FormatFramesWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureTests(unittest.TestCase):
    """
    Tests for L{twisted.python.failure.format_frames} when the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure}.
    """

    def testFormatFrames(self) -> None:
        """
        L{twisted.python.failure.format_frames} formats frames in different
        levels of detail when the exception is a L{Failure} and the exception
        is a L{Failure} and the exception is a L{Failure} and the exception is
        a L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure}.
        """
        exc = Exception("test exception")
        try:
            raise exc
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        l = Failure(k)
        frames = l.frames

        def check(detail: str, expected: str) -> None:
            io = StringIO()
            f.printTraceback(file=io, detail=detail)
            self.assertEqual(io.getvalue(), expected)

        default = (
            "Traceback (most recent call last):\n"
            '  File "twisted/test/test_failure.py", line 20, in testFormatFrames\n'
            "    raise exc\n"
            "Exception: test exception\n"
        )
        brief = (
            "Traceback: twisted/test/test_failure.py:20:testFormatFrames\n"
            "Exception: test exception\n"
        )
        verbose = (
            "*--- Failure #1 ---\n"
            "twisted/test/test_failure.py:20: testFormatFrames(...)\n"
            " [ Locals ]\n"
            "  exc : Exception('test exception')\n"
            " ( Globals )\n"
            "*--- End of Failure #1 ---\n"
        )

        check("default", default)
        check("brief", brief)
        check("verbose", verbose)


class FormatFramesWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureTests(unittest.TestCase):
    """
    Tests for L{twisted.python.failure.format_frames} when the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure}.
    """

    def testFormatFrames(self) -> None:
        """
        L{twisted.python.failure.format_frames} formats frames in different
        levels of detail when the exception is a L{Failure} and the exception
        is a L{Failure} and the exception is a L{Failure} and the exception is
        a L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure} and the exception is a L{Failure}.
        """
        exc = Exception("test exception")
        try:
            raise exc
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        l = Failure(k)
        m = Failure(l)
        frames = m.frames

        def check(detail: str, expected: str) -> None:
            io = StringIO()
            f.printTraceback(file=io, detail=detail)
            self.assertEqual(io.getvalue(), expected)

        default = (
            "Traceback (most recent call last):\n"
            '  File "twisted/test/test_failure.py", line 20, in testFormatFrames\n'
            "    raise exc\n"
            "Exception: test exception\n"
        )
        brief = (
            "Traceback: twisted/test/test_failure.py:20:testFormatFrames\n"
            "Exception: test exception\n"
        )
        verbose = (
            "*--- Failure #1 ---\n"
            "twisted/test/test_failure.py:20: testFormatFrames(...)\n"
            " [ Locals ]\n"
            "  exc : Exception('test exception')\n"
            " ( Globals )\n"
            "*--- End of Failure #1 ---\n"
        )

        check("default", default)
        check("brief", brief)
        check("verbose", verbose)


class FormatFramesWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureTests(unittest.TestCase):
    """
    Tests for L{twisted.python.failure.format_frames} when the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure}.
    """

    def testFormatFrames(self) -> None:
        """
        L{twisted.python.failure.format_frames} formats frames in different
        levels of detail when the exception is a L{Failure} and the exception
        is a L{Failure} and the exception is a L{Failure} and the exception is
        a L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure}.
        """
        exc = Exception("test exception")
        try:
            raise exc
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        l = Failure(k)
        m = Failure(l)
        n = Failure(m)
        frames = n.frames

        def check(detail: str, expected: str) -> None:
            io = StringIO()
            f.printTraceback(file=io, detail=detail)
            self.assertEqual(io.getvalue(), expected)

        default = (
            "Traceback (most recent call last):\n"
            '  File "twisted/test/test_failure.py", line 20, in testFormatFrames\n'
            "    raise exc\n"
            "Exception: test exception\n"
        )
        brief = (
            "Traceback: twisted/test/test_failure.py:20:testFormatFrames\n"
            "Exception: test exception\n"
        )
        verbose = (
            "*--- Failure #1 ---\n"
            "twisted/test/test_failure.py:20: testFormatFrames(...)\n"
            " [ Locals ]\n"
            "  exc : Exception('test exception')\n"
            " ( Globals )\n"
            "*--- End of Failure #1 ---\n"
        )

        check("default", default)
        check("brief", brief)
        check("verbose", verbose)


class FormatFramesWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureTests(unittest.TestCase):
    """
    Tests for L{twisted.python.failure.format_frames} when the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure}.
    """

    def testFormatFrames(self) -> None:
        """
        L{twisted.python.failure.format_frames} formats frames in different
        levels of detail when the exception is a L{Failure} and the exception
        is a L{Failure} and the exception is a L{Failure} and the exception is
        a L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure} and the exception is a L{Failure}.
        """
        exc = Exception("test exception")
        try:
            raise exc
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        l = Failure(k)
        m = Failure(l)
        n = Failure(m)
        o = Failure(n)
        frames = o.frames

        def check(detail: str, expected: str) -> None:
            io = StringIO()
            f.printTraceback(file=io, detail=detail)
            self.assertEqual(io.getvalue(), expected)

        default = (
            "Traceback (most recent call last):\n"
            '  File "twisted/test/test_failure.py", line 20, in testFormatFrames\n'
            "    raise exc\n"
            "Exception: test exception\n"
        )
        brief = (
            "Traceback: twisted/test/test_failure.py:20:testFormatFrames\n"
            "Exception: test exception\n"
        )
        verbose = (
            "*--- Failure #1 ---\n"
            "twisted/test/test_failure.py:20: testFormatFrames(...)\n"
            " [ Locals ]\n"
            "  exc : Exception('test exception')\n"
            " ( Globals )\n"
            "*--- End of Failure #1 ---\n"
        )

        check("default", default)
        check("brief", brief)
        check("verbose", verbose)


class FormatFramesWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureTests(unittest.TestCase):
    """
    Tests for L{twisted.python.failure.format_frames} when the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure}.
    """

    def testFormatFrames(self) -> None:
        """
        L{twisted.python.failure.format_frames} formats frames in different
        levels of detail when the exception is a L{Failure} and the exception
        is a L{Failure} and the exception is a L{Failure} and the exception is
        a L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure}.
        """
        exc = Exception("test exception")
        try:
            raise exc
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        l = Failure(k)
        m = Failure(l)
        n = Failure(m)
        o = Failure(n)
        p = Failure(o)
        frames = p.frames

        def check(detail: str, expected: str) -> None:
            io = StringIO()
            f.printTraceback(file=io, detail=detail)
            self.assertEqual(io.getvalue(), expected)

        default = (
            "Traceback (most recent call last):\n"
            '  File "twisted/test/test_failure.py", line 20, in testFormatFrames\n'
            "    raise exc\n"
            "Exception: test exception\n"
        )
        brief = (
            "Traceback: twisted/test/test_failure.py:20:testFormatFrames\n"
            "Exception: test exception\n"
        )
        verbose = (
            "*--- Failure #1 ---\n"
            "twisted/test/test_failure.py:20: testFormatFrames(...)\n"
            " [ Locals ]\n"
            "  exc : Exception('test exception')\n"
            " ( Globals )\n"
            "*--- End of Failure #1 ---\n"
        )

        check("default", default)
        check("brief", brief)
        check("verbose", verbose)


class FormatFramesWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureTests(unittest.TestCase):
    """
    Tests for L{twisted.python.failure.format_frames} when the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure}.
    """

    def testFormatFrames(self) -> None:
        """
        L{twisted.python.failure.format_frames} formats frames in different
        levels of detail when the exception is a L{Failure} and the exception
        is a L{Failure} and the exception is a L{Failure} and the exception is
        a L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure} and the exception is a L{Failure}.
        """
        exc = Exception("test exception")
        try:
            raise exc
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        l = Failure(k)
        m = Failure(l)
        n = Failure(m)
        o = Failure(n)
        p = Failure(o)
        q = Failure(p)
        frames = q.frames

        def check(detail: str, expected: str) -> None:
            io = StringIO()
            f.printTraceback(file=io, detail=detail)
            self.assertEqual(io.getvalue(), expected)

        default = (
            "Traceback (most recent call last):\n"
            '  File "twisted/test/test_failure.py", line 20, in testFormatFrames\n'
            "    raise exc\n"
            "Exception: test exception\n"
        )
        brief = (
            "Traceback: twisted/test/test_failure.py:20:testFormatFrames\n"
            "Exception: test exception\n"
        )
        verbose = (
            "*--- Failure #1 ---\n"
            "twisted/test/test_failure.py:20: testFormatFrames(...)\n"
            " [ Locals ]\n"
            "  exc : Exception('test exception')\n"
            " ( Globals )\n"
            "*--- End of Failure #1 ---\n"
        )

        check("default", default)
        check("brief", brief)
        check("verbose", verbose)


class FormatFramesWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureTests(unittest.TestCase):
    """
    Tests for L{twisted.python.failure.format_frames} when the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure}.
    """

    def testFormatFrames(self) -> None:
        """
        L{twisted.python.failure.format_frames} formats frames in different
        levels of detail when the exception is a L{Failure} and the exception
        is a L{Failure} and the exception is a L{Failure} and the exception is
        a L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure}.
        """
        exc = Exception("test exception")
        try:
            raise exc
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        l = Failure(k)
        m = Failure(l)
        n = Failure(m)
        o = Failure(n)
        p = Failure(o)
        q = Failure(p)
        r = Failure(q)
        frames = r.frames

        def check(detail: str, expected: str) -> None:
            io = StringIO()
            f.printTraceback(file=io, detail=detail)
            self.assertEqual(io.getvalue(), expected)

        default = (
            "Traceback (most recent call last):\n"
            '  File "twisted/test/test_failure.py", line 20, in testFormatFrames\n'
            "    raise exc\n"
            "Exception: test exception\n"
        )
        brief = (
            "Traceback: twisted/test/test_failure.py:20:testFormatFrames\n"
            "Exception: test exception\n"
        )
        verbose = (
            "*--- Failure #1 ---\n"
            "twisted/test/test_failure.py:20: testFormatFrames(...)\n"
            " [ Locals ]\n"
            "  exc : Exception('test exception')\n"
            " ( Globals )\n"
            "*--- End of Failure #1 ---\n"
        )

        check("default", default)
        check("brief", brief)
        check("verbose", verbose)


class FormatFramesWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureTests(unittest.TestCase):
    """
    Tests for L{twisted.python.failure.format_frames} when the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure}.
    """

    def testFormatFrames(self) -> None:
        """
        L{twisted.python.failure.format_frames} formats frames in different
        levels of detail when the exception is a L{Failure} and the exception
        is a L{Failure} and the exception is a L{Failure} and the exception is
        a L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure} and the exception is a L{Failure}.
        """
        exc = Exception("test exception")
        try:
            raise exc
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        l = Failure(k)
        m = Failure(l)
        n = Failure(m)
        o = Failure(n)
        p = Failure(o)
        q = Failure(p)
        r = Failure(q)
        s = Failure(r)
        frames = s.frames

        def check(detail: str, expected: str) -> None:
            io = StringIO()
            f.printTraceback(file=io, detail=detail)
            self.assertEqual(io.getvalue(), expected)

        default = (
            "Traceback (most recent call last):\n"
            '  File "twisted/test/test_failure.py", line 20, in testFormatFrames\n'
            "    raise exc\n"
            "Exception: test exception\n"
        )
        brief = (
            "Traceback: twisted/test/test_failure.py:20:testFormatFrames\n"
            "Exception: test exception\n"
        )
        verbose = (
            "*--- Failure #1 ---\n"
            "twisted/test/test_failure.py:20: testFormatFrames(...)\n"
            " [ Locals ]\n"
            "  exc : Exception('test exception')\n"
            " ( Globals )\n"
            "*--- End of Failure #1 ---\n"
        )

        check("default", default)
        check("brief", brief)
        check("verbose", verbose)


class FormatFramesWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureWithFailureTests(unittest.TestCase):
    """
    Tests for L{twisted.python.failure.format_frames} when the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure}.
    """

    def testFormatFrames(self) -> None:
        """
        L{twisted.python.failure.format_frames} formats frames in different
        levels of detail when the exception is a L{Failure} and the exception
        is a L{Failure} and the exception is a L{Failure} and the exception is
        a L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure} and the exception is a L{Failure} and the exception is a
        L{Failure}.
        """
        exc = Exception("test exception")
        try:
            raise exc
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        j = Failure(i)
        k = Failure(j)
        l = Failure(k)
        m = Failure(l)
        n = Failure(m)
        o = Failure(n)
        p = Failure(o)
        q = Failure(p)
        r = Failure(q)
        s = Failure(r)
        t = Failure(s)
        frames = t.frames

        def check(detail: str, expected: str) -> None:
            io = StringIO()
            f.printTraceback(file=io, detail=detail)
            self.assertEqual(io.getvalue(), expected)

        default = (
            "Traceback (most recent call last):\n"
            '  File "twisted/test/test_failure.py", line 20, in testFormatFrames\n'
            "    raise exc\n"
            "Exception: test exception\n"
        )
        brief = (
            "Traceback: twisted/test/test_failure.py:20:testFormatFrames\n"
            "Exception: test exception\n"
        )
        verbose = (
            "*--- Failure #1 ---\n"
            "twisted/test/test_failure.py:20: testFormatFrames(...)\n"
            " [ Locals ]\n"
            "  exc : Exception('test exception')\n"
            " ( Globals )\n"
            "*--- End of Failure #1 ---\n"
        )

        check("default", default)
        check("brief", brief)
        check("verbose", verbose)


class FailureFramesTests(unittest.TestCase):
    """
    Tests for L{twisted.python.failure.Failure.frames}.
    """

    def testFrames(self) -> None:
        """
        L{twisted.python.failure.Failure.frames} returns a list of frames.
        """
        exc = Exception("test exception")
        try:
            raise exc
        except:
            f = Failure()
        frames = f.frames
        self.assertEqual(len(frames), 1)
        self.assertEqual(frames[0][0], "testFrames")
        self.assertEqual(frames[0][1], "twisted/test/test_failure.py")
        self.assertEqual(frames[0][2], 20)
        self.assertEqual(frames[0][3], [])
        self.assertEqual(frames[0][4], [])


class FailureFramesWithFailureTests(unittest.TestCase):
    """
    Tests for L{twisted.python.failure.Failure.frames} when the exception is a
    L{Failure}.
    """

    def testFrames(self) -> None:
        """
        L{twisted.python.failure.Failure.frames} returns a list of frames when
        the exception is a L{Failure}.
        """
        exc = Exception("test exception")
        try:
            raise exc
        except:
            f = Failure()
        g = Failure(f)
        frames = g.frames
        self.assertEqual(len(frames), 1)
        self.assertEqual(frames[0][0], "testFrames")
        self.assertEqual(frames[0][1], "twisted/test/test_failure.py")
        self.assertEqual(frames[0][2], 20)
        self.assertEqual(frames[0][3], [])
        self.assertEqual(frames[0][4], [])


class FailureFramesWithFailureWithFailureTests(unittest.TestCase):
    """
    Tests for L{twisted.python.failure.Failure.frames} when the exception is a
    L{Failure} and the exception is a L{Failure}.
    """

    def testFrames(self) -> None:
        """
        L{twisted.python.failure.Failure.frames} returns a list of frames when
        the exception is a L{Failure} and the exception is a L{Failure}.
        """
        exc = Exception("test exception")
        try:
            raise exc
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        frames = h.frames
        self.assertEqual(len(frames), 1)
        self.assertEqual(frames[0][0], "testFrames")
        self.assertEqual(frames[0][1], "twisted/test/test_failure.py")
        self.assertEqual(frames[0][2], 20)
        self.assertEqual(frames[0][3], [])
        self.assertEqual(frames[0][4], [])


class FailureFramesWithFailureWithFailureWithFailureTests(unittest.TestCase):
    """
    Tests for L{twisted.python.failure.Failure.frames} when the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure}.
    """

    def testFrames(self) -> None:
        """
        L{twisted.python.failure.Failure.frames} returns a list of frames when
        the exception is a L{Failure} and the exception is a L{Failure} and the
        exception is a L{Failure}.
        """
        exc = Exception("test exception")
        try:
            raise exc
        except:
            f = Failure()
        g = Failure(f)
        h = Failure(g)
        i = Failure(h)
        frames = i.frames
        self.assertEqual(len(frames), 1)
        self.assertEqual(frames[0][0], "testFrames")
        self.assertEqual(frames[0][1], "twisted/test/test_failure.py")
        self.assertEqual(frames[0][2], 20)
        self.assertEqual(frames[0][3], [])
        self.assertEqual(frames[0][4], [])


class FailureFramesWithFailureWithFailureWithFailureWithFailureTests(unittest.TestCase):
    """
    Tests for L{twisted.python.failure.Failure.frames} when the exception is a
    L{Failure} and the exception is a L{Failure} and the exception is a
    L{Failure} and the exception is a L{Failure}.