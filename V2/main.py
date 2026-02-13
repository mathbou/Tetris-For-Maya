"""
---------------------Tetris For Maya----------------------------------


Author: Mathieu BOUZARD
Date : 03-2018
Version : 2.0

Warnings:
    Only work on Maya 2017-2020

This version requires a separate venv that will launch the keyboard catcher

---------------------------------------------------------------------
"""
import maya.OpenMayaUI as mui
import shiboken2
from PySide2 import QtWidgets
from controller import Controller
from ui import Ui

if __name__ == "__main__":
    # define names
    window_title = "Tetris"
    # get maya window
    ptr = mui.MQtUtil.mainWindow()
    parent = shiboken2.wrapInstance(long(ptr), QtWidgets.QWidget)

    # create window
    window = Controller(Ui, "Tetris", parent)
    window.show()
