# ---------------------Tetris For Maya----------------------------------
#
# Version : 2.0
#
# Warnings:
#     - Only work on Maya 2017-2020
#     - This version requires a separate venv that will launch the keyboard catcher
#
#
# Copyright (c) 2018 Mathieu Bouzard.
#
# This file is part of Tetris Maya 
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
