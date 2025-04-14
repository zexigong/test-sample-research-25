# -*- test-case-name: twisted.test.test_logfile -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.python.logfile}.
"""

import os
import time
import warnings

from twisted.python.runtime import platform

from twisted.python import logfile, threadable
from twisted.python.compat import NativeStringIO as StringIO
from twisted.trial.unittest import TestCase
from twisted.python.filepath import FilePath


class LogfileTestsMixin:
    """
    Tests for L{logfile.BaseLogFile}.
    """

    # Subclass should provide.
    fileType = None
    defaultSuffix = None

    def setUp(self):
        """
        Create a L{FilePath} pointing to a temporary directory and create a
        log file in it.
        """
        self.directory = FilePath(self.mktemp())
        self.directory.makedirs()
        self.path = self.directory.child("logfile")
        self.log = self.fileType.fromFullPath(self.path.path)

    def tearDown(self):
        """
        Close the log file.
        """
        self.log.close()

    def test_write(self):
        """
        L{logfile.BaseLogFile.write} writes the given data in the underlying
        file.
        """
        self.log.write(b"something")
        self.log.flush()
        self.assertEqual(self.path.getContent(), b"something")

    def test_writeUnicode(self):
        """
        L{logfile.BaseLogFile.write} will encode unicode data to UTF-8 to
        write it to the underlying file.
        """
        self.log.write("something")
        self.log.flush()
        self.assertEqual(self.path.getContent(), b"something")

    def test_writeUnicodeWithNonASCII(self):
        """
        L{logfile.BaseLogFile.write} will encode unicode data containing
        non-ASCII characters to UTF-8 to write it to the underlying file.
        """
        self.log.write("\N{VULGAR FRACTION ONE HALF}")
        self.log.flush()
        self.assertEqual(self.path.getContent(), b"\xc2\xbd")

    def test_writeBytesAndUnicode(self):
        """
        L{logfile.BaseLogFile.write} can be called with both L{bytes} and
        L{unicode} and the written data will be concatenated in the
        underlying file.
        """
        self.log.write(b"foo")
        self.log.write("bar")
        self.log.flush()
        self.assertEqual(self.path.getContent(), b"foobar")

    def test_writeUnicodeAndBytes(self):
        """
        L{logfile.BaseLogFile.write} can be called with both L{bytes} and
        L{unicode} and the written data will be concatenated in the
        underlying file.
        """
        self.log.write("foo")
        self.log.write(b"bar")
        self.log.flush()
        self.assertEqual(self.path.getContent(), b"foobar")

    def test_writeNonUTF8Bytes(self):
        """
        When L{logfile.BaseLogFile.write} is called with L{bytes} with a
        non-UTF-8 representation, the data is written to the underlying file.
        """
        self.log.write(b"\x80")
        self.log.flush()
        self.assertEqual(self.path.getContent(), b"\x80")

    def test_flush(self):
        """
        L{logfile.BaseLogFile.flush} flushes the underlying file.
        """
        self.log.write(b"something")
        self.log.flush()
        self.assertEqual(self.path.getContent(), b"something")

    def test_close(self):
        """
        L{logfile.BaseLogFile.close} closes the underlying file.
        """
        self.log.close()
        exc = self.assertRaises(ValueError, self.log.flush)
        self.assertEqual(str(exc), "flush of closed file")

    def test_reopen(self):
        """
        L{logfile.BaseLogFile.reopen} closes and reopens the underlying file.
        """
        self.log.write(b"something")
        self.log.flush()
        self.log.reopen()
        self.log.write(b"else")
        self.log.flush()
        self.assertEqual(self.path.getContent(), b"somethingelse")

    def test_getCurrentLog(self):
        """
        L{logfile.BaseLogFile.getCurrentLog} returns a L{logfile.LogReader}
        that reads from the current log file.
        """
        self.log.write(b"something")
        self.log.flush()
        reader = self.log.getCurrentLog()
        self.assertEqual(reader.readLines(), [b"something"])


class LogfileTests(LogfileTestsMixin, TestCase):
    """
    Tests for L{logfile.LogFile}.
    """

    fileType = logfile.LogFile

    def test_rotation(self):
        """
        If the log file grows larger than a limit, it is rotated.
        """
        log = logfile.LogFile.fromFullPath(self.path.path, rotateLength=10)
        log.write(b"0123456789")
        log.flush()
        self.assertEqual(self.path.getContent(), b"0123456789")
        log.write(b"abcdefghij")
        log.flush()
        self.assertEqual(self.path.getContent(), b"abcdefghij")
        self.assertEqual(self.path.sibling("logfile.1").getContent(), b"0123456789")

    def test_rotationByteCount(self):
        """
        Any bytes written beyond the rotation limit cause a new log file to be
        opened.
        """
        log = logfile.LogFile.fromFullPath(self.path.path, rotateLength=10)
        log.write(b"0123456789")
        log.write(b"abcdefghij")
        log.write(b"0123456789")
        log.flush()
        self.assertEqual(self.path.getContent(), b"abcdefghij0123456789")
        self.assertEqual(self.path.sibling("logfile.1").getContent(), b"0123456789")

    def test_rotate(self):
        """
        L{logfile.LogFile.rotate} rotates the log file.
        """
        log = logfile.LogFile.fromFullPath(self.path.path, rotateLength=10)
        log.write(b"0123456789")
        log.flush()
        self.assertEqual(self.path.getContent(), b"0123456789")
        log.rotate()
        log.write(b"abcdefghij")
        log.flush()
        self.assertEqual(self.path.getContent(), b"abcdefghij")
        self.assertEqual(self.path.sibling("logfile.1").getContent(), b"0123456789")

    def test_rotationDisallowedWhenDirectoryIsNotWritable(self):
        """
        The log file is not rotated if the directory is not writable.
        """
        log = logfile.LogFile.fromFullPath(self.path.path, rotateLength=10)
        log.write(b"0123456789")
        self.directory.chmod(0o400)
        self.addCleanup(self.directory.chmod, 0o700)
        log.write(b"abcdefghij")
        log.flush()
        self.assertEqual(self.path.getContent(), b"0123456789abcdefghij")
        self.assertFalse(self.path.sibling("logfile.1").exists())

    def test_rotationDisallowedWhenFileIsNotWritable(self):
        """
        The log file is not rotated if the file is not writable.
        """
        log = logfile.LogFile.fromFullPath(self.path.path, rotateLength=10)
        log.write(b"0123456789")
        self.path.chmod(0o400)
        self.addCleanup(self.path.chmod, 0o600)
        log.write(b"abcdefghij")
        log.flush()
        self.assertEqual(self.path.getContent(), b"0123456789abcdefghij")
        self.assertFalse(self.path.sibling("logfile.1").exists())

    def test_rotationAllowedWhenDirectoryAndFileAreWritable(self):
        """
        The log file is rotated if both the directory and the file are writable.
        """
        log = logfile.LogFile.fromFullPath(self.path.path, rotateLength=10)
        log.write(b"0123456789")
        self.path.chmod(0o400)
        self.directory.chmod(0o700)
        self.addCleanup(self.path.chmod, 0o600)
        log.write(b"abcdefghij")
        log.flush()
        self.assertEqual(self.path.getContent(), b"abcdefghij")
        self.assertEqual(self.path.sibling("logfile.1").getContent(), b"0123456789")

    def test_rotateMaxFiles(self):
        """
        L{logfile.LogFile.rotate} deletes older rotated log files when the
        maximum number of rotated log files is reached.
        """
        log = logfile.LogFile.fromFullPath(
            self.path.path, rotateLength=10, maxRotatedFiles=2
        )
        log.write(b"0123456789")
        log.flush()
        self.assertEqual(self.path.getContent(), b"0123456789")
        log.rotate()
        self.assertFalse(self.path.sibling("logfile.2").exists())
        self.assertEqual(self.path.sibling("logfile.1").getContent(), b"0123456789")

        log.write(b"abcdefghij")
        log.flush()
        log.rotate()
        self.assertFalse(self.path.sibling("logfile.3").exists())
        self.assertEqual(self.path.sibling("logfile.2").getContent(), b"0123456789")
        self.assertEqual(self.path.sibling("logfile.1").getContent(), b"abcdefghij")

        log.write(b"0123456789")
        log.flush()
        log.rotate()
        self.assertFalse(self.path.sibling("logfile.3").exists())
        self.assertEqual(self.path.sibling("logfile.2").getContent(), b"abcdefghij")
        self.assertEqual(self.path.sibling("logfile.1").getContent(), b"0123456789")

    def test_rotateMaxFilesNone(self):
        """
        L{logfile.LogFile.rotate} doesn't delete older rotated log files when
        the maximum number of rotated log files is not set.
        """
        log = logfile.LogFile.fromFullPath(
            self.path.path, rotateLength=10, maxRotatedFiles=None
        )
        log.write(b"0123456789")
        log.flush()
        self.assertEqual(self.path.getContent(), b"0123456789")
        log.rotate()
        self.assertTrue(self.path.sibling("logfile.1").exists())
        self.assertEqual(self.path.sibling("logfile.1").getContent(), b"0123456789")

        log.write(b"abcdefghij")
        log.flush()
        log.rotate()
        self.assertTrue(self.path.sibling("logfile.2").exists())
        self.assertEqual(self.path.sibling("logfile.2").getContent(), b"0123456789")
        self.assertEqual(self.path.sibling("logfile.1").getContent(), b"abcdefghij")

        log.write(b"0123456789")
        log.flush()
        log.rotate()
        self.assertTrue(self.path.sibling("logfile.3").exists())
        self.assertEqual(self.path.sibling("logfile.3").getContent(), b"0123456789")
        self.assertEqual(self.path.sibling("logfile.2").getContent(), b"abcdefghij")
        self.assertEqual(self.path.sibling("logfile.1").getContent(), b"0123456789")

    def test_rotateMaxFilesNoneDefault(self):
        """
        L{logfile.LogFile.rotate} doesn't delete older rotated log files when
        the maximum number of rotated log files isn't passed as an argument.
        """
        log = logfile.LogFile.fromFullPath(self.path.path, rotateLength=10)
        log.write(b"0123456789")
        log.flush()
        self.assertEqual(self.path.getContent(), b"0123456789")
        log.rotate()
        self.assertTrue(self.path.sibling("logfile.1").exists())
        self.assertEqual(self.path.sibling("logfile.1").getContent(), b"0123456789")

        log.write(b"abcdefghij")
        log.flush()
        log.rotate()
        self.assertTrue(self.path.sibling("logfile.2").exists())
        self.assertEqual(self.path.sibling("logfile.2").getContent(), b"0123456789")
        self.assertEqual(self.path.sibling("logfile.1").getContent(), b"abcdefghij")

        log.write(b"0123456789")
        log.flush()
        log.rotate()
        self.assertTrue(self.path.sibling("logfile.3").exists())
        self.assertEqual(self.path.sibling("logfile.3").getContent(), b"0123456789")
        self.assertEqual(self.path.sibling("logfile.2").getContent(), b"abcdefghij")
        self.assertEqual(self.path.sibling("logfile.1").getContent(), b"0123456789")

    def test_getLog(self):
        """
        L{logfile.LogFile.getLog} returns a L{logfile.LogReader} that reads
        from a rotated log file.
        """
        log = logfile.LogFile.fromFullPath(self.path.path, rotateLength=10)
        log.write(b"0123456789")
        log.flush()
        log.rotate()
        reader = log.getLog(1)
        self.assertEqual(reader.readLines(), [b"0123456789"])

    def test_getLogCurrent(self):
        """
        L{logfile.LogFile.getLog} returns a L{logfile.LogReader} that reads
        from the current log file.
        """
        log = logfile.LogFile.fromFullPath(self.path.path, rotateLength=10)
        log.write(b"0123456789")
        reader = log.getLog(0)
        self.assertEqual(reader.readLines(), [b"0123456789"])

    def test_getLogNonExistent(self):
        """
        L{logfile.LogFile.getLog} raises a L{ValueError} if the given rotated
        log file doesn't exist.
        """
        log = logfile.LogFile.fromFullPath(self.path.path, rotateLength=10)
        log.write(b"0123456789")
        log.flush()
        self.assertRaises(ValueError, log.getLog, 1)

    def test_listLogs(self):
        """
        L{logfile.LogFile.listLogs} returns a list of log files' identifiers,
        sorted in ascending order.
        """
        log = logfile.LogFile.fromFullPath(self.path.path, rotateLength=10)
        log.write(b"0123456789")
        log.flush()
        log.rotate()
        log.write(b"abcdefghij")
        log.flush()
        log.rotate()
        log.write(b"0123456789")
        log.flush()
        self.assertEqual(log.listLogs(), [1, 2])

    def test_listLogsWithNonRotatedFiles(self):
        """
        L{logfile.LogFile.listLogs} returns a list of log files' identifiers,
        sorted in ascending order, including non-rotated log files.
        """
        log = logfile.LogFile.fromFullPath(self.path.path, rotateLength=10)
        log.write(b"0123456789")
        log.flush()
        log.rotate()
        log.write(b"abcdefghij")
        log.flush()
        self.path.sibling("logfile.1.2").setContent(b"")
        log.write(b"0123456789")
        log.flush()
        self.assertEqual(log.listLogs(), [1])

    def test_defaultMode(self):
        """
        If the log file already exists, L{logfile.LogFile} uses its current
        permissions to create new log file.
        """
        self.path.setContent(b"")
        self.path.chmod(0o640)
        self.addCleanup(self.path.chmod, 0o600)
        log = logfile.LogFile.fromFullPath(self.path.path, rotateLength=10)
        log.write(b"0123456789")
        log.flush()
        log.rotate()
        self.assertEqual(self.path.getPermissions(), self.path.sibling("logfile.1").getPermissions())

    def test_defaultModeNonExistent(self):
        """
        If the log file doesn't exist, L{logfile.LogFile} creates it with the
        default permission of 0o600.
        """
        log = logfile.LogFile.fromFullPath(self.path.path, rotateLength=10)
        log.write(b"0123456789")
        log.flush()
        self.assertEqual(self.path.getPermissions(), 0o600)

    def test_defaultModeGiven(self):
        """
        If the C{defaultMode} argument is passed to L{logfile.LogFile}, it is
        used to create new log file.
        """
        log = logfile.LogFile.fromFullPath(self.path.path, rotateLength=10, defaultMode=0o640)
        log.write(b"0123456789")
        log.flush()
        log.rotate()
        self.assertEqual(self.path.getPermissions(), self.path.sibling("logfile.1").getPermissions())


class DailyLogFileTests(LogfileTestsMixin, TestCase):
    """
    Tests for L{logfile.DailyLogFile}.
    """

    fileType = logfile.DailyLogFile

    def test_rotation(self):
        """
        The log file is rotated every day.
        """
        log = logfile.DailyLogFile.fromFullPath(self.path.path)
        log.toDate = lambda *args: (2008, 10, 8)
        log.write(b"something")
        log.flush()
        self.assertEqual(self.path.getContent(), b"something")

        log.toDate = lambda *args: (2008, 10, 9)
        log.write(b"else")
        log.flush()
        self.assertEqual(self.path.getContent(), b"else")
        self.assertEqual(self.path.sibling("logfile.2008_10_8").getContent(), b"something")

    def test_rotationTimeTravel(self):
        """
        If the clock goes back but the day doesn't change, the log file
        is not rotated.
        """
        log = logfile.DailyLogFile.fromFullPath(self.path.path)
        log.toDate = lambda *args: (2008, 10, 8)
        log.write(b"something")
        log.flush()
        self.assertEqual(self.path.getContent(), b"something")

        log.toDate = lambda *args: (2008, 10, 8)
        log.write(b"else")
        log.flush()
        self.assertEqual(self.path.getContent(), b"somethingelse")
        self.assertFalse(self.path.sibling("logfile.2008_10_8").exists())

    def test_rotationTimeTravelNotMidnight(self):
        """
        If the clock goes back and the day changes, the log file is
        rotated.
        """
        log = logfile.DailyLogFile.fromFullPath(self.path.path)
        log.toDate = lambda *args: (2008, 10, 8)
        log.write(b"something")
        log.flush()
        self.assertEqual(self.path.getContent(), b"something")

        log.toDate = lambda *args: (2008, 10, 7)
        log.write(b"else")
        log.flush()
        self.assertEqual(self.path.getContent(), b"else")
        self.assertEqual(self.path.sibling("logfile.2008_10_8").getContent(), b"something")

    def test_rotationDisallowedWhenDirectoryIsNotWritable(self):
        """
        The log file is not rotated if the directory is not writable.
        """
        log = logfile.DailyLogFile.fromFullPath(self.path.path)
        log.toDate = lambda *args: (2008, 10, 8)
        log.write(b"something")
        log.flush()
        self.assertEqual(self.path.getContent(), b"something")

        log.toDate = lambda *args: (2008, 10, 9)
        self.directory.chmod(0o400)
        self.addCleanup(self.directory.chmod, 0o700)
        log.write(b"else")
        log.flush()
        self.assertEqual(self.path.getContent(), b"somethingelse")
        self.assertFalse(self.path.sibling("logfile.2008_10_8").exists())

    def test_rotationDisallowedWhenFileIsNotWritable(self):
        """
        The log file is not rotated if the file is not writable.
        """
        log = logfile.DailyLogFile.fromFullPath(self.path.path)
        log.toDate = lambda *args: (2008, 10, 8)
        log.write(b"something")
        log.flush()
        self.assertEqual(self.path.getContent(), b"something")

        log.toDate = lambda *args: (2008, 10, 9)
        self.path.chmod(0o400)
        self.addCleanup(self.path.chmod, 0o600)
        log.write(b"else")
        log.flush()
        self.assertEqual(self.path.getContent(), b"somethingelse")
        self.assertFalse(self.path.sibling("logfile.2008_10_8").exists())

    def test_rotationAllowedWhenDirectoryAndFileAreWritable(self):
        """
        The log file is rotated if both the directory and the file are writable.
        """
        log = logfile.DailyLogFile.fromFullPath(self.path.path)
        log.toDate = lambda *args: (2008, 10, 8)
        log.write(b"something")
        log.flush()
        self.assertEqual(self.path.getContent(), b"something")

        log.toDate = lambda *args: (2008, 10, 9)
        self.path.chmod(0o400)
        self.directory.chmod(0o700)
        self.addCleanup(self.path.chmod, 0o600)
        log.write(b"else")
        log.flush()
        self.assertEqual(self.path.getContent(), b"else")
        self.assertEqual(self.path.sibling("logfile.2008_10_8").getContent(), b"something")

    def test_getLog(self):
        """
        L{logfile.DailyLogFile.getLog} returns a L{logfile.LogReader} that
        reads from a rotated log file.
        """
        log = logfile.DailyLogFile.fromFullPath(self.path.path)
        log.toDate = lambda *args: (2008, 10, 8)
        log.write(b"something")
        log.flush()
        log.toDate = lambda *args: (2008, 10, 9)
        log.write(b"else")
        log.flush()
        reader = log.getLog(time.mktime((2008, 10, 8, 0, 0, 0, 0, 0, -1)))
        self.assertEqual(reader.readLines(), [b"something"])

    def test_getLogCurrent(self):
        """
        L{logfile.DailyLogFile.getLog} returns a L{logfile.LogReader} that
        reads from the current log file.
        """
        log = logfile.DailyLogFile.fromFullPath(self.path.path)
        log.toDate = lambda *args: (2008, 10, 8)
        log.write(b"something")
        log.flush()
        reader = log.getLog(time.mktime((2008, 10, 8, 0, 0, 0, 0, 0, -1)))
        self.assertEqual(reader.readLines(), [b"something"])

    def test_getLogNonExistent(self):
        """
        L{logfile.DailyLogFile.getLog} raises a L{ValueError} if the given
        rotated log file doesn't exist.
        """
        log = logfile.DailyLogFile.fromFullPath(self.path.path)
        self.assertRaises(ValueError, log.getLog, time.mktime((2008, 10, 8, 0, 0, 0, 0, 0, -1)))

    def test_defaultMode(self):
        """
        If the log file already exists, L{logfile.DailyLogFile} uses its
        current permissions to create new log file.
        """
        self.path.setContent(b"")
        self.path.chmod(0o640)
        self.addCleanup(self.path.chmod, 0o600)
        log = logfile.DailyLogFile.fromFullPath(self.path.path)
        log.toDate = lambda *args: (2008, 10, 8)
        log.write(b"something")
        log.flush()
        log.toDate = lambda *args: (2008, 10, 9)
        log.write(b"else")
        log.flush()
        self.assertEqual(self.path.getPermissions(), self.path.sibling("logfile.2008_10_8").getPermissions())

    def test_defaultModeNonExistent(self):
        """
        If the log file doesn't exist, L{logfile.DailyLogFile} creates it with
        the default permission of 0o600.
        """
        log = logfile.DailyLogFile.fromFullPath(self.path.path)
        log.write(b"something")
        log.flush()
        self.assertEqual(self.path.getPermissions(), 0o600)

    def test_defaultModeGiven(self):
        """
        If the C{defaultMode} argument is passed to L{logfile.DailyLogFile},
        it is used to create new log file.
        """
        log = logfile.DailyLogFile.fromFullPath(self.path.path, defaultMode=0o640)
        log.write(b"something")
        log.flush()
        log.toDate = lambda *args: (2008, 10, 8)
        log.write(b"else")
        log.flush()
        log.toDate = lambda *args: (2008, 10, 9)
        log.write(b"something")
        log.flush()
        self.assertEqual(self.path.getPermissions(), self.path.sibling("logfile.2008_10_8").getPermissions())


class LogReaderTests(TestCase):
    """
    Tests for L{logfile.LogReader}.
    """

    def setUp(self):
        """
        Create a L{FilePath} pointing to a temporary directory and create a
        log file in it.
        """
        self.path = FilePath(self.mktemp())
        self.reader = logfile.LogReader(self.path.path)

    def tearDown(self):
        """
        Close the log reader.
        """
        self.reader.close()

    def test_readLines(self):
        """
        L{logfile.LogReader.readLines} reads lines from the log file.
        """
        self.path.setContent(b"line1\nline2\nline3\n")
        self.assertEqual(self.reader.readLines(), [b"line1\n", b"line2\n", b"line3\n"])

    def test_readLinesPartial(self):
        """
        L{logfile.LogReader.readLines} reads a given number of lines from the
        log file.
        """
        self.path.setContent(b"line1\nline2\nline3\n")
        self.assertEqual(self.reader.readLines(2), [b"line1\n", b"line2\n"])

    def test_readLinesPartialMultipleTimes(self):
        """
        L{logfile.LogReader.readLines} can be called multiple times to read
        the entire content of the log file.
        """
        self.path.setContent(b"line1\nline2\nline3\n")
        self.assertEqual(self.reader.readLines(2), [b"line1\n", b"line2\n"])
        self.assertEqual(self.reader.readLines(2), [b"line3\n"])

    def test_readLinesEOF(self):
        """
        L{logfile.LogReader.readLines} returns an empty list when the end of
        the log file is reached.
        """
        self.path.setContent(b"")
        self.assertEqual(self.reader.readLines(), [])

    def test_close(self):
        """
        L{logfile.LogReader.close} closes the log reader.
        """
        self.reader.close()
        exc = self.assertRaises(ValueError, self.reader.readLines)
        self.assertEqual(str(exc), "I/O operation on closed file.")


class ThreadedLogfileTests(TestCase):
    """
    Tests for L{logfile.LogFile} and L{logfile.DailyLogFile} when used with
    threads.
    """

    def setUp(self):
        """
        Enable threading.
        """
        threadable.init()
        threadable.threaded = True

    def tearDown(self):
        """
        Disable threading.
        """
        threadable.threaded = False

    def test_logFile(self):
        """
        L{logfile.LogFile.write} can be called from multiple threads.
        """
        directory = FilePath(self.mktemp())
        directory.makedirs()
        path = directory.child("logfile")
        log = logfile.LogFile.fromFullPath(path.path)
        log.write(b"something")
        log.flush()
        self.assertEqual(path.getContent(), b"something")

    def test_dailyLogFile(self):
        """
        L{logfile.DailyLogFile.write} can be called from multiple threads.
        """
        directory = FilePath(self.mktemp())
        directory.makedirs()
        path = directory.child("logfile")
        log = logfile.DailyLogFile.fromFullPath(path.path)
        log.write(b"something")
        log.flush()
        self.assertEqual(path.getContent(), b"something")


class LogfileDeprecationTests(TestCase):
    """
    Tests for deprecations in L{logfile}.
    """

    def test_synchronize(self):
        """
        L{logfile.synchronize} is deprecated.
        """
        log = logfile.LogFile("logfile", self.mktemp())
        self.assertWarns(
            DeprecationWarning,
            "twisted.python.logfile.synchronize was deprecated in Twisted 17.9.0. Use twisted.python.threadable.synchronize instead.",
            logfile.synchronize,
            log,
        )
        self.assertEqual(threadable.synchronize([log]), None)