from contextlib import contextmanager
import ctypes

__all__ = ["timer_precision"]


@contextmanager
def timer_precision(ms: int = 1):
    """Force higher precision timer on Windows.

    References:
        https://stackoverflow.com/a/43505033
    """
    winmm = ctypes.WinDLL('winmm')
    winmm.timeBeginPeriod(ms)

    try:
        yield
    finally:
        winmm.timeEndPeriod(ms)