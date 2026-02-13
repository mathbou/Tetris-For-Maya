import math
from typing import Tuple

__all__ = ["rotate_point", "absmax"]


def rotate_point(point: Tuple[float, float], angle: float, origin: Tuple[float, float] = (0,0)) -> Tuple[float, float]:
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


def absmax(a: float, b: float) -> float:
    """Returns the absolute highest number.

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