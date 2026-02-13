// Copyright (c) 2025 Mathieu Bouzard.
//
// This file is part of Tetris For Maya
// (see https://gitlab.com/mathbou/TetrisMaya).
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program. If not, see <http://www.gnu.org/licenses/>.

use super::cube::Cube;
use super::maya;
use super::point::Point;
use pyo3::{pyclass, pymethods, Py, Python};
use std::array;
use stubgen_macro::stubgen;

#[stubgen]
#[pyclass(eq, eq_int)]
#[derive(PartialEq, Clone, Debug)]
pub enum TetriminoLetter {
    T,
    O,
    L,
    J,
    Z,
    S,
    I,
}

#[stubgen]
#[pymethods]
impl TetriminoLetter {
    #[getter]
    fn name(&self) -> String {
        format!("{:?}", self)
    }
}

#[stubgen]
#[pyclass(frozen)]
pub struct Tetrimino {
    pub r#type: TetriminoLetter,
    pub root: String,
    pub cubes: [Cube; 4],
}

#[stubgen]
#[pymethods]
impl Tetrimino {
    #[new]
    fn new(
        r#type: TetriminoLetter,
        root: String,
        cubes: [String; 4],
        py: Python<'_>,
    ) -> Py<Tetrimino> {
        let cubes = cubes.map(Cube::new);
        Py::new(
            py,
            Tetrimino {
                r#type,
                root,
                cubes,
            },
        )
        .unwrap()
    }

    #[getter]
    fn root(&self) -> String {
        self.root.clone()
    }

    #[getter]
    fn get_position(&self) -> (f32, f32) {
        self.get_root_position().as_f32_tuple()
    }
}

impl Tetrimino {
    pub fn get_root_position(&self) -> Point {
        Point::from(maya::get_position(&self.root))
    }

    pub fn get_cube_positions(&self) -> [Point; 4] {
        array::from_fn(|i| self.cubes[i].get_position())
    }
}
