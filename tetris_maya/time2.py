from contextlib import contextmanager
import ctypes
import platform

__all__ = ["timer_precision"]


@contextmanager
def timer_precision(ms: int = 1):
    """Force higher precision timer on Windows.

    References:
        https://stackoverflow.com/a/43505033
    """
    is_win = platform.system() == "Windows"

    if is_win:
        winmm = ctypes.WinDLL('winmm')
        winmm.timeBeginPeriod(ms)

        try:
            yield
        finally:
            winmm.timeEndPeriod(ms)

    else:
        yield