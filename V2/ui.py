#
# Copyright (c) 2018 Mathieu Bouzard.
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
from PySide2.QtCore import *
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import *


class Ui(QWidget):
    def __init__(self, controller, name, parent=None):
        QWidget.__init__(self, parent)
        self.controller = controller
        #  create window
        self.setWindowTitle(name)

        icon = QIcon(self.controller.get_icon())
        self.setWindowIcon(icon)
        self.setMinimumWidth(150)
        self.move(75, 175)
        self.setWindowFlags(Qt.Window)
        self.action = 0

        # create widgets

        title_lbl = QLabel("Tetris for maya")
        self.start_btn = QPushButton("Start game")

        # create layout

        main_layout = QVBoxLayout()

        # connect layout

        main_layout.addWidget(title_lbl)
        main_layout.addWidget(self.start_btn)

        self.setLayout(main_layout)
        # connect widget

        self.start_btn.clicked.connect(self.start_game)

    def start_game(self):
        self.controller.start_game()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            print("up")
            self.action = 1
        elif event.key() == Qt.Key_Down:
            print("down")
            self.action = 2
        elif event.key() == Qt.Key_Left:
            print("left")
            self.action = 3
        elif event.key() == Qt.Key_Right:
            print("right")
            self.action = 4
