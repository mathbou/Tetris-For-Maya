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
use pyo3::types::IntoPyDict;
use pyo3::Python;

fn cmds(py: Python<'_>) -> Bound<PyModule> {
    PyModule::import(py, "maya.cmds").expect("Failed to import maya.cmds")
}

pub fn get_position(name: &str) -> [f32; 3] {
    Python::with_gil(|py| {
        let args = (&name,);
        let kwargs = [("query", true), ("worldSpace", true), ("translation", true)]
            .into_py_dict(py)
            .unwrap();

        cmds(py)
            .getattr("xform")
            .expect("Cant get xform")
            .call(args, Some(&kwargs))
            .expect("xform call failed")
            .extract::<[f32; 3]>()
            .expect("xform extraction failed")
    })
}

pub enum Move {
    Absolute,
    Relative,
}

pub fn r#move<T>(name: &str, x: T, y: T, z: T, mode: Move)
where
    T: num_traits::Signed + for<'py> pyo3::IntoPyObject<'py> + Copy,
{
    moves(&vec![name], x, y, z, mode)
}

pub fn r#moves<T>(names: &Vec<&str>, x: T, y: T, z: T, mode: Move)
where
    T: num_traits::Signed + for<'py> pyo3::IntoPyObject<'py> + Copy,
{
    let mode = match mode {
        Move::Absolute => "absolute",
        Move::Relative => "relative",
    };

    Python::with_gil(|py| {
        let args = (x, y, z, names);
        let kwargs = [("worldSpace", true), (mode, true)]
            .into_py_dict(py)
            .unwrap();

        cmds(py)
            .getattr("move")
            .expect("Cant get move")
            .call(args, Some(&kwargs))
            .unwrap();
    })
}

pub fn refresh() {
    Python::with_gil(|py| {
        cmds(py)
            .getattr("refresh")
            .expect("Cant get refresh")
            .call0()
            .unwrap();
    })
}

pub fn delete(items: &Vec<&str>) {
    Python::with_gil(|py| {
        cmds(py)
            .getattr("delete")
            .expect("Cant get delete")
            .call1((items,))
            .unwrap();
    })
}
