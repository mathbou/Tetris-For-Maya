# Copyright (c) 2025 Mathieu Bouzard.
#
# This file is part of Tetris For Maya
# (see https://gitlab.com/mathbou/TetrisMaya).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import time
from typing import Any

import maya.cmds as mc
from maya import OpenMayaUI as OpenMayaUI

try:
    from PySide2.QtWidgets import QMainWindow
    from shiboken2 import wrapInstance
except ImportError:
    from PySide6.QtWidgets import QMainWindow
    from shiboken6 import wrapInstance

__all__ = ["get_main_window", "hud_countdown"]


def get_main_window() -> QMainWindow:
    maya_main_window_ptr = OpenMayaUI.MQtUtil.mainWindow()

    ptr = int(maya_main_window_ptr)

    return wrapInstance(ptr, QMainWindow)


def hud_countdown(msg: str, sec: int = 3):
    """Show a countdown.

    Raises:
        ValueError: If sec is negative.
    """
    if not sec > 0:
        raise ValueError("Countdown can't be negative")

    for i in range(sec):
        mc.headsUpMessage(f"{msg}: {sec - i}", time=1)
        time.sleep(1)


class HeadsUpDisplay:
    def __init__(self, name: str):
        self._name = name

    @classmethod
    def add(cls, name: str, block: int, section: int, **kwargs: Any) -> "HeadsUpDisplay":
        mc.headsUpDisplay(name, block=block, section=section, **kwargs)

        return cls(name)

    def remove(self):
        mc.headsUpDisplay(self._name, remove=True)


def remove_empty_groups(pattern: str):
    groups = mc.ls(pattern, exactType="transform")
    for grp in groups:
        if not mc.listRelatives(grp, children=True):
            mc.delete(grp)
