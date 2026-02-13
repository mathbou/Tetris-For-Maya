from dataclasses import dataclass, field
from typing import ClassVar

import maya.cmds as mc

from .constants import PREFIX

from typing import Tuple, List


__all__ = ["TetriminoType", "Tetrimino"]


@dataclass(frozen=True)
class Tetrimino:
    type: str
    root: str
    cubes: Tuple[str, str, str, str]

    @property
    def position(self) -> Tuple[float, float]:
        """Get (x, y) world position of the root group"""
        return mc.xform(self.root, query=True, worldSpace=True, translation=True)[:2]

    @property
    def cube_positions(self) -> List[Tuple[float, float]]:
        """Get (x, y) world positions for each cube"""
        return [mc.xform(cube, query=True, worldSpace=True, translation=True)[:2] for cube in self.cubes]


@dataclass(frozen=True)
class TetriminoType:
    name: str
    cubes: Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float]]
    color: Tuple[float, float, float]
    _types: ClassVar[List["TetriminoType"]] = field(default=[], init=False)

    def __post_init__(self):
        # Register type
        self._types.append(self)

    @classmethod
    def get_all(cls) -> List["TetriminoType"]:
        return cls._types

    def make(self, id: int) -> Tetrimino:
        return tetrimino_maker(self.cubes, self.color, f"{self.name}{id}")


T = TetriminoType(name="T", cubes=((0, 0), (1, 0), (-1, 0), (0, -1)), color=(0.23, 0.0, 0.27))
O = TetriminoType(name="O", cubes=((0, 0), (0, -1), (1, 0), (1, -1)), color=(0.7, 0.65, 0.02))
L = TetriminoType(name="L", cubes=((0, 0), (-1, -1), (1, 0), (-1, 0)), color=(0.75, 0.25, 0))
J = TetriminoType(name="J", cubes=((0, 0), (1, -1), (1, 0), (-1, 0)), color=(0.02, 0.02, 0.65))
Z = TetriminoType(name="Z", cubes=((0, 0), (0, -1), (-1, 0), (1, -1)), color=(0.65, 0.02, 0.02))
S = TetriminoType(name="S", cubes=((0, 0), (0, -1), (1, 0), (-1, -1)), color=(0.02, 0.65, 0.02))
I = TetriminoType(name="I", cubes=((0, 0), (-1, 0), (1, 0), (2, 0)), color=(0, 0.5, 1))


def tetrimino_maker(cubes: Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float]],
                    color: Tuple[float, float, float],
                    name: str) -> Tetrimino:
    tetrimino_cubes = []

    for i, (tx, ty) in enumerate(cubes):
        tetrimino_cube = mc.polyCube(
            width=1, height=1, depth=1,
            subdivisionsX=1, subdivisionsY=1, subdivisionsZ=1,
            createUVs=False,
            constructionHistory=False,
            axis=(0, 1, 0),
            name=f"{PREFIX}_tetrimino{name}{i}"
        )[0]
        mc.polyBevel3(f"{tetrimino_cube}.e[0:11]", segments=1,
                      constructionHistory=False, offset=0.1, offsetAsFraction=False,
                      worldSpace=True,
                      angleTolerance=30)
        mc.polyColorPerVertex(rgb=color, colorDisplayOption=True, notUndoable=True)

        mc.move(tx, ty, 0, tetrimino_cube, absolute=True)
        tetrimino_cubes.append(tetrimino_cube)

    group = mc.group(tetrimino_cubes, name=f"{PREFIX}_tetrimino{name}_grp")
    mc.xform(group, pivots=(0, 0, 0), worldSpace=True)

    cubes = tuple(f'{group}|{cube}' for cube in tetrimino_cubes) # way faster than listRelatives

    mc.select(clear=True)

    return Tetrimino(type=name, root=group, cubes=cubes)




