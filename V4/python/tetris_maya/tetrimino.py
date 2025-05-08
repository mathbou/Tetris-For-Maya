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

from dataclasses import dataclass, field
from typing import ClassVar

import maya.cmds as mc

from .constants import PREFIX
from .rlib import Cube as BaseCube
from .rlib import Tetrimino, TetriminoLetter

__all__ = ["TetriminoType"]

Point = tuple[float, float]
Color = tuple[float, float, float]


@dataclass(frozen=True)
class TetriminoType:
    name: TetriminoLetter
    cubes: tuple[Point, Point, Point, Point]
    color: Color
    _types: ClassVar[list[TetriminoType]] = field(default=[], init=False)

    def __post_init__(self):
        # Register tetrimino type
        self._types.append(self)

    @classmethod
    def get_all(cls) -> list[TetriminoType]:
        return cls._types

    def make(self, id: int) -> Tetrimino:
        return tetrimino_maker(self, id)


TetriminoType(name=TetriminoLetter.T, cubes=((0, 0), (1, 0), (-1, 0), (0, -1)), color=(0.23, 0.0, 0.27))
TetriminoType(name=TetriminoLetter.O, cubes=((0, 0), (0, -1), (1, 0), (1, -1)), color=(0.7, 0.65, 0.02))
TetriminoType(name=TetriminoLetter.L, cubes=((0, 0), (-1, -1), (1, 0), (-1, 0)), color=(0.75, 0.25, 0))
TetriminoType(name=TetriminoLetter.J, cubes=((0, 0), (1, -1), (1, 0), (-1, 0)), color=(0.02, 0.02, 0.65))
TetriminoType(name=TetriminoLetter.Z, cubes=((0, 0), (0, -1), (-1, 0), (1, -1)), color=(0.65, 0.02, 0.02))
TetriminoType(name=TetriminoLetter.S, cubes=((0, 0), (0, -1), (1, 0), (-1, -1)), color=(0.02, 0.65, 0.02))
TetriminoType(name=TetriminoLetter.I, cubes=((0, 0), (-1, 0), (1, 0), (2, 0)), color=(0, 0.5, 1))


class Cube(BaseCube):
    def __str__(self) -> str:
        return self.name

    @classmethod
    def make(cls, name: str, position: Point, color: Color) -> Cube:
        tetrimino_cube = mc.polyCube(
            width=1,
            height=1,
            depth=1,
            subdivisionsX=1,
            subdivisionsY=1,
            subdivisionsZ=1,
            createUVs=False,
            constructionHistory=False,
            axis=(0, 1, 0),
            name=f"{name}0",
        )[0]
        mc.polyBevel3(
            f"{tetrimino_cube}.e[0:11]",
            segments=1,
            constructionHistory=False,
            offset=0.1,
            offsetAsFraction=False,
            worldSpace=True,
            angleTolerance=30,
        )
        mc.polyColorPerVertex(rgb=color, colorDisplayOption=True, notUndoable=True)

        cube = cls(tetrimino_cube)
        cube.move(*position)

        return cube

    def instance(self) -> Cube:
        return self.__class__(mc.duplicate(self.name, instanceLeaf=True)[0])


def tetrimino_maker(t_type: TetriminoType, id: int = 0) -> Tetrimino:
    name = f"{PREFIX}_tetrimino_{t_type.name}{id}"

    cubes: list[Cube] = []

    root_cube = Cube.make(name, position=t_type.cubes[0], color=t_type.color)
    cubes.append(root_cube)

    for tx, ty in t_type.cubes[1:]:
        instance_cube = root_cube.instance()
        instance_cube.move(tx, ty)
        cubes.append(instance_cube)

    group = mc.group(map(str, cubes), name=f"{name}_grp")
    mc.xform(group, pivots=(0, 0, 0), worldSpace=True)

    mc.select(clear=True)

    return Tetrimino(type=t_type.name, root=group, cubes=cubes)
