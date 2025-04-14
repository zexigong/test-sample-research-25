# -*- test-case-name: twisted.test.test_failure -*-

from twisted.trial import unittest
from twisted.test_failure import Failure, DefaultException, NoCurrentExceptionError, format_frames
import sys


class FailureTests(unittest.TestCase):
    def test_failureInitializationWithCurrentException(self):
        """
        Test that a Failure can be initialized using the current exception.
        """
        try:
            raise DefaultException("test exception")
        except DefaultException:
            f = Failure()
        self.assertEqual(f.type, DefaultException)
        self.assertEqual(str(f.value), "test exception")

    def test_failureInitializationWithExplicitException(self):
        """
        Test that a Failure can be initialized with an explicit exception value.
        """
        exc = DefaultException("explicit exception")
        f = Failure(exc)
        self.assertEqual(f.type, DefaultException)
        self.assertEqual(f.value, exc)

    def test_failureInitializationWithoutCurrentException(self):
        """
        Test that initializing a Failure without a current exception raises NoCurrentExceptionError.
        """
        self.assertRaises(NoCurrentExceptionError, Failure)

    def test_trapCatchesExpectedException(self):
        """
        Test that the trap method catches an expected exception type.
        """
        try:
            raise DefaultException("trap this")
        except DefaultException:
            f = Failure()
        self.assertEqual(f.trap(DefaultException), DefaultException)

    def test_trapReraisesUnexpectedException(self):
        """
        Test that the trap method reraises an unexpected exception type.
        """
        try:
            raise DefaultException("do not trap this")
        except DefaultException:
            f = Failure()
        self.assertRaises(DefaultException, f.trap, ValueError)

    def test_checkIdentifiesExceptionType(self):
        """
        Test that the check method correctly identifies an exception type.
        """
        try:
            raise DefaultException("check this")
        except DefaultException:
            f = Failure()
        self.assertEqual(f.check(DefaultException), DefaultException)
        self.assertIsNone(f.check(ValueError))

    def test_raiseExceptionPreservesTraceback(self):
        """
        Test that raiseException raises the original exception with its traceback.
        """
        try:
            raise DefaultException("raise this")
        except DefaultException:
            f = Failure()
        self.assertRaises(DefaultException, f.raiseException)

    def test_formatFramesDefaultDetail(self):
        """
        Test the format_frames function with default detail level.
        """
        frames = [
            ("function1", "file1.py", 10, [("var1", "value1")], [("gvar1", "gvalue1")])
        ]
        output = []

        def write(s):
            output.append(s)

        format_frames(frames, write, detail="default")
        self.assertIn('  File "file1.py", line 10, in function1\n', output[0])

    def test_formatFramesBriefDetail(self):
        """
        Test the format_frames function with brief detail level.
        """
        frames = [
            ("function2", "file2.py", 20, [("var2", "value2")], [("gvar2", "gvalue2")])
        ]
        output = []

        def write(s):
            output.append(s)

        format_frames(frames, write, detail="brief")
        self.assertIn("file2.py:20:function2\n", output[0])