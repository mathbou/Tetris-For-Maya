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

use pyo3::pyclass;
use stubgen_macro::stubgen;

#[stubgen]
#[pyclass]
#[derive(PartialEq, Copy, Clone, Debug)]
pub enum Turn {
    Left = 90,
    Right = -90,
}

#[derive(Debug, Default, Clone)]
pub struct Point {
    pub x: i32,
    pub y: i32,
}

impl PartialEq for Point {
    fn eq(&self, other: &Self) -> bool {
        self.x == other.x && self.y == other.y
    }
}

impl From<(i32, i32)> for Point {
    fn from(value: (i32, i32)) -> Self {
        Point::new(value.0, value.1)
    }
}

impl From<[f32; 3]> for Point {
    fn from(value: [f32; 3]) -> Self {
        Point::new(value[0] as i32, value[1] as i32)
    }
}

impl Point {
    pub fn new(x: i32, y: i32) -> Self {
        Point { x, y }
    }

    pub fn as_f32_tuple(&self) -> (f32, f32) {
        (self.x as f32, self.y as f32)
    }

    /// 2D rotation
    pub fn rotate(&mut self, angle: Turn, origin: Option<&Point>) {
        let (ox, oy) = origin.unwrap_or(&Point::default()).as_f32_tuple();
        let (px, py) = self.as_f32_tuple();

        let rad_angle = (angle as i32 as f32).to_radians();

        let rx = ox + rad_angle.cos() * (px - ox) - rad_angle.sin() * (py - oy);
        let ry = oy + rad_angle.sin() * (px - ox) + rad_angle.cos() * (py - oy);

        self.x = rx.round() as i32;
        self.y = ry.round() as i32;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_rotate() {
        let mut p = Point::new(1, 0);
        p.rotate(Turn::Left, None);

        let expect = Point::new(0, 1);
        assert_eq!(p, expect);
    }

    #[test]
    fn test_rotate_around_origin() {
        let mut p = Point::new(1, 0);
        let o = Point::new(0, 1);
        p.rotate(Turn::Left, Some(&o));

        let expect = Point::new(1, 2);
        assert_eq!(p, expect);
    }
}
