from twisted.trial import unittest
from twisted.test.test_lockfile import FilesystemLock, isLocked
import os
from unittest.mock import patch, MagicMock


class FilesystemLockTests(unittest.TestCase):
    def setUp(self):
        self.lockfile = "test.lock"
        self.lock = FilesystemLock(self.lockfile)

    def tearDown(self):
        if os.path.exists(self.lockfile):
            try:
                os.remove(self.lockfile)
            except Exception:
                pass

    def test_lock_acquire(self):
        result = self.lock.lock()
        self.assertTrue(result)
        self.assertTrue(self.lock.locked)
        self.assertTrue(os.path.exists(self.lockfile))

    def test_lock_acquire_fail(self):
        with patch("os.symlink", side_effect=OSError(errno.EEXIST, "File exists")):
            result = self.lock.lock()
            self.assertFalse(result)
            self.assertFalse(self.lock.locked)

    def test_unlock(self):
        self.lock.lock()
        self.lock.unlock()
        self.assertFalse(self.lock.locked)
        self.assertFalse(os.path.exists(self.lockfile))

    def test_unlock_not_owned(self):
        self.lock.lock()
        with patch("os.getpid", return_value=99999):
            with self.assertRaises(ValueError):
                self.lock.unlock()

    def test_isLocked_true(self):
        self.lock.lock()
        self.assertTrue(isLocked(self.lockfile))

    def test_isLocked_false(self):
        self.assertFalse(isLocked(self.lockfile))

    def test_lock_clean_release(self):
        self.lock.lock()
        self.lock.unlock()
        self.assertTrue(self.lock.clean)

    def test_lock_unclean_release(self):
        with patch("os.readlink", side_effect=OSError(errno.ENOENT, "No such file or directory")):
            self.lock.lock()
            self.assertFalse(self.lock.clean)