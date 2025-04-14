# Copyright (c) 2005 Divmod, Inc.
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from os import rename, symlink, unlink, rmdir
import os
import errno
import sys

from twisted.python.runtime import platform

from twisted.trial import unittest
from twisted.python import lockfile

if platform.isWindows():
    raise unittest.SkipTest("lockfile does not work on Windows.")

# The lock object to use in tests.
class BaseTests:
    def setUp(self):
        self.tmp = self.mktemp()
        self.lock = lockfile.FilesystemLock(self.tmp)

    def tearDown(self):
        try:
            os.unlink(self.tmp)
        except:
            pass

    def testLock(self):
        self.assertTrue(self.lock.lock())
        self.assertTrue(self.lock.locked)
        self.assertRaises(OSError, self.lock.lock)

    def testUnlock(self):
        self.lock.lock()
        self.lock.unlock()
        self.assertFalse(self.lock.locked)
        self.assertTrue(self.lock.lock())
        self.lock.unlock()

    def testDoubleUnlock(self):
        self.lock.lock()
        self.lock.unlock()
        self.assertRaises(ValueError, self.lock.unlock)

    def testNotOwnedUnlock(self):
        self.lock.lock()
        if platform.isWindows():
            # On Windows, symlink is simulated by writing a file. Since a file
            # can't be owned by more than one process, just exit.
            return
        try:
            unlink(self.tmp)
        except:
            pass
        symlink(str(os.getpid() + 1), self.tmp)
        self.assertRaises(ValueError, self.lock.unlock)

    def testIsLocked(self):
        self.assertFalse(lockfile.isLocked(self.tmp))
        self.lock.lock()
        self.assertTrue(lockfile.isLocked(self.tmp))
        self.lock.unlock()
        self.assertFalse(lockfile.isLocked(self.tmp))

    def testCleanLock(self):
        self.assertTrue(self.lock.lock())
        self.assertTrue(self.lock.clean)
        self.lock.unlock()

    def testUncleanLock(self):
        self.assertTrue(self.lock.lock())
        self.lock.unlock()
        if platform.isWindows():
            # On Windows, symlink is simulated by writing a file. Since a file
            # can't be owned by more than one process, just exit.
            return
        try:
            unlink(self.tmp)
        except:
            pass
        symlink(str(os.getpid()), self.tmp)
        self.assertTrue(self.lock.lock())
        self.assertFalse(self.lock.clean)
        self.lock.unlock()


class FilesystemLockTests(BaseTests, unittest.TestCase):
    pass


class UnicodeTests(BaseTests, unittest.TestCase):
    def setUp(self):
        self.tmp = self.mktemp() + "üñîçø∂€"
        self.lock = lockfile.FilesystemLock(self.tmp)

    def tearDown(self):
        try:
            os.unlink(self.tmp)
        except:
            pass


class UnicodeTests(BaseTests, unittest.TestCase):
    def setUp(self):
        self.tmp = self.mktemp() + "üñîçø∂€"
        self.lock = lockfile.FilesystemLock(self.tmp)

    def tearDown(self):
        try:
            os.unlink(self.tmp)
        except:
            pass