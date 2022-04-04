#
# Copyright (c) 2022 Mathieu Bouzard.
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
from __future__ import absolute_import
from __future__ import unicode_literals

import math

__all__ = ["rotate_point", "absmax"]


def rotate_point(point, angle, origin = (0, 0)):
    # type: (tuple[float, float], float, tuple[float, float]) -> tuple[float, float]
    """2D rotation on XY plane

    Args:
        origin:
        point:
        angle: Radians

    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)

    return qx, qy


def absmax(a, b):
    # type: (float, float) -> float
    """Get the absolute highest number.

    Examples:
        >>> absmax(-3, 2)
        -3

        >>> absmax(3, 2)
        3

    """
    if abs(a) > abs(b):
        return a
    else:
        return b
