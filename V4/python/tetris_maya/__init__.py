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

# ---------------------Tetris For Maya----------------------------------
#
# Version : 4.0.0
#
# Warnings:
#     Works on Maya 2022+
#

from pathlib import Path

import maya.mel as mel
import pkg_resources

from . import rlib
from .game import Game

__doc__ = rlib.__doc__
if hasattr(rlib, "__all__"):
    __all__ = rlib.__all__


def launch():
    Game.start()


def install_shelf():
    shelf_location = Path(pkg_resources.resource_filename("tetris_maya", "resources/shelf_Tetris.mel"))
    mel.eval(f'loadNewShelf "{shelf_location.as_posix()}"')
