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

from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING
from unittest.mock import patch

import maya.cmds as mc
from maya.app.type import typeToolSetup

from .constants import PREFIX
from .rlib import Grid as BaseGrid

if TYPE_CHECKING:
    from .tetrimino import Tetrimino

__all__ = ["Grid", "Hold"]


class Hold(IntEnum):
    CANT = 0
    PUSH = 1
    SWAP = 2


class Grid(BaseGrid):
    def __init__(self):
        self._make_background()
        self._make_square("Next", self.NEXT_POS)
        self._make_square("Hold", self.HOLD_POS)
        mc.refresh()

        super().__init__()

        self._next_tetrimino: Tetrimino | None = None
        self._hold_tetrimino: Tetrimino | None = None
        self._can_hold: bool = True

    @classmethod
    def _make_background(cls):
        bg_group = mc.group(name=f"{PREFIX}_background_grp", empty=1)
        for x in range(cls.COLUMN_COUNT):
            for y in range(cls.ROW_COUNT):
                bg_cube = mc.polyCube(
                    width=1,
                    height=1,
                    depth=1,
                    subdivisionsX=1,
                    subdivisionsY=1,
                    subdivisionsZ=1,
                    createUVs=False,
                    constructionHistory=False,
                    name=f"{PREFIX}_background{x:02}{y:02}_geo",
                )[0]
                mc.polyBevel3(
                    f"{bg_cube}.e[0:11]",
                    segments=1,
                    constructionHistory=False,
                    offset=0.05,
                    offsetAsFraction=False,
                    worldSpace=True,
                    angleTolerance=30,
                )
                mc.move(x, y, -1, bg_cube, absolute=1)
                mc.parent(bg_cube, bg_group)

    @classmethod
    def _make_square(cls, text: str, position: tuple[float, float, float]):
        square = mc.polyTorus(
            radius=3.2,
            sectionRadius=0.3,
            twist=0,
            subdivisionsX=4,
            subdivisionsY=3,
            createUVs=False,
            constructionHistory=False,
            name=f"{PREFIX}_square_geo",
        )
        mc.move(*position, square, absolute=True)
        mc.rotate("90deg", 0, "-45deg", square, absolute=True)

        # --------- Square title ---------

        type_node = mc.createNode("type", n="type#", skipSelect=True)

        with patch("maya.app.type.typeToolSetup.IN_BATCH_MODE", new=True):  # avoid AE to be shown after `type` creation
            type_node = typeToolSetup.createTypeToolWithNode(type_node, text=text)

        type_extrude_node = mc.listConnections(type_node, type="typeExtrude")[0]

        mc.setAttr(f"{type_extrude_node}.enableExtrusion", False)  # noqa: FBT003
        mc.setAttr(f"{type_node}.alignmentMode", 2)  # center
        mc.setAttr(f"{type_node}.fontSize", 1.125)

        type_transform = mc.listConnections(type_node, type="transform")[0]
        mc.move(*position, type_transform, absolute=True)
        mc.move(0, 3, 0, type_transform, relative=True)
        mc.rename(type_transform, f"{PREFIX}_{type_transform}")

    def _move_to_start(self, tetrimino: Tetrimino):
        mc.move(self.COLUMN_COUNT / 2 - 1, self.TOP, 0, tetrimino.root, absolute=True)
        mc.scale(1, 1, 1, tetrimino.root, absolute=True)

    def _move_to_next(self, tetrimino: Tetrimino):
        translation = [h - t for t, h in zip(mc.objectCenter(tetrimino.root), self.NEXT_POS)]
        mc.move(*translation, tetrimino.root, absolute=True)
        mc.scale(0.85, 0.85, 0.85, tetrimino.root, absolute=True)

    def put_to_next(self, tetrimino: Tetrimino):
        if self._next_tetrimino:
            self.active_tetrimino = self._next_tetrimino
            self._move_to_start(self.active_tetrimino)

        self._next_tetrimino = tetrimino
        self._move_to_next(self._next_tetrimino)
        mc.refresh()

    def _move_to_hold(self, tetrimino: Tetrimino):
        local_center = [c - p for c, p in zip(mc.objectCenter(tetrimino.root), tetrimino.position)]  # only return x, y
        translation = [h - c for h, c in zip(self.HOLD_POS, local_center)]
        mc.move(*translation, 0, tetrimino.root, absolute=True)
        mc.scale(0.85, 0.85, 0.85, tetrimino.root, absolute=True)

    def reset_hold(self):
        self._can_hold = True

    def hold(self) -> Hold:
        if self._can_hold:
            exit_code = Hold.PUSH
            backup = self.active_tetrimino

            if self._hold_tetrimino:
                self.active_tetrimino = self._hold_tetrimino
                self._move_to_start(self.active_tetrimino)
                exit_code = Hold.SWAP

            self._hold_tetrimino = backup
            self._can_hold = False
            self._move_to_hold(self._hold_tetrimino)
            mc.refresh()

            return exit_code
        return Hold.CANT
