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

use pyo3::prelude::*;

#[cfg(feature = "stubgen")]
use pyo3_stub_gen::define_stub_info_gatherer;

mod cube;
mod grid;
mod math;
mod maya;
mod point;
mod tetrimino;

#[pymodule]
#[pyo3(name = "rlib")]
fn tetris_maya(m: &Bound<'_, PyModule>) -> PyResult<()> {
    pyo3_log::init();
    m.add_class::<tetrimino::Tetrimino>()?;
    m.add_class::<tetrimino::TetriminoLetter>()?;
    m.add_class::<cube::Cube>()?;
    m.add_class::<grid::Grid>()?;
    m.add_class::<point::Turn>()?;
    Ok(())
}

// Define a function to gather stub information.
#[cfg(feature = "stubgen")]
define_stub_info_gatherer!(stub_info);
