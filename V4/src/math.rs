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

#[derive(Copy, Clone, Debug)]
pub enum Number {
    I32(i32),
    F32(f32),
}

impl From<Number> for f32 {
    fn from(value: Number) -> Self {
        match value {
            Number::I32(i) => i as f32,
            Number::F32(f) => f,
        }
    }
}

impl From<i32> for Number {
    fn from(value: i32) -> Self {
        Number::I32(value)
    }
}

impl From<f32> for Number {
    fn from(value: f32) -> Self {
        Number::F32(value)
    }
}

/// Get the absolute highest number.
pub fn absmax<T: Into<Number> + Copy>(a: T, b: T) -> T {
    let a_: f32 = a.into().into();
    let b_: f32 = b.into().into();

    if a_.abs() > b_.abs() { a } else { b }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_absmax() {
        assert_eq!(absmax(-3.0, 2.0), -3.0);
        assert_eq!(absmax(3.0, 2.0), 3.0);
        assert_eq!(absmax(-3, 2), -3);
    }
}
