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
from __future__ import absolute_import, division, unicode_literals, with_statement

import math
from itertools import ifilter, imap, izip

import maya.cmds as mc
from maya.app.type import typeToolSetup

from .constants import PREFIX
from .enum import IntEnum
from .math2 import absmax, rotate_point
from .tetrimino import O, Tetrimino

# from unittest.mock import patch



__all__ = ["Grid", "Hold"]


class Hold(IntEnum):
    CANT = 0
    PUSH = 1
    SWAP = 2


class Grid(object):
    ROW_COUNT = 20  # type: ClassVar[int]
    COLUMN_COUNT = 10  # type: ClassVar[int]

    TOP = ROW_COUNT - 1  # type: ClassVar[int]
    BOTTOM = 0  # type: ClassVar[int]
    LEFT = 0  # type: ClassVar[int]
    RIGHT = COLUMN_COUNT - 1  # type: ClassVar[int]

    NEXT_POS = (12.5, 15, -1)  # type: ClassVar[tuple[float, float, float]]
    HOLD_POS = (-3.5, 15, -1)  # type: ClassVar[tuple[float, float, float]]

    def __init__(self):
        self._make_background()
        self._make_square("Next", self.NEXT_POS)
        self._make_square("Hold", self.HOLD_POS)
        mc.refresh()

        self._matrix = [
            [None] * self.COLUMN_COUNT for _ in xrange(self.ROW_COUNT)
        ]  # type: list[list[Optional[unicode]]]

        self.active_tetrimino = None  # type: Optional[Tetrimino]
        self._next_tetrimino = None  # type: Optional[Tetrimino]

        self._hold_tetrimino = None  # type: Optional[Tetrimino]
        self._can_hold = True  # type: bool

    @classmethod
    def _make_background(cls):
        bg_group = mc.group(name="{}_background_grp".format(PREFIX), empty=1)
        for x in xrange(cls.COLUMN_COUNT):
            for y in xrange(cls.ROW_COUNT):
                bg_cube = mc.polyCube(
                    width=1,
                    height=1,
                    depth=1,
                    subdivisionsX=1,
                    subdivisionsY=1,
                    subdivisionsZ=1,
                    createUVs=False,
                    constructionHistory=False,
                    name="{}_background{:02}{:02}_geo".format(PREFIX, x, y),
                )[0]
                mc.polyBevel3(
                    "{}.e[0:11]".format(bg_cube),
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
    def _make_square(cls, text, position):
        # type: (str, tuple[float, float, float]) -> None
        square = mc.polyTorus(
            radius=3.2,
            sectionRadius=0.3,
            twist=0,
            subdivisionsX=4,
            subdivisionsY=3,
            createUVs=False,
            constructionHistory=False,
            name="{}_square_geo".format(PREFIX),
        )
        x, y, z = position
        mc.move(x, y, z, square, absolute=True)
        mc.rotate("90deg", 0, "-45deg", square, absolute=True)

        # --------- Square title ---------

        type_node = mc.createNode("type", n="type#", skipSelect=True)

        typeToolSetup.IN_BATCH_MODE = True  # avoid AE to be shown after `type` creation
        type_node = typeToolSetup.createTypeToolWithNode(type_node, text=text)
        typeToolSetup.IN_BATCH_MODE = False

        type_extrude_node = mc.listConnections(type_node, type="typeExtrude")[0]

        mc.setAttr("{}.enableExtrusion".format(type_extrude_node), False)
        mc.setAttr("{}.alignmentMode".format(type_node), 2)  # center
        mc.setAttr("{}.fontSize".format(type_node), 1.125)

        type_transform = mc.listConnections(type_node, type="transform")[0]
        mc.move(x, y, z, type_transform, absolute=True)
        mc.move(0, 3, 0, type_transform, relative=True)
        mc.rename(type_transform, "{}_{}".format(PREFIX, type_transform))

    # --------------- CHECKERS ---------------

    def inside_grid(self, x, y):
        # type: (int, int) -> bool
        horizontally_inside = self.LEFT <= x <= self.RIGHT
        vertically_inside = self.BOTTOM <= y <= self.TOP

        return vertically_inside and horizontally_inside

    def cell_is_available(self, x, y, whitelist=None):
        # type: (int, int, list[str]) -> bool
        whitelist = list(whitelist) or []
        whitelist.append(None)

        cell = self._matrix[y][x]

        return cell in whitelist

    def cells_are_available(self, positions, whitelist=None, offset_x=0, offset_y=0):
        # type: (list[tuple[int, int]], tuple[str, ...], int, int) -> bool
        for (x, y) in positions:
            ox, oy = imap(int, (x + offset_x, y + offset_y))

            if not self.inside_grid(ox, oy):
                return False

            elif not self.cell_is_available(ox, oy, whitelist=whitelist):
                return False

        return True

    def can_move_to(self, tetrimino, x, y):
        # type: (Tetrimino, int, int) -> bool
        """.

        Args:
            tetrimino:
            x: offset applied to the tetrimino
            y: offset applied to the tetrimino
        """
        return self.cells_are_available(tetrimino.cube_positions, whitelist=tetrimino.cubes, offset_x=x, offset_y=y)

    def inplace_collision(self, tetrimino):
        # type: (Tetrimino) -> bool
        return not self.can_move_to(tetrimino, 0, 0)

    # --------------- ACTIONS ---------------

    def move(self, tetrimino, x, y):
        # type: (Tetrimino, int, int) -> bool
        if self.can_move_to(tetrimino, x, y):
            mc.move(x, y, 0, tetrimino.root, relative=1)
            mc.refresh()
            return True
        return False

    def rotate(self, tetrimino, angle=-90):
        # type: (Tetrimino, int) -> bool
        if tetrimino.type == O.name:
            return False

        origin_x, origin_y = tetrimino.position
        new_cube_pos = []  # type: list[tuple[int, int]]

        global_offset_x, global_offset_y = 0, 0

        # ------ COMPUTE ------
        for cx, cy in tetrimino.cube_positions:
            rx, ry = imap(round, rotate_point(point=(cx, cy), angle=math.radians(angle), origin=(origin_x, origin_y)))

            if not self.inside_grid(rx, ry):
                item_offset_x = max(self.LEFT, min(rx, self.RIGHT)) - rx
                global_offset_x = absmax(item_offset_x, global_offset_x)

                item_offset_y = max(self.BOTTOM, min(ry, self.TOP)) - ry
                global_offset_y = absmax(item_offset_y, global_offset_y)

            new_cube_pos.append((rx, ry))

        # ------ CHECK ------
        if not self.cells_are_available(
            new_cube_pos, tetrimino.cubes, offset_x=global_offset_x, offset_y=global_offset_y
        ):
            for ox in (-1, 1, -2, 2):  # check if left or right move is possible
                if self.cells_are_available(
                    new_cube_pos, tetrimino.cubes, offset_x=global_offset_x + ox, offset_y=global_offset_y
                ):
                    global_offset_x += ox
                    break
            else:
                return False

        # ------ APPLY ------
        for cube, (x, y) in izip(tetrimino.cubes, new_cube_pos):
            mc.move(x, y, 0, cube, worldSpace=True, absolute=True)

        mc.move(global_offset_x, global_offset_y, 0, tetrimino.root, relative=True)
        mc.refresh()

        return True

    def _move_to_start(self, tetrimino):
        # type: (Tetrimino) -> None
        mc.move(self.COLUMN_COUNT / 2 - 1, self.TOP, 0, tetrimino.root, absolute=True)
        mc.scale(1, 1, 1, tetrimino.root, absolute=True)

    def _move_to_next(self, tetrimino):
        # type: (Tetrimino) -> None
        x, y, z = [h - t for t, h in izip(mc.objectCenter(tetrimino.root), self.NEXT_POS)]
        mc.move(x, y, z, tetrimino.root, absolute=True)
        mc.scale(0.85, 0.85, 0.85, tetrimino.root, absolute=True)

    def put_to_next(self, tetrimino):
        # type: (Tetrimino) -> None
        if self._next_tetrimino:
            self.active_tetrimino = self._next_tetrimino
            self._move_to_start(self.active_tetrimino)

        self._next_tetrimino = tetrimino
        self._move_to_next(self._next_tetrimino)
        mc.refresh()

    def _move_to_hold(self, tetrimino):
        # type: (Tetrimino) -> None
        local_center = [c - p for c, p in izip(mc.objectCenter(tetrimino.root), tetrimino.position)]  # only return x, y
        x, y = [h - c for h, c in izip(self.HOLD_POS, local_center)]
        mc.move(x, y, 0, tetrimino.root, absolute=True)
        mc.scale(0.85, 0.85, 0.85, tetrimino.root, absolute=True)

    def reset_hold(self):
        self._can_hold = True

    def hold(self):
        # type: () -> Hold
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
        else:
            return Hold.CANT

    def update_cells(self, tetrimino):
        # type: (Tetrimino) -> None
        mc.refresh()
        for cube, (x, y) in izip(tetrimino.cubes, tetrimino.cube_positions):
            self._matrix[int(y)][int(x)] = cube

    def process_completed_rows(self):
        # type: () -> int
        """Check the grid for completed rows. Delete them and move down the others if possible."""
        row_id = 0
        completed_rows = 0

        while row_id < self.ROW_COUNT:
            row = list(ifilter(None, self._matrix[row_id]))
            row_is_complete = len(row) == self.COLUMN_COUNT

            if row_is_complete:
                completed_rows += 1
                mc.delete(row)

                moved_down = self._move_down_rows(from_row=row_id)

                # must roll back on previous index if cubes were moved down
                row_id = row_id - int(moved_down)

            row_id += 1

        return completed_rows

    def _move_down_rows(self, from_row):
        # type: (int) -> bool
        """Move down rows and update grid data.

        Warnings:
            Does not check if `from_row` is an empty row.

        """
        moved_down = False

        row_id = from_row + 1
        while row_id < self.ROW_COUNT:
            row = list(ifilter(None, self._matrix[row_id]))

            if row:
                mc.move(0, -1, 0, row, relative=1)

                self._matrix[row_id - 1] = list(self._matrix[row_id])  # update matrix with the moved down row
                moved_down = True

            else:
                self._matrix[row_id - 1] = [None] * self.COLUMN_COUNT  # update matrix with an empty row
            row_id += 1

        mc.refresh()
        return moved_down
