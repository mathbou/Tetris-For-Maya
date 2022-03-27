from PySide2.QtWidgets import QMainWindow
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
import maya.cmds as mc
import time

__all__ = ["get_main_window", "hud_countdown"]


def get_main_window() -> QMainWindow:
    maya_main_window_ptr = omui.MQtUtil.mainWindow()

    ptr = int(maya_main_window_ptr)
    maya_main_window = wrapInstance(ptr, QMainWindow)

    return maya_main_window


def hud_countdown(msg: str, sec: int = 3):
    assert sec > 0

    for i in range(sec):
        mc.headsUpMessage("{}: {}".format(msg, sec - i), time=1)
        time.sleep(1)
