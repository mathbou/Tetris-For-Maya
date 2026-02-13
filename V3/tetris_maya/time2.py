#
# Copyright (c) 2025 Mathieu Bouzard.
#
# This file is part of Tetris For Maya
# (see https://gitlab.com/mathbou/TetrisMaya).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import ctypes
import platform
import sys
from contextlib import contextmanager

__all__ = ["timer_precision"]


@contextmanager
def timer_precision(ms: int = 1):
    """Force higher precision timer on Windows.

    References:
        https://stackoverflow.com/a/43505033
    """
    is_win = platform.system() == "Windows"

    if is_win and sys.version_info < (3, 11):
        winmm = ctypes.WinDLL("winmm")
        winmm.timeBeginPeriod(ms)

        try:
            yield
        finally:
            winmm.timeEndPeriod(ms)

    else:
        yield
