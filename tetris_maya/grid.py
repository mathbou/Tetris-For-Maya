import math
from enum import IntEnum
from typing import ClassVar, Optional, Tuple, List

import maya.cmds as mc
from maya.app.type import typeToolSetup

from .constants import PREFIX
from .math2 import rotate_point, absmax
from .tetrimino import O, Tetrimino


__all__ = ["Grid", "Hold"]


class Hold(IntEnum):
    CANT = 0
    PUSH = 1
    SWAP = 2


class Grid():
    ROW_COUNT: ClassVar[int] = 20
    COLUMN_COUNT: ClassVar[int] = 10

    TOP: ClassVar[int] = ROW_COUNT - 1
    BOTTOM: ClassVar[int] = 0
    LEFT: ClassVar[int] = 0
    RIGHT: ClassVar[int] = COLUMN_COUNT - 1

    NEXT_POS: ClassVar[Tuple[float, float, float]] = (12.5, 15, -1)
    HOLD_POS: ClassVar[Tuple[float, float, float]] = (-3.5, 15, -1)

    def __init__(self):
        self._make_background()
        self._make_square("Next", self.NEXT_POS)
        self._make_square("Hold", self.HOLD_POS)
        mc.refresh()

        self._matrix: List[List[Optional[str]]] = [[None] * self.COLUMN_COUNT for _ in range(self.ROW_COUNT)]

        self.active_tetrimino: Optional[Tetrimino] = None
        self._next_tetrimino: Optional[Tetrimino] = None

        self._hold_tetrimino: Optional[Tetrimino] = None
        self._can_hold: bool = True

    @classmethod
    def _make_background(cls):
        bg_group = mc.group(name=f"{PREFIX}_background_grp", empty=1)
        for x in range(cls.COLUMN_COUNT):
            for y in range(cls.ROW_COUNT):
                bg_cube = mc.polyCube(width=1, height=1, depth=1,
                                      subdivisionsX=1, subdivisionsY=1, subdivisionsZ=1,
                                      createUVs=False,
                                      constructionHistory=False,
                                      name=f"{PREFIX}_background{x:02}{y:02}_geo")[0]
                mc.polyBevel3(f"{bg_cube}.e[0:11]", segments=1,
                              constructionHistory=False,
                              offset=0.05,
                              offsetAsFraction=False,
                              worldSpace=True,
                              angleTolerance=30)
                mc.move(x, y, -1, bg_cube, absolute=1)
                mc.parent(bg_cube, bg_group)

    @classmethod
    def _make_square(cls, text: str, position: Tuple[float, float, float]):
        square = mc.polyTorus(radius=3.2,
                              sectionRadius=0.3, twist=0,
                              subdivisionsX=4,
                              subdivisionsY=3, createUVs=False,
                              constructionHistory=False,
                              name=f"{PREFIX}_square_geo")
        mc.move(*position, square, absolute=True)
        mc.rotate("90deg", 0, "-45deg", square, absolute=True)

        # --------- Square title ---------

        type_node = mc.createNode('type', n='type#', skipSelect=True)
        type_node = typeToolSetup.createTypeToolWithNode(type_node, text=text)
        type_extrude_node = mc.listConnections(type_node, type="typeExtrude")[0]

        mc.setAttr(f"{type_extrude_node}.enableExtrusion", False)
        mc.setAttr(f"{type_node}.alignmentMode", 2)  # center
        mc.setAttr(f"{type_node}.fontSize", 1.125)

        type_transform = mc.listConnections(type_node, type="transform")[0]
        mc.move(*position, type_transform, absolute=True)
        mc.move(0, 3, 0, type_transform, relative=True)
        mc.rename(type_transform, f"{PREFIX}_{type_transform}")

    # --------------- CHECKERS ---------------

    def inside_grid(self, x: int, y: int) -> bool:
        horizontally_inside = self.LEFT <= x <= self.RIGHT
        vertically_inside = self.BOTTOM <= y <= self.TOP

        return vertically_inside and horizontally_inside

    def cell_occupied(self, x: int, y: int, whitelist: List[str] = None) -> bool:
        whitelist = whitelist or []
        cell = self._matrix[y][x]
        return cell and cell not in whitelist

    def can_move_to(self, tetrimino: Tetrimino, x: int, y: int) -> bool:
        """

        Args:
            tetrimino:
            x: offset applied to the tetrimino
            y: offset applied to the tetrimino
        """
        for cx, cy in tetrimino.cube_positions:
            rx, ry = map(int, (cx + x, cy + y))

            if not self.inside_grid(rx, ry):
                return False

            elif self.cell_occupied(rx, ry, whitelist=tetrimino.cubes):
                return False

        return True

    def inplace_collision(self, tetrimino: Tetrimino) -> bool:
        return not self.can_move_to(tetrimino, 0, 0)

    # --------------- ACTIONS ---------------

    def move(self, tetrimino: Tetrimino, x: int, y: int) -> bool:
        if self.can_move_to(tetrimino, x, y):
            mc.move(x, y, 0, tetrimino.root, relative=1)
            mc.refresh()
            return True
        return False

    def rotate(self, tetrimino: Tetrimino, angle: int = -90) -> bool:
        if tetrimino.type == O.name:
            return False

        origin_x, origin_y = tetrimino.position
        new_cube_pos: List[Tuple[int, int]] = []

        offset_x, offset_y = 0, 0

        for cx, cy in tetrimino.cube_positions:
            rx, ry = map(int, rotate_point(point=(cx, cy), angle=math.radians(angle), origin=(origin_x, origin_y)))

            if self.cell_occupied(rx, ry, tetrimino.cubes):
                return False

            if not self.inside_grid(rx, ry):
                item_ox = max(0, min(rx, self.RIGHT)) - rx
                offset_x = absmax(item_ox, offset_x)

                item_oy = max(0, min(ry, self.TOP)) - ry
                offset_y = absmax(item_oy, offset_y)

            new_cube_pos.append((rx, ry))

        for cube, (x, y) in zip(tetrimino.cubes, new_cube_pos):
            mc.move(x, y, 0, cube, worldSpace=True, absolute=True)

        mc.move(offset_x, offset_y, 0, tetrimino.root, relative=True)
        mc.refresh()

        return True

    def _move_to_start(self, tetrimino: Tetrimino):
        mc.move(self.COLUMN_COUNT/2 - 1, self.TOP, 0, tetrimino.root, absolute=True)
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
        local_center = [c - p  for c, p in zip(mc.objectCenter(tetrimino.root), tetrimino.position)]
        translation = [h - c  for h, c in zip(self.HOLD_POS, local_center)]
        mc.move(*translation, tetrimino.root, absolute=True)
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
        else:
            return Hold.CANT

    def update_cells(self, tetrimino: Tetrimino):
        mc.refresh()
        for cube, (x, y) in zip(tetrimino.cubes, tetrimino.cube_positions):
            self._matrix[int(y)][int(x)] = cube

    def process_completed_rows(self) -> int:
        row_id = 0
        completed_rows = 0

        while row_id < self.ROW_COUNT:
            row = list(filter(None, self._matrix[row_id]))
            # check si la ligne est complete
            if len(row) == self.COLUMN_COUNT:
                completed_rows += 1
                mc.delete(row)  # delete la ligne complete

                moved_down = self.remove_empty_rows(from_row=row_id)

                # fait revenir le scan a l index precedant si des blocs ont ete descendus
                row_id = row_id - int(moved_down)

            row_id += 1

        return completed_rows

    def remove_empty_rows(self, from_row: int):
        moved_down = False

        row_id = from_row + 1
        while row_id < self.ROW_COUNT:
            # descend d une case la lignes superieur si non vide
            row = list(filter(None, self._matrix[row_id]))
            if row:
                mc.move(0, -1, 0, row, relative=1)

                # actualisation des matrices
                self._matrix[row_id - 1] = self._matrix[row_id].copy()
                moved_down = True

            else:
                self._matrix[row_id - 1] = [None] * self.COLUMN_COUNT
            row_id += 1

        mc.refresh()
        return moved_down