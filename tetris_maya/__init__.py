# ---------------------Tetris For Maya----------------------------------
#
# Version : 3.0.0
#
# Warnings:
#     Only work on Maya 2022+
#
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
from __future__ import absolute_import, unicode_literals

import os.path

import maya.mel as mel

from .game import Game


def launch():
    Game.start()


def install_shelf():
    parent = os.path.dirname(__file__)
    shelf_location = os.path.normpath(os.path.join(parent, "resources", "shelf_Tetris.mel")).replace(os.sep, "/")
    mel.eval('loadNewShelf "{}"'.format(shelf_location))
