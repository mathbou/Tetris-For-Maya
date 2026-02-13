import time
from typing import Any

import maya.cmds as mc
from maya import OpenMayaUI as omui  # noqa: N813
from PySide2.QtWidgets import QMainWindow
from shiboken2 import wrapInstance

__all__ = ["get_main_window", "hud_countdown"]


def get_main_window() -> QMainWindow:
    maya_main_window_ptr = omui.MQtUtil.mainWindow()

    ptr = int(maya_main_window_ptr)

    return wrapInstance(ptr, QMainWindow)


def hud_countdown(msg: str, sec: int = 3):
    """.

    Raises:
        ValueError: If sec is negative.
    """
    if not sec > 0:
        raise ValueError("Countdown can't be negative")

    for i in range(sec):
        mc.headsUpMessage("{}: {}".format(msg, sec - i), time=1)
        time.sleep(1)


class HeadsUpDisplay:
    def __init__(self, name: str):
        self._name = name

    @classmethod
    def add(cls, name: str, block: int, section: int, **kwargs: Any):
        mc.HeadsUpDisplay(name, block=block, section=section, **kwargs)

        return cls(name)

    def remove(self):
        mc.HeadsUpDisplay(self._name, remove=True)
