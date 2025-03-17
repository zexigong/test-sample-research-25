import os
import pytest
import tempfile
from twisted.test_logfile.test_logfile import BaseLogFile, LogFile, DailyLogFile, LogReader


class TestBaseLogFile:
    def setup_method(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_path = os.path.join(self.temp_dir.name, "logfile.log")
        self.logfile = BaseLogFile("logfile.log", self.temp_dir.name)

    def teardown_method(self):
        self.temp_dir.cleanup()

    def test_initialization(self):
        assert self.logfile.name == "logfile.log"
        assert self.logfile.directory == self.temp_dir.name
        assert self.logfile.path == self.log_path

    def test_write_and_read(self):
        self.logfile.write(b"Hello, World!")
        self.logfile.flush()
        with open(self.log_path, "rb") as f:
            content = f.read()
        assert content == b"Hello, World!"

    def test_close(self):
        self.logfile.write(b"Hello, World!")
        self.logfile.close()
        assert self.logfile.closed

    def test_reopen(self):
        self.logfile.write(b"Hello, World!")
        self.logfile.close()
        self.logfile.reopen()
        assert not self.logfile.closed
        self.logfile.write(b" More data")
        self.logfile.flush()
        with open(self.log_path, "rb") as f:
            content = f.read()
        assert content == b"Hello, World! More data"

    def test_get_current_log(self):
        reader = self.logfile.getCurrentLog()
        assert isinstance(reader, LogReader)


class TestLogFile:
    def setup_method(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.logfile = LogFile("logfile.log", self.temp_dir.name, rotateLength=10)

    def teardown_method(self):
        self.temp_dir.cleanup()

    def test_rotation(self):
        self.logfile.write(b"12345")
        self.logfile.write(b"67890")
        assert os.path.exists(self.logfile.path + ".1")
        assert not os.path.exists(self.logfile.path + ".2")

    def test_write_and_rotate(self):
        self.logfile.write(b"1234567890abc")
        self.logfile.flush()
        assert os.path.exists(self.logfile.path + ".1")
        with open(self.logfile.path, "rb") as f:
            content = f.read()
        assert content == b"abc"

    def test_max_rotated_files(self):
        self.logfile.maxRotatedFiles = 1
        self.logfile.write(b"1234567890abc")
        self.logfile.write(b"def")
        assert os.path.exists(self.logfile.path + ".1")
        assert not os.path.exists(self.logfile.path + ".2")


class TestDailyLogFile:
    def setup_method(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.logfile = DailyLogFile("dailylog.log", self.temp_dir.name)

    def teardown_method(self):
        self.temp_dir.cleanup()

    def test_daily_rotation(self):
        self.logfile.write(b"Daily log entry")
        self.logfile.flush()
        self.logfile.lastDate = self.logfile.toDate(time.time() - 86400)  # simulate a day passing
        self.logfile.write(b"New day entry")
        assert os.path.exists(self.logfile.path + "." + self.logfile.suffix(self.logfile.lastDate))
        with open(self.logfile.path, "rb") as f:
            content = f.read()
        assert content == b"New day entry"


class TestLogReader:
    def setup_method(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_path = os.path.join(self.temp_dir.name, "logfile.log")
        with open(self.log_path, "w") as f:
            f.write("line1\nline2\nline3\n")
        self.reader = LogReader(self.log_path)

    def teardown_method(self):
        self.temp_dir.cleanup()

    def test_read_lines(self):
        lines = self.reader.readLines(2)
        assert lines == ["line1\n", "line2\n"]
        lines = self.reader.readLines(2)
        assert lines == ["line3\n"]

    def test_close_reader(self):
        self.reader.close()
        assert self.reader._file.closed


if __name__ == "__main__":
    pytest.main()