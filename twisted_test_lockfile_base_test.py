import os
import pytest
from twisted.test.test_lockfile import FilesystemLock, isLocked

@pytest.fixture
def lockfile(tmp_path):
    return tmp_path / "test.lock"

def test_filesystem_lock_acquire_and_release(lockfile):
    lock = FilesystemLock(str(lockfile))

    # Lock should be acquired successfully
    assert lock.lock()
    assert lock.locked
    assert lock.clean

    # Try to acquire the same lock again, should fail
    another_lock = FilesystemLock(str(lockfile))
    assert not another_lock.lock()
    assert not another_lock.locked

    # Unlock the lock
    lock.unlock()
    assert not lock.locked

def test_filesystem_lock_cleanup_on_process_exit(lockfile):
    lock = FilesystemLock(str(lockfile))
    assert lock.lock()

    # Simulate process exit by removing lockfile manually
    os.remove(lockfile)

    # Another lock should now be able to acquire it
    another_lock = FilesystemLock(str(lockfile))
    assert another_lock.lock()

def test_filesystem_lock_unlock_not_owned(lockfile):
    lock = FilesystemLock(str(lockfile))
    assert lock.lock()

    # Simulate process exit by removing lockfile manually
    os.remove(lockfile)

    # Another process cannot unlock the lock they do not own
    with pytest.raises(ValueError):
        lock.unlock()

def test_is_locked_function(lockfile):
    lock = FilesystemLock(str(lockfile))
    assert not isLocked(str(lockfile))  # Initially should not be locked

    lock.lock()
    assert isLocked(str(lockfile))  # Should be locked after acquiring lock

    lock.unlock()
    assert not isLocked(str(lockfile))  # Should not be locked after unlocking