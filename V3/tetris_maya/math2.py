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
from __future__ import annotations

import math

__all__ = ["absmax", "rotate_point"]


def rotate_point(point: tuple[float, float], angle: float, origin: tuple[float, float] = (0, 0)) -> tuple[float, float]:
    """2D rotation on XY plane

    Args:
        origin:
        point:
        angle: Radians

    Returns:
        New (x, y) position after rotation.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)

    return qx, qy


def absmax(a: float, b: float) -> float:
    """Get the absolute highest number.

    Returns:
        Absolute highest number.

    Examples:
        >>> absmax(-3, 2)
        -3

        >>> absmax(3, 2)
        3

    """
    if abs(a) > abs(b):
        return a
    return b
