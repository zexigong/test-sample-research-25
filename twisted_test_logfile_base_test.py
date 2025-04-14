# -*- test-case-name: twisted.test.test_logfile -*-

import os
import time
from twisted.trial import unittest
from twisted.test.test_logfile import BaseLogFile, LogFile, DailyLogFile, LogReader


class BaseLogFileTests(unittest.TestCase):
    def setUp(self):
        self.directory = "test_logs"
        os.makedirs(self.directory, exist_ok=True)
        self.filename = "test_log.log"
        self.filepath = os.path.join(self.directory, self.filename)

    def tearDown(self):
        for file in os.listdir(self.directory):
            os.remove(os.path.join(self.directory, file))
        os.rmdir(self.directory)

    def test_create_log_file(self):
        logFile = BaseLogFile(self.filename, self.directory)
        self.assertTrue(os.path.exists(self.filepath))
        logFile.close()

    def test_write_to_log_file(self):
        logFile = BaseLogFile(self.filename, self.directory)
        logFile.write("Test log entry")
        logFile.flush()
        logFile.close()

        with open(self.filepath, "rb") as f:
            content = f.read()
        self.assertIn(b"Test log entry", content)

    def test_reopen_log_file(self):
        logFile = BaseLogFile(self.filename, self.directory)
        logFile.write("Test log entry")
        logFile.flush()
        logFile.close()

        logFile.reopen()
        self.assertFalse(logFile.closed)
        logFile.write("Another entry")
        logFile.flush()
        logFile.close()

        with open(self.filepath, "rb") as f:
            content = f.read()
        self.assertIn(b"Another entry", content)


class LogFileTests(unittest.TestCase):
    def setUp(self):
        self.directory = "test_logs"
        os.makedirs(self.directory, exist_ok=True)
        self.filename = "test_log.log"
        self.filepath = os.path.join(self.directory, self.filename)

    def tearDown(self):
        for file in os.listdir(self.directory):
            os.remove(os.path.join(self.directory, file))
        os.rmdir(self.directory)

    def test_log_rotation(self):
        logFile = LogFile(self.filename, self.directory, rotateLength=10)
        logFile.write("12345")
        logFile.flush()
        logFile.write("67890")
        logFile.flush()
        self.assertTrue(os.path.exists(self.filepath))
        self.assertTrue(os.path.exists(f"{self.filepath}.1"))
        logFile.close()

    def test_max_rotated_files(self):
        logFile = LogFile(self.filename, self.directory, rotateLength=10, maxRotatedFiles=2)
        logFile.write("12345")
        logFile.flush()
        logFile.write("67890")
        logFile.flush()
        logFile.write("abcde")
        logFile.flush()
        self.assertTrue(os.path.exists(self.filepath))
        self.assertTrue(os.path.exists(f"{self.filepath}.1"))
        self.assertTrue(os.path.exists(f"{self.filepath}.2"))
        self.assertFalse(os.path.exists(f"{self.filepath}.3"))
        logFile.close()


class DailyLogFileTests(unittest.TestCase):
    def setUp(self):
        self.directory = "test_logs"
        os.makedirs(self.directory, exist_ok=True)
        self.filename = "test_log.log"
        self.filepath = os.path.join(self.directory, self.filename)

    def tearDown(self):
        for file in os.listdir(self.directory):
            os.remove(os.path.join(self.directory, file))
        os.rmdir(self.directory)

    def test_daily_rotation(self):
        logFile = DailyLogFile(self.filename, self.directory)
        logFile.write("Test log entry")
        logFile.flush()
        logFile.rotate()
        self.assertTrue(os.path.exists(self.filepath))
        suffix = logFile.suffix(logFile.lastDate)
        self.assertTrue(os.path.exists(f"{self.filepath}.{suffix}"))
        logFile.close()

    def test_no_rotation_on_same_day(self):
        logFile = DailyLogFile(self.filename, self.directory)
        logFile.write("Test log entry")
        logFile.flush()
        logFile.rotate()
        suffix = logFile.suffix(logFile.lastDate)
        logFile.write("Another entry")
        logFile.flush()
        logFile.rotate()
        self.assertFalse(os.path.exists(f"{self.filepath}.{suffix}"))
        logFile.close()


class LogReaderTests(unittest.TestCase):
    def setUp(self):
        self.directory = "test_logs"
        os.makedirs(self.directory, exist_ok=True)
        self.filename = "test_log.log"
        self.filepath = os.path.join(self.directory, self.filename)

    def tearDown(self):
        for file in os.listdir(self.directory):
            os.remove(os.path.join(self.directory, file))
        os.rmdir(self.directory)

    def test_read_lines(self):
        with open(self.filepath, "wb") as f:
            f.write(b"Line 1\nLine 2\nLine 3\n")

        logReader = LogReader(self.filepath)
        lines = logReader.readLines(2)
        self.assertEqual(lines, ["Line 1\n", "Line 2\n"])
        logReader.close()