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

/// https://github.com/Jij-Inc/pyo3-stub-gen/issues/161

#[cfg(feature = "stubgen")]
use tetris_maya::stub_info;


#[cfg(feature = "stubgen")]
use pyo3_stub_gen::Result;

#[cfg(feature = "stubgen")]
fn main() -> Result<()> {
    let stub = tetris_maya::stub_info()?;
    stub.generate()?;
    Ok(())
}

#[cfg(not(feature = "stubgen"))]
fn main() {
    eprintln!("The 'stubgen' feature is not enabled. Enable it with `--features stubgen/stubgen`.");
}
