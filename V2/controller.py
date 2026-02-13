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
import os

from tetris import Tetris


class Controller(object):
    def __init__(self, ui, name, parent=None):
        self.ui = ui(self, name, parent)

    def show(self):
        self.ui.show()

    def start_game(self):
        tetris = Tetris()
        tetris.launch_game_process()

    def get_icon(self):
        icon_path = "{0}/ressources/logo.ico".format(os.path.dirname(os.path.abspath(__file__)))
        return icon_path
