import threading
from contextlib import contextmanager


# source: https://www.oreilly.com/library/view/python-cookbook/0596001673/ch06s04.html
class ReadWriteLock:
    """A lock object that allows many simultaneous "read locks", but
    only one "write lock." """

    def __init__(self):
        self._read_ready = threading.Condition(threading.Lock())
        self._readers = 0
        self._write_locked = False

    def try_acquire_read(self, timeout):
        acquired = self._read_ready.acquire(blocking=True, timeout=timeout)
        if not acquired:
            print("not acquired, returning False")
            return False
        self._acquire_read_core()
        return True

    def acquire_read(self):
        """Acquire a read lock. Blocks only if a thread has
        acquired the write lock."""
        self._read_ready.acquire(blocking=True)
        self._acquire_read_core()

    def _acquire_read_core(self):
        try:
            self._readers += 1
        finally:
            self._read_ready.release()

    def release_read(self):
        """Release a read lock."""
        self._read_ready.acquire(blocking=True)
        try:
            self._readers -= 1
            if not self._readers:
                self._read_ready.notify_all()
        finally:
            self._read_ready.release()

    @contextmanager
    def read_locked(self):
        """This method is designed to be used via the `with` statement."""
        try:
            self.acquire_read()
            yield
        finally:
            self.release_read()

    @contextmanager
    def read_locked_timeout(self, timeout=1):
        """This method is designed to be used via the `with` statement.
        check return value: returns True only if lock is acquired
        """
        result = self.try_acquire_read(timeout=timeout)
        try:
            if result:
                yield result
            else:
                # return the result even if false rather than throw an exception, caller needs to check the result
                yield result

        finally:
            if result:
                self.release_read()

    @contextmanager
    def try_read_locked(self, timeout=10):
        """This method is designed to be used via the `with` statement."""
        try:
            self.acquire_read()
            yield
        finally:
            self.release_read()

    def acquire_write(self):
        """Acquire a write lock. Blocks until there are no
        acquired read or write locks."""
        self._read_ready.acquire(blocking=True)
        while self._readers > 0:
            self._read_ready.wait()
        self._write_locked = True

    def release_write(self):
        """Release a write lock."""
        self._read_ready.release()
        self._write_locked = False

    @contextmanager
    def write_locked(self):
        """This method is designed to be used via the with statement"""
        try:
            self.acquire_write()
            yield
        finally:
            self.release_write()
