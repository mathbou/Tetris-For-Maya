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
use super::maya::Move;
use super::point::Point;

#[derive(PartialEq, Clone, Debug)]
pub struct Cube {
    pub name: String,
}

impl Cube {
    pub fn new(name: String) -> Self {
        Cube { name }
    }
    pub fn get_position(&self) -> Point {
        Point::from(maya::get_position(self.name.as_str()))
    }

    pub fn r#move(&self, position: Point, mode: Move) {
        maya::r#move(self.name.as_str(), position.x, position.y, 0, mode)
    }
}
