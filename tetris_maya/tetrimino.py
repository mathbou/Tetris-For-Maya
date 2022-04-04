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
from __future__ import absolute_import
from __future__ import unicode_literals

import maya.cmds as mc

from .constants import PREFIX

__all__ = ["TetriminoType", "Tetrimino"]


class Tetrimino(object):
    def __init__(self, type, root, cubes):
        # type: (unicode, unicode, tuple[unicode, unicode, unicode, unicode]) -> None
        self.type = type
        self.root = root
        self.cubes = cubes

    @property
    def position(self):
        # type: () -> tuple[float, float]
        """Get (x, y) world position of the root group"""
        return mc.xform(self.root, query=True, worldSpace=True, translation=True)[:2]

    @property
    def cube_positions(self):
        # type: () -> list[tuple[float, float]]
        """Get (x, y) world positions for each cube"""
        return [mc.xform(cube, query=True, worldSpace=True, translation=True)[:2] for cube in self.cubes]


class TetriminoType(object):
    _types = []  # type: ClassVar[list[TetriminoType]]

    def __init__(self, name,cubes,color):
        # type: (unicode, tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]], tuple[float, float, float]) -> None
        self.name = name
        self.cubes = cubes
        self.color = color

        # Register tetrimino type
        self._types.append(self)

    @classmethod
    def get_all(cls):
        # type: () -> list[TetriminoType]
        return cls._types

    def make(self, id):  # noqa: A002
        # type: () -> Tetrimino
        return tetrimino_maker(self, id)


T = TetriminoType(name="T", cubes=((0, 0), (1, 0), (-1, 0), (0, -1)), color=(0.23, 0.0, 0.27))
O = TetriminoType(name="O", cubes=((0, 0), (0, -1), (1, 0), (1, -1)), color=(0.7, 0.65, 0.02))  # noqa: E741
L = TetriminoType(name="L", cubes=((0, 0), (-1, -1), (1, 0), (-1, 0)), color=(0.75, 0.25, 0))
J = TetriminoType(name="J", cubes=((0, 0), (1, -1), (1, 0), (-1, 0)), color=(0.02, 0.02, 0.65))
Z = TetriminoType(name="Z", cubes=((0, 0), (0, -1), (-1, 0), (1, -1)), color=(0.65, 0.02, 0.02))
S = TetriminoType(name="S", cubes=((0, 0), (0, -1), (1, 0), (-1, -1)), color=(0.02, 0.65, 0.02))
I = TetriminoType(name="I", cubes=((0, 0), (-1, 0), (1, 0), (2, 0)), color=(0, 0.5, 1))  # noqa: E741


def tetrimino_maker(t_type, id = 0):  # noqa: A002
    # type: (TetriminoType, int) -> Tetrimino
    name = "{}{}".format(t_type.name, id)

    tetrimino_cubes = []

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
        name="{}_tetrimino{}0".format(PREFIX, name),
    )[0]
    mc.polyBevel3(
        "{}.e[0:11]".format(tetrimino_cube),
        segments=1,
        constructionHistory=False,
        offset=0.1,
        offsetAsFraction=False,
        worldSpace=True,
        angleTolerance=30,
    )
    mc.polyColorPerVertex(rgb=t_type.color, colorDisplayOption=True, notUndoable=True)
    x, y = t_type.cubes[0]
    mc.move(x, y, 0, tetrimino_cube, absolute=True)

    tetrimino_cubes.append(tetrimino_cube)

    for tx, ty in t_type.cubes[1:]:
        duplicate_cube = mc.duplicate(tetrimino_cube, instanceLeaf=True)[0]
        mc.move(tx, ty, 0, duplicate_cube, absolute=True)
        tetrimino_cubes.append(duplicate_cube)

    group = mc.group(tetrimino_cubes, name="{}_tetrimino{}_grp".format(PREFIX, name))
    mc.xform(group, pivots=(0, 0, 0), worldSpace=True)

    cubes = tuple("{}|{}".format(group, cube) for cube in tetrimino_cubes)  # way faster than listRelatives

    mc.select(clear=True)

    return Tetrimino(type=t_type.name, root=group, cubes=cubes)
