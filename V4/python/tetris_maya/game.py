# Copyright (c) 2025 Mathieu Bouzard.
#
# This file is part of Tetris For Maya
# (see https://gitlab.com/mathbou/TetrisMaya).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

import random
import time
from enum import IntEnum
from typing import ClassVar

import maya.cmds as mc
import maya.mel as mel

from . import maya2
from .constants import PREFIX
from .grid import Grid, Hold
from .rlib import Turn
from .tetrimino import TetriminoType
from .time2 import timer_precision

try:
    from PySide2.QtCore import QEvent, QObject, Qt, QThread, Signal, Slot
    from PySide2.QtGui import QKeySequence
    from PySide2.QtWidgets import QWidget
except ImportError:
    from PySide6.QtCore import QEvent, QObject, Qt, QThread, Signal, Slot
    from PySide6.QtGui import QKeySequence
    from PySide6.QtWidgets import QWidget

__all__ = ["Game"]


class Action(IntEnum):
    LEFT = Qt.Key.Key_Left
    RIGHT = Qt.Key.Key_Right
    SOFT_DROP = Qt.Key.Key_Down
    HARD_DROP = Qt.Key.Key_Space
    ROTATE_LEFT = Qt.Key.Key_Z
    ROTATE_RIGHT = Qt.Key.Key_Up
    HOLD = Qt.Key.Key_C
    EXIT = Qt.Key.Key_Escape


class LoopWorker(QObject):
    """The game 'clock'. It sends a signal when the tetrimino should move down.

    Warnings:
        It must run in a separate thread, otherwise it blocks the main thread and the keyboard catcher won't work.

    """

    step = Signal()
    finished = Signal()
    canceled = Signal()

    def __init__(self, row_count: int, time_step: float, max_frequency: int = 60):
        self.__loop_count = row_count
        self.__time_step = time_step
        self.__max_frequency = max_frequency
        super().__init__()

        self.finished.connect(self.deleteLater)
        self.canceled.connect(self.deleteLater)

    def run(self):
        self._is_stopped = False
        self._is_canceled = False

        f_step = self.__time_step / self.__max_frequency

        with timer_precision():
            for _ in range(self.__loop_count):
                duration = 0

                while duration < self.__time_step:
                    start = time.perf_counter()
                    if self._is_stopped:
                        self.finished.emit()
                        return
                    if self._is_canceled:
                        self.canceled.emit()
                        return
                    time.sleep(f_step)
                    duration += time.perf_counter() - start

                self.step.emit()

        self.finished.emit()

    def stop(self):
        self._is_stopped = True

    def cancel(self):
        self._is_canceled = True


class Game(QWidget):
    TIME_STEP: ClassVar[float] = 0.5
    SCORE_TABLE: ClassVar[dict[int, int]] = {1: 100, 2: 300, 3: 500, 4: 800}

    def __init__(self):
        self._score = 0
        self._level = 0
        self._lines = 0
        self._loop_counter = 0

        self._game_huds: list[maya2.HeadsUpDisplay] = []
        self._tetrimino_type_queue: list[TetriminoType] = []

        self.update_time_step()

        self.grid = Grid()
        self._thread = QThread()

        super().__init__(parent=maya2.get_main_window())

    def close(self) -> bool:
        self._thread.quit()
        self._thread.deleteLater()

        self.parent().removeEventFilter(self)

        return super().close()

    # --------------Game UI----------

    @staticmethod
    def clean_geo():
        mc.delete(f"{PREFIX}_*")

    def _prepare_hud(self):
        self._hud_backup = {
            hud_name: mc.headsUpDisplay(hud_name, query=True, visible=True)
            for hud_name in mc.headsUpDisplay(query=True, listHeadsUpDisplays=True)
        }

        # disable current hud
        for hud, visible in self._hud_backup.items():
            if visible:
                mc.headsUpDisplay(hud, edit=True, visible=False)

        hud_score = maya2.HeadsUpDisplay.add(
            f"{PREFIX}_score_hud",
            block=11,
            section=0,
            label="Score :",
            command=self.get_score,
            labelFontSize="large",
            dataFontSize="large",
            attachToRefresh=True,
        )
        self._game_huds.append(hud_score)

        hud_level = maya2.HeadsUpDisplay.add(
            f"{PREFIX}_level_hud",
            block=12,
            section=0,
            label="Level :",
            command=self.get_ui_level,
            labelFontSize="large",
            dataFontSize="large",
            attachToRefresh=True,
        )
        self._game_huds.append(hud_level)

        hud_lines = maya2.HeadsUpDisplay.add(
            f"{PREFIX}_lines_hud",
            block=13,
            section=0,
            label="Level :",
            command=self.get_lines,
            labelFontSize="large",
            dataFontSize="large",
            attachToRefresh=True,
        )
        self._game_huds.append(hud_lines)

        for idx, action in enumerate(Action):
            name = action.name.replace("_", " ").title()
            key_str = QKeySequence(action.value).toString()
            label = f"{name}: {key_str}"

            hud = maya2.HeadsUpDisplay.add(f"{PREFIX}_{action.name}", block=idx + 10, section=5, label=label)

            self._game_huds.append(hud)

    def _create_game_camera(self) -> str:
        camera, _ = mc.camera(focalLength=300, nearClipPlane=10, name=f"{PREFIX}_cam")
        mc.lookThru(camera)

        mc.refresh()
        mc.viewFit(camera)

        for attr in ["translate", "rotate"]:
            mc.setAttr(f"{camera}.{attr}", lock=True)

        return camera

    def prepare_viewport(self):
        mel.eval('setNamedPanelLayout("Single Perspective View")')

        self._editor_backup = {}
        for ui in ["ChannelBoxLayerEditor", "ToolSettings"]:
            self._editor_backup[ui] = mc.workspaceControl(ui, query=True, collapse=True)
            mc.workspaceControl(ui, edit=True, collapse=True)

        self._create_game_camera()

        self._panel_backup = {}
        for attr in ("hud", "grid", "handles"):
            self._panel_backup[attr] = mc.modelEditor("modelPanel4", query=True, **{attr: True})

        mc.modelEditor("modelPanel4", edit=True, hud=True, grid=False, handles=False)

        self._prepare_hud()

    def _restore_hud(self):
        for hud in self._game_huds:
            hud.remove()

        for hud, state in self._hud_backup.items():
            mc.headsUpDisplay(hud, edit=True, visible=state)

    def restore_viewport(self):
        for ui, collapse in self._editor_backup.items():
            mc.workspaceControl(ui, edit=True, collapse=collapse)

        for attr, value in self._panel_backup.items():
            mc.modelEditor("modelPanel4", edit=True, **{attr: value})

        self._restore_hud()

    # -------------- Keyboard Catcher ----------

    def eventFilter(self, watched: QWidget, event: QEvent) -> bool:  # noqa: N802
        if event.type() == QEvent.KeyPress:
            if event.key() == Action.EXIT:
                self.cancel_loop_worker()
                self.game_over()
                return False

            self.move(event.key())
            return True  # Avoid pickWalk trigger
        return super().eventFilter(watched, event)

    # ---------------------- Game Actions ----------------------

    def move(self, value: Action):  # noqa: C901
        x, y = 0, 0

        if value == Action.LEFT:
            x, y = -1, 0
        elif value == Action.RIGHT:
            x, y = 1, 0
        elif value == Action.SOFT_DROP:
            x, y = 0, -1
            self._score += 1

        elif value == Action.ROTATE_RIGHT:
            self.grid.rotate(angle=Turn.Right)
        elif value == Action.ROTATE_LEFT:
            self.grid.rotate(angle=Turn.Left)
        elif value == Action.HARD_DROP:
            while self.grid.move(0, -1):
                pass
            self._score += 20
            self.stop_loop_worker()

        elif value == Action.HOLD:
            hold_code = self.grid.hold()
            if hold_code in {Hold.SWAP, Hold.PUSH}:
                self.cancel_loop_worker()
                self.post_hold(hold_code)

        if x or y:
            self.grid.move(x, y)

    def update_tetrimino_type_queue(self):
        types = TetriminoType.get_all()

        if len(self._tetrimino_type_queue) <= len(types):
            new_queue = random.sample(types, len(types))
            self._tetrimino_type_queue.extend(new_queue)

    @property
    def tetrimino_type_queue(self) -> list[TetriminoType]:
        return self._tetrimino_type_queue

    @property
    def time_step(self) -> float:
        """Value is in second."""
        return self._time_step

    def update_time_step(self, multiplier: float = 0.66):
        self._time_step = self.TIME_STEP * (multiplier**self._level)

    def get_score(self) -> int:
        """Should be used for ui only.

        Returns:
            Point count.
        """
        return self._score

    def update_score(self, rows: int):
        self._score += self.SCORE_TABLE.get(rows, 0)

    def get_lines(self) -> int:
        """Should be used for ui only.

        Returns:
            Line count.
        """
        return self._lines

    def get_ui_level(self) -> int:
        """Should be used for ui only.

        Returns:
            Current level starting from 1.
        """
        # For programming purposes, the first level is 0, so it needs an +1 offset for the ui.
        return self._level + 1

    def update_level(self, line_count: int):
        self._lines += line_count
        self._level = self._lines // 10

    def game_over(self):
        mc.confirmDialog(
            title="Score",
            button="Ok",
            message=f"Game Over\n\n"
            f"Final Score: {self.get_score()}\n"
            f"Lines: {self.get_lines()}\n"
            f"Final Level: {self.get_ui_level()}",
        )

        self.clean_geo()
        self.restore_viewport()
        self.close()

    # ---------------------- Game Loop ----------------------

    def launch_loop_worker(self):
        self.loop_worker = LoopWorker(self.grid.ROW_COUNT, self.time_step)
        self.loop_worker.step.connect(self.step)
        self.loop_worker.moveToThread(self._thread)

        self._thread.started.connect(self.loop_worker.run)

        self.loop_worker.finished.connect(self._thread.quit)
        self.loop_worker.finished.connect(self.post_loop)

        self._thread.start()

    def stop_loop_worker(self):
        self.loop_worker.stop()
        self.stop_thread()

    def cancel_loop_worker(self):
        self.loop_worker.cancel()
        self.stop_thread()

    def stop_thread(self):
        self._thread.quit()
        with timer_precision():
            while not self._thread.isFinished():
                time.sleep(0.02)

    def init_loop(self):
        self.update_tetrimino_type_queue()

        tetrimino_type = self.tetrimino_type_queue.pop(0)
        next_tetrimino = tetrimino_type.make(id=self._loop_counter)
        self.grid.put_to_next(next_tetrimino)

        self._loop_counter += 1

        if self._loop_counter <= 1:
            # Force a second init on the first turn
            self.init_loop()
        elif self.grid.inplace_collision():
            self.game_over()
        else:
            self.launch_loop_worker()

    @Slot()
    def step(self):
        """Try to move down the current tetrimino. Stop the loop worker if it can't."""
        if not self.grid.move(0, -1):
            self.stop_loop_worker()

    @Slot()
    def post_loop(self):
        """Update the grid and the score, then launch the next loop."""
        self.grid.reset_hold()
        self.grid.update_cells()

        completed_rows = self.grid.process_completed_rows()

        self.update_score(completed_rows)
        self.update_level(completed_rows)
        self.update_time_step()

        maya2.remove_empty_groups(f"{PREFIX}_*_grp")

        self.init_loop()

    def post_hold(self, value: Hold):
        """Depending on the hold type, relaunch a worker (swap) or the full loop (push)."""
        if value is Hold.SWAP:
            self.launch_loop_worker()
        elif value is Hold.PUSH:
            self.init_loop()

    @classmethod
    def start(cls):
        self = cls()
        self.prepare_viewport()
        self.showMinimized()
        self.parent().installEventFilter(self)  # install keyboardCatcher

        maya2.hud_countdown("Starts in", sec=3)

        self.init_loop()
