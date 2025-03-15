import os
import stat
import tempfile
import time
import warnings
from itertools import count

import pytest

from twisted.logger import LogPublisher, Logger, LogLevel
from twisted.logger.test.test_observer import TestHandler
from twisted.python.logfile import (
    BaseLogFile,
    DailyLogFile,
    LogFile,
    LogReader,
)
from twisted.python.runtime import platform


def _writeSomeEntries(logfile, n=10):
    for i in range(n):
        logfile.write(f"line {i}\n")
    logfile.flush()


def testDefaultMode():
    """
    Check that default permissions are respected.
    """
    with tempfile.TemporaryDirectory() as directory:
        # Initialize a log file
        logFile = LogFile("test.log", directory)
        path = os.path.join(directory, "test.log")
        _writeSomeEntries(logFile)
        logFile.flush()
        assert stat.S_IMODE(os.stat(path)[stat.ST_MODE]) == 0o666 & ~os.umask(0)

        # Reopen it
        logFile.reopen()
        logFile.write("x\n")
        logFile.close()
        assert stat.S_IMODE(os.stat(path)[stat.ST_MODE]) == 0o666 & ~os.umask(0)

        # Recreate with specific mode
        logFile = LogFile("test.log", directory, defaultMode=0o600)
        logFile.write("x\n")
        logFile.close()
        assert stat.S_IMODE(os.stat(path)[stat.ST_MODE]) == 0o600


def testRotateWithoutPermissions():
    """
    It should be possible to rotate a log file without write permissions.
    """
    with tempfile.TemporaryDirectory() as directory:
        logFile = LogFile("test.log", directory)
        path = os.path.join(directory, "test.log")
        _writeSomeEntries(logFile)
        logFile.flush()
        os.chmod(path, 0o444)
        logFile.rotate()


def testReopenWithoutPermissions():
    """
    It should be possible to reopen a log file without write permissions.
    """
    with tempfile.TemporaryDirectory() as directory:
        logFile = LogFile("test.log", directory)
        path = os.path.join(directory, "test.log")
        _writeSomeEntries(logFile)
        logFile.flush()
        os.chmod(path, 0o444)
        logFile.reopen()
        logFile.write("x\n")


def testLogFileRotate():
    """
    Test that LogFile rotates properly on length.
    """
    with tempfile.TemporaryDirectory() as directory:
        logFile = LogFile("test.log", directory, 10)
        path = os.path.join(directory, "test.log")
        _writeSomeEntries(logFile)
        assert os.path.exists(f"{path}.1")
        assert not os.path.exists(f"{path}.2")
        _writeSomeEntries(logFile)
        assert os.path.exists(f"{path}.2")


def testLogReader():
    """
    Test that LogReader reads correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        logFile = LogFile("test.log", directory)
        path = os.path.join(directory, "test.log")
        _writeSomeEntries(logFile)
        logReader = LogReader(path)
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")


def testLogReaderReadLines():
    """
    Test that LogReader.readLines reads the correct number of lines.
    """
    with tempfile.TemporaryDirectory() as directory:
        logFile = LogFile("test.log", directory)
        path = os.path.join(directory, "test.log")
        _writeSomeEntries(logFile)
        logReader = LogReader(path)
        lines = logReader.readLines(5)
        assert len(lines) == 5
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 4")
        logReader.close()


def testLogFile():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        logFile = LogFile("test.log", directory)
        path = os.path.join(directory, "test.log")
        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        logFile.rotate()

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 0
        logReader.close()

        logReader = logFile.getLog(1)
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 3
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        logFile.rotate()

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 0
        logReader.close()

        logReader = logFile.getLog(1)
        lines = logReader.readLines()
        assert len(lines) == 3
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        logReader = logFile.getLog(2)
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileMaxFiles():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        logFile = LogFile("test.log", directory, maxRotatedFiles=2)
        path = os.path.join(directory, "test.log")
        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        logFile.rotate()

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 0
        logReader.close()

        logReader = logFile.getLog(1)
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 3
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        logFile.rotate()

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 0
        logReader.close()

        logReader = logFile.getLog(1)
        lines = logReader.readLines()
        assert len(lines) == 3
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        logReader = logFile.getLog(2)
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        # Rotate back to 1
        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 3
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        logFile.rotate()

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 0
        logReader.close()

        logReader = logFile.getLog(1)
        lines = logReader.readLines()
        assert len(lines) == 3
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        logReader = logFile.getLog(2)
        lines = logReader.readLines()
        assert len(lines) == 3
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        with pytest.raises(ValueError):
            logFile.getLog(3)


def testLogFileFromFullPath():
    """
    Test that LogFile.fromFullPath works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        logFile.rotate()

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 0
        logReader.close()

        logReader = logFile.getLog(1)
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithUnwritableDirectory():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(directory, 0o555)
        logFile.rotate()
        os.chmod(directory, 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testDailyLogFile():
    """
    Test that DailyLogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        logFile = DailyLogFile("test.log", directory)
        path = os.path.join(directory, "test.log")
        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        logFile.rotate()

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 0
        logReader.close()

        logReader = logFile.getLog(time.time())
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 3
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        logFile.rotate()

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 0
        logReader.close()

        logReader = logFile.getLog(time.time())
        lines = logReader.readLines()
        assert len(lines) == 3
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        logReader = logFile.getLog(time.time() - 60 * 60 * 24)
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNonExistentLog():
    """
    Attempting to retrieve a non-existent log raises a C{ValueError}.
    """
    with tempfile.TemporaryDirectory() as directory:
        logFile = LogFile("test.log", directory)

        with pytest.raises(ValueError):
            logFile.getLog(1)


def testNoUnicode():
    """
    Attempting to write bytes to a log file results in a C{DeprecationWarning}.
    """
    with tempfile.TemporaryDirectory() as directory:
        logFile = LogFile("test.log", directory)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            logFile.write(b"foo")
            assert len(w) == 1
            assert issubclass(w[-1].category, DeprecationWarning)


def testUnicode():
    """
    Unicode written to a log file is properly encoded as UTF-8.
    """
    with tempfile.TemporaryDirectory() as directory:
        logFile = LogFile("test.log", directory)

        logFile.write("\N{VULGAR FRACTION ONE HALF}")
        logFile.flush()
        logFile.write("\N{LATIN SMALL LETTER A WITH DIAERESIS}")
        logFile.flush()

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 2
        assert lines[0] == "\xc2\xbd"
        assert lines[1] == "\xc3\xa4"


def testLogFileRotateWithoutPermissions():
    """
    Test that LogFile rotate fails silently without permissions.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        os.chmod(os.path.join(directory, "sub"), 0o755)
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)
        os.chmod(os.path.join(directory, "sub"), 0o555)

        # Should fail silently
        logFile.rotate()

        assert os.path.exists(path)
        assert not os.path.exists(f"{path}.1")

        os.chmod(os.path.join(directory, "sub"), 0o755)


def testDailyLogFileRotateWithoutPermissions():
    """
    Test that DailyLogFile rotate fails silently without permissions.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        os.chmod(os.path.join(directory, "sub"), 0o755)
        path = os.path.join(directory, "sub", "test.log")
        logFile = DailyLogFile.fromFullPath(path)

        _writeSomeEntries(logFile)
        os.chmod(os.path.join(directory, "sub"), 0o555)

        # Should fail silently
        logFile.rotate()

        assert os.path.exists(path)
        assert not os.path.exists(f"{path}.{logFile.suffix(logFile.lastDate)}")

        os.chmod(os.path.join(directory, "sub"), 0o755)


def testLogFileReopenWithoutPermissions():
    """
    Test that LogFile reopen fails silently without permissions.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        os.chmod(os.path.join(directory, "sub"), 0o755)
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)
        os.chmod(os.path.join(directory, "sub"), 0o555)

        # Should fail silently
        logFile.reopen()

        assert os.path.exists(path)

        os.chmod(os.path.join(directory, "sub"), 0o755)


def testDailyLogFileReopenWithoutPermissions():
    """
    Test that DailyLogFile reopen fails silently without permissions.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        os.chmod(os.path.join(directory, "sub"), 0o755)
        path = os.path.join(directory, "sub", "test.log")
        logFile = DailyLogFile.fromFullPath(path)

        _writeSomeEntries(logFile)
        os.chmod(os.path.join(directory, "sub"), 0o555)

        # Should fail silently
        logFile.reopen()

        assert os.path.exists(path)

        os.chmod(os.path.join(directory, "sub"), 0o755)


def testLogFileFromFullPathWithNonExistentPath():
    """
    Test that LogFile.fromFullPath works correctly with a non-existent path.
    """
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        logFile.rotate()

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 0
        logReader.close()

        logReader = logFile.getLog(1)
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testDailyLogFileFromFullPathWithNonExistentPath():
    """
    Test that DailyLogFile.fromFullPath works correctly with a non-existent path.
    """
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "sub", "test.log")
        logFile = DailyLogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        logFile.rotate()

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 0
        logReader.close()

        logReader = logFile.getLog(time.time())
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testDailyLogFileFromFullPathWithNonExistentPathWithNoPermissions():
    """
    Test that DailyLogFile.fromFullPath works correctly with a non-existent path.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = DailyLogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testDailyLogFileFromFullPathWithNonExistentPathWithNoPermissionsToFile():
    """
    Test that DailyLogFile.fromFullPath works correctly with a non-existent path.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = DailyLogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(path, 0o555)
        logFile.rotate()
        os.chmod(path, 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileFromFullPathWithNonExistentPathWithNoPermissions():
    """
    Test that LogFile.fromFullPath works correctly with a non-existent path.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileFromFullPathWithNonExistentPathWithNoPermissionsToFile():
    """
    Test that LogFile.fromFullPath works correctly with a non-existent path.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(path, 0o555)
        logFile.rotate()
        os.chmod(path, 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testDailyLogFileWithNoPermissionsToFile():
    """
    Test that DailyLogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "test.log")
        logFile = DailyLogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(path, 0o555)
        logFile.rotate()
        os.chmod(path, 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testDailyLogFileWithNoPermissionsToFileAndDirectory():
    """
    Test that DailyLogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = DailyLogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNoPermissionsToFile():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(path, 0o555)
        logFile.rotate()
        os.chmod(path, 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNoPermissionsToFileAndDirectory():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNonExistentPathWithNoPermissions():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNonExistentPathWithNoPermissionsToFile():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(path, 0o555)
        logFile.rotate()
        os.chmod(path, 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testDailyLogFileWithNonExistentPathWithNoPermissions():
    """
    Test that DailyLogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = DailyLogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testDailyLogFileWithNonExistentPathWithNoPermissionsToFile():
    """
    Test that DailyLogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = DailyLogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(path, 0o555)
        logFile.rotate()
        os.chmod(path, 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNonExistentPathWithNoPermissionsToFile():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(path, 0o555)
        logFile.rotate()
        os.chmod(path, 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNonExistentPathWithNoPermissionsToFileAndDirectory():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNonExistentPathWithNoPermissionsToDirectory():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNonExistentPathWithNoPermissionsToFileAndDirectory():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNonExistentPathWithNoPermissionsToDirectoryAndFile():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNonExistentPathWithNoPermissionsToFileAndDirectoryAndFile():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNonExistentPathWithNoPermissionsToDirectoryAndFileAndFile():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNonExistentPathWithNoPermissionsToDirectoryAndFileAndFileAndFile():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNonExistentPathWithNoPermissionsToDirectoryAndFileAndFileAndFileAndFile():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNonExistentPathWithNoPermissionsToDirectoryAndFileAndFileAndFileAndFileAndFile():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNonExistentPathWithNoPermissionsToDirectoryAndFileAndFileAndFileAndFileAndFileAndFile():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNonExistentPathWithNoPermissionsToDirectoryAndFileAndFileAndFileAndFileAndFileAndFileAndFile():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNonExistentPathWithNoPermissionsToDirectoryAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFile():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNonExistentPathWithNoPermissionsToDirectoryAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFile():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNonExistentPathWithNoPermissionsToDirectoryAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFile():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNonExistentPathWithNoPermissionsToDirectoryAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFile():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNonExistentPathWithNoPermissionsToDirectoryAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFile():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNonExistentPathWithNoPermissionsToDirectoryAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFile():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 10
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 9")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        os.chmod(os.path.join(directory, "sub"), 0o555)
        logFile.rotate()
        os.chmod(os.path.join(directory, "sub"), 0o755)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 13
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()

        _writeSomeEntries(logFile, 3)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines) == 16
        assert lines[0].startswith("line 0")
        assert lines[-1].startswith("line 2")
        logReader.close()


def testLogFileWithNonExistentPathWithNoPermissionsToDirectoryAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFileAndFile():
    """
    Test that LogFile works correctly.
    """
    with tempfile.TemporaryDirectory() as directory:
        os.mkdir(os.path.join(directory, "sub"))
        path = os.path.join(directory, "sub", "test.log")
        logFile = LogFile.fromFullPath(path)

        _writeSomeEntries(logFile)

        logReader = logFile.getCurrentLog()
        lines = logReader.readLines()
        assert len(lines)