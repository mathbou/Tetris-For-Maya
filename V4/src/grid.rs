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
use super::point::{Point, Turn};
use super::tetrimino::{Tetrimino, TetriminoLetter};
use super::{math, maya};
use pyo3::{pyclass, pymethods, Py};
use stubgen_macro::stubgen;

#[stubgen]
#[pyclass(subclass)]
pub struct Grid {
    cells: Vec<Vec<Option<Cube>>>,
    active_tetrimino: Option<Py<Tetrimino>>,
}

#[stubgen]
#[pymethods]
impl Grid {
    #[classattr]
    const ROW_COUNT: usize = 20;
    #[classattr]
    const COLUMN_COUNT: usize = 10;

    #[classattr]
    const TOP: i32 = Self::ROW_COUNT as i32 - 1;
    #[classattr]
    const BOTTOM: i32 = 0;
    #[classattr]
    const LEFT: i32 = 0;
    #[classattr]
    const RIGHT: i32 = Self::COLUMN_COUNT as i32 - 1;
    #[classattr]
    const NEXT_POS: (f32, f32, f32) = (12.5, 15.0, -1.0);
    #[classattr]
    const HOLD_POS: (f32, f32, f32) = (-3.5, 15.0, -1.0);

    #[classattr]
    const JIGGLE_MOVES: [i32; 4] = [-1, 1, -2, 2];

    #[new]
    fn new() -> Self {
        let columns = vec![None; Self::COLUMN_COUNT];

        Grid {
            cells: vec![columns; Self::ROW_COUNT],
            active_tetrimino: None,
        }
    }

    /// Move the active tetrimino
    #[pyo3(name = "move")]
    pub fn py_move(&self, x: i32, y: i32) -> bool {
        match &self.active_tetrimino {
            Some(t) => self.r#move(t.get(), &Point::new(x, y)),
            None => false,
        }
    }

    /// Rotate the active tetrimino
    #[pyo3(name = "rotate")]
    pub fn py_rotate(&self, angle: Turn) -> bool {
        match &self.active_tetrimino {
            Some(t) => self.rotate(t.get(), angle),
            None => false,
        }
    }

    /// Check if the active tetrimino collides with another one
    #[pyo3(name = "inplace_collision")]
    pub fn py_inplace_collision(&self) -> bool {
        match &self.active_tetrimino {
            Some(t) => self.inplace_collision(t.get()),
            None => false,
        }
    }

    /// Store the active tetrimino cubes in the cell matrix. Should only be called in the post-loop.  
    #[pyo3(name = "update_cells")]
    pub fn py_update_cells(&mut self) {
        maya::refresh();

        if let Some(active) = &self.active_tetrimino {
            let t = active.get();
            for (cube, point) in t.cubes.iter().zip(t.get_cube_positions().iter()) {
                self.cells[point.y as usize][point.x as usize] = Some(cube.clone());
            }
        };
    }

    /// Check the grid for completed rows. Delete them and move down the others if possible.
    #[pyo3(name = "process_completed_rows")]
    pub fn py_process_completed_rows(&mut self) -> i32 {
        let mut row_idx = 0;
        let mut completed_rows = 0;

        while row_idx < Self::ROW_COUNT {
            let is_row_complete = self.cells[row_idx].iter().all(|c| c.is_some());

            if is_row_complete {
                completed_rows += 1;
                let cube_names_to_delete = &self.cells[row_idx]
                    .iter()
                    .flatten()
                    .map(|c| c.name.as_str())
                    .collect();
                maya::delete(cube_names_to_delete);

                if !self.move_down_rows(row_idx) {
                    row_idx += 1;
                }
            } else {
                row_idx += 1;
            }
        }
        completed_rows
    }

    #[setter]
    pub fn set_active_tetrimino(&mut self, active_tetrimino: Py<Tetrimino>) {
        self.active_tetrimino = Some(active_tetrimino);
    }

    #[getter]
    pub fn get_active_tetrimino(&self) -> &Option<Py<Tetrimino>> {
        &self.active_tetrimino
    }
}

impl Grid {
    fn is_inside_grid(point: &Point) -> bool {
        (Self::LEFT <= point.x)
            && (point.x <= Self::RIGHT)
            && (Self::BOTTOM <= point.y)
            && (point.y <= Self::TOP)
    }

    fn cell_is_available(&self, point: &Point, whitelist: Option<&[&Cube]>) -> bool {
        let value = &self.cells[point.y as usize][point.x as usize];
        match value {
            Some(cube) => match whitelist {
                Some(whitelist) => whitelist.contains(&cube),
                None => false,
            },
            None => true,
        }
    }

    fn cells_are_available(
        &self,
        points: &[Point; 4],
        whitelist: Option<&[&Cube]>,
        offset: &Point,
    ) -> bool {
        for point in points {
            let offset_point = Point::new(point.x + offset.x, point.y + offset.y);

            let is_available_and_inside = Self::is_inside_grid(&offset_point)
                && self.cell_is_available(&offset_point, whitelist);
            if !is_available_and_inside {
                return false;
            }
        }
        true
    }

    fn can_move_to(&self, tetrimino: &Tetrimino, point: &Point) -> bool {
        let cubes: &[&Cube; 4] = &std::array::from_fn(|i| &tetrimino.cubes[i]);

        self.cells_are_available(&tetrimino.get_cube_positions(), Some(cubes), point)
    }

    fn inplace_collision(&self, tetrimino: &Tetrimino) -> bool {
        !self.can_move_to(tetrimino, &Point::default())
    }

    fn r#move(&self, tetrimino: &Tetrimino, point: &Point) -> bool {
        if self.can_move_to(tetrimino, point) {
            maya::r#move(&tetrimino.root, point.x, point.y, 0, maya::Move::Relative);
            maya::refresh();
            return true;
        }
        false
    }
    fn rotate(&self, tetrimino: &Tetrimino, angle: Turn) -> bool {
        if tetrimino.r#type == TetriminoLetter::O {
            return false;
        }

        let root_position = tetrimino.get_root_position();

        let mut rot_cube_positions = tetrimino.get_cube_positions();
        rot_cube_positions
            .iter_mut()
            .for_each(|p| p.rotate(angle, Some(&root_position)));

        let mut global_offset = Point::default();
        for point in rot_cube_positions.iter() {
            if !Self::is_inside_grid(point) {
                let cube_offset_x = point.x.clamp(Self::LEFT, Self::RIGHT) - point.x;
                let cube_offset_y = point.y.clamp(Self::BOTTOM, Self::TOP) - point.y;
                global_offset.x = math::absmax(cube_offset_x, global_offset.x);
                global_offset.y = math::absmax(cube_offset_y, global_offset.y);
            }
        }

        let cubes: &[&Cube; 4] = &std::array::from_fn(|i| &tetrimino.cubes[i]);

        if !self.cells_are_available(&rot_cube_positions, Some(cubes), &global_offset) {
            let mut broken = false;

            for ox in Self::JIGGLE_MOVES {
                let move_offset = Point::new(global_offset.x + ox, global_offset.y);

                if self.cells_are_available(&rot_cube_positions, Some(cubes), &move_offset) {
                    global_offset.x += ox;
                    broken = true;
                    break;
                }
            }
            if broken {
                return false;
            }
        }

        for (cube, point) in cubes.iter().zip(rot_cube_positions.iter()) {
            maya::r#move(
                cube.name.as_str(),
                point.x,
                point.y,
                0,
                maya::Move::Absolute,
            );
        }
        maya::r#move(
            &tetrimino.root,
            global_offset.x,
            global_offset.y,
            0,
            maya::Move::Relative,
        );
        maya::refresh();
        true
    }

    fn move_down_rows(&mut self, from_row: usize) -> bool {
        let mut moved_down = false;
        let mut row_idx = from_row + 1;

        while row_idx < Self::ROW_COUNT {
            let current_row = &self.cells[row_idx];
            let row_is_not_empty = current_row.iter().all(|c| c.is_some());

            if row_is_not_empty {
                let row_object_names: Vec<&str> = current_row
                    .iter()
                    .flatten()
                    .map(|c| c.name.as_str())
                    .collect();

                maya::r#moves(&row_object_names, 0, -1, 0, maya::Move::Relative);
                self.cells[row_idx - 1] = current_row.clone();
                moved_down = true;
            } else {
                self.cells[row_idx - 1] = vec![None; Self::COLUMN_COUNT];
            }
            row_idx += 1;
        }

        maya::refresh();
        moved_down
    }
}
