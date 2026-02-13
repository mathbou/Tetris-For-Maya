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

use super::maya;
use super::point::Point;
use pyo3::{pyclass, pymethods};
use stubgen_macro::stubgen;

#[stubgen]
#[pyclass(subclass)]
#[derive(PartialEq, Clone, Debug)]
pub struct Cube {
    #[pyo3(get)]
    pub name: String,
}

#[pymethods]
impl Cube {
    #[new]
    pub fn new(name: String) -> Self {
        Cube { name }
    }

    /// Move the cube to the desired coordinates.
    #[pyo3(name = "move")]
    pub fn py_move(&self, x: i32, y: i32) {
        self.r#move(Point::new(x, y), maya::Move::Absolute);
    }
}

impl Cube {
    pub fn get_position(&self) -> Point {
        Point::from(maya::get_position(self.name.as_str()))
    }

    pub fn r#move(&self, position: Point, mode: maya::Move) {
        maya::r#move(self.name.as_str(), position.x, position.y, 0, mode)
    }
}
