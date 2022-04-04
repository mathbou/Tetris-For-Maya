#
# Copyright (c) 2022 Mathieu Bouzard.
#
# This file is part of Tetris For Maya
# (see https://gitlab.com/mathbou/TetrisMaya).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import absolute_import, division, unicode_literals, with_statement

import random
import time

import maya.cmds as mc
import maya.mel as mel
from PySide2.QtCore import QEvent, QObject, Qt, QThread, Signal, Slot
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QWidget

from . import maya2
from .constants import PREFIX, SCORE_TABLE, TIME_STEP
from .enum import IntEnum
from .grid import Grid, Hold
from .tetrimino import TetriminoType
from .time2 import timer_precision

__all__ = ["Game"]


class Action(IntEnum):
    LEFT = Qt.Key.Key_Left
    RIGHT = Qt.Key.Key_Right
    SOFT_DROP = Qt.Key.Key_Down
    HARD_DROP = Qt.Key.Key_Space
    ROTATE_LEFT = Qt.Key.Key_Z
    ROTATE_RIGHT = Qt.Key.Key_Up
    HOLD = Qt.Key.Key_C


class LoopWorker(QObject):
    """The game 'clock'. It sends a signal when the tetrimino should move down.

    Warnings:
        It must run in a separate thread, otherwise it blocks the main thread and the keyboard catcher won't work.

    """

    step = Signal()
    finished = Signal()
    canceled = Signal()

    def __init__(self, row_count, time_step, max_frequency=60):
        # type: (int, float, int) -> None
        self.__loop_count = row_count
        self.__time_step = time_step
        self.__max_frequency = max_frequency
        super(LoopWorker, self).__init__()

        self.finished.connect(self.deleteLater)
        self.canceled.connect(self.deleteLater)

    def run(self):
        self._is_stopped = False
        self._is_canceled = False

        f_step = self.__time_step / self.__max_frequency

        with timer_precision():
            for _ in xrange(self.__loop_count):
                duration = 0

                while duration < self.__time_step:
                    start = time.clock()
                    if self._is_stopped:
                        self.finished.emit()
                        return
                    elif self._is_canceled:
                        self.canceled.emit()
                        return
                    else:
                        time.sleep(f_step)
                    duration += time.clock() - start
                self.step.emit()

        self.finished.emit()

    def stop(self):
        self._is_stopped = True

    def cancel(self):
        self._is_canceled = True


class Game(QWidget):
    def __init__(self):
        self._score = 0
        self._level = 0
        self._lines = 0
        self._loop_counter = 0

        self._game_huds = []  # type: list[maya2.HeadsUpDisplay]

        self.update_time_step(self._level)
        self.update_tetrimino_queue()

        self.grid = Grid()

        self._thread = QThread()

        super(Game, self).__init__(parent=maya2.get_main_window())

    def close(self):
        # type: () -> bool
        self._thread.quit()
        self._thread.deleteLater()

        self.parent().removeEventFilter(self)

        return super(Game, self).close()

    # --------------Game UI----------

    @staticmethod
    def clean_geo():
        mc.delete("{}_*".format(PREFIX))

    def _prepare_hud(self):
        self._hud_backup = dict(
            (hud_name, mc.headsUpDisplay(hud_name, query=True, visible=True))
            for hud_name in mc.headsUpDisplay(query=True, listHeadsUpDisplays=True)
        )

        # disable current hud
        for hud, visible in self._hud_backup.items():
            if visible:
                mc.headsUpDisplay(hud, edit=True, visible=False)

        hud_score = maya2.HeadsUpDisplay.add(
            "{}_score_hud".format(PREFIX),
            block=21,
            section=0,
            label="Score :",
            command=self.get_score,
            labelFontSize="large",
            dataFontSize="large",
            attachToRefresh=True,
        )
        self._game_huds.append(hud_score)

        hud_level = maya2.HeadsUpDisplay.add(
            "{}_level_hud".format(PREFIX),
            block=22,
            section=0,
            label="Level :",
            command=self.get_level,
            labelFontSize="large",
            dataFontSize="large",
            attachToRefresh=True,
        )
        self._game_huds.append(hud_level)

        hud_lines = maya2.HeadsUpDisplay.add(
            "{}_lines_hud".format(PREFIX),
            block=23,
            section=0,
            label="Level :",
            command=self.get_lines,
            labelFontSize="large",
            dataFontSize="large",
            attachToRefresh=True,
        )
        self._game_huds.append(hud_lines)

        for i, command in enumerate(Action):
            name = command.name.replace("_", " ").title()
            key_str = QKeySequence(command.value).toString()
            label = "{}: {}".format(name, key_str)

            hud = maya2.HeadsUpDisplay.add("{}_{}".format(PREFIX, command.name), block=i + 10, section=5, label=label)

            self._game_huds.append(hud)

    def _create_game_camera(self):
        # type: () -> str
        camera, _ = mc.camera(focalLength=300, nearClipPlane=10, name="{}_cam".format(PREFIX))
        mc.lookThru(camera)

        mc.refresh()
        mc.viewFit(camera)

        for attr in ["translate", "rotate"]:
            mc.setAttr("{}.{}".format(camera, attr), lock=True)

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
            self._panel_backup[str(attr)] = mc.modelEditor("modelPanel4", query=True, **{str(attr): True})

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

    def eventFilter(self, watched, event):  # noqa: N802
        # type: (QWidget, QEvent) -> bool
        if event.type() == QEvent.KeyPress:
            self.move(event.key())
            return True  # Avoid pickWalk trigger
        return super(Game, self).eventFilter(watched, event)

    # ---------------------- Game Actions ----------------------

    def move(self, value):
        # type: (Action) -> None
        x, y = 0, 0

        if value == Action.LEFT:
            x, y = -1, 0
        elif value == Action.RIGHT:
            x, y = 1, 0
        elif value == Action.SOFT_DROP:
            x, y = 0, -1
            self._score += 1

        elif value == Action.ROTATE_RIGHT:
            self.grid.rotate(self.grid.active_tetrimino, angle=-90)
        elif value == Action.ROTATE_LEFT:
            self.grid.rotate(self.grid.active_tetrimino, angle=90)
        elif value == Action.HARD_DROP:
            while self.grid.move(self.grid.active_tetrimino, 0, -1):
                pass
            self._score += 20
            self.stop_loop_worker()

        elif value == Action.HOLD:
            hold_code = self.grid.hold()
            if hold_code in [Hold.SWAP, Hold.PUSH]:
                self.cancel_loop_worker()
                self.post_hold(hold_code)

        if x or y:
            self.grid.move(self.grid.active_tetrimino, x, y)

    def update_tetrimino_queue(self):
        new_queue = list(TetriminoType.get_all())
        random.shuffle(new_queue)

        try:
            self.tetrimino_type_queue.extend(new_queue)
        except AttributeError:
            self.tetrimino_type_queue = new_queue

    @property
    def time_step(self):
        # type: () -> float
        """Value is in second."""
        return self._time_step

    def update_time_step(self, level, multiplier=0.66):
        # type: (int, float) -> None
        self._time_step = TIME_STEP * (multiplier ** level)

    def remove_empty_groups(self):
        groups = mc.ls("{}_*grp".format(PREFIX), exactType="transform")
        for grp in groups:
            if not mc.listRelatives(grp, children=True):
                mc.delete(grp)

    def get_score(self):
        # type: () -> int
        """Should be used for ui purpose only."""
        return self._score

    def update_score(self, rows):
        # type: (int) -> None
        self._score += SCORE_TABLE.get(rows, 0)

    def get_lines(self):
        # type: () -> int
        """Should be used for ui purpose only."""
        return self._lines

    def get_level(self):
        # type: () -> int
        """Should be used for ui purpose only."""
        # For programming purposes, the first level is 0, so it needs an +1 offset for the ui.
        return self._level + 1

    def update_level(self, line_count):
        # type: (int) -> None
        self._lines += line_count
        self._level = self._lines // 10
        self.update_time_step(self._level)

    def game_over(self):
        mc.confirmDialog(
            title="Score",
            button="Ok",
            message="Game Over\n\n"
            "Final Score: {}\nLines: {}\nFinal Level: {}".format(self.get_score(), self.get_lines(), self.get_level()),
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
        if len(self.tetrimino_type_queue) < len(TetriminoType.get_all()):
            self.update_tetrimino_queue()

        tetrimino_type = self.tetrimino_type_queue.pop(0)
        next_tetrimino = tetrimino_type.make(id=self._loop_counter)
        self.grid.put_to_next(next_tetrimino)

        self._loop_counter += 1

        if self._loop_counter <= 1:
            # Force a second init on the first turn
            self.init_loop()
        elif self.grid.inplace_collision(self.grid.active_tetrimino):
            self.game_over()
        else:
            self.launch_loop_worker()

    @Slot()
    def step(self):
        """Try to move down the current tetrimino. Stop the loop worker if it can't."""
        if not self.grid.move(self.grid.active_tetrimino, 0, -1):
            self.stop_loop_worker()

    @Slot()
    def post_loop(self):
        """Update the grid and the score, then launch the next loop."""
        self.grid.reset_hold()
        self.grid.update_cells(self.grid.active_tetrimino)

        completed_rows = self.grid.process_completed_rows()

        self.update_score(completed_rows)
        self.update_level(completed_rows)

        self.remove_empty_groups()

        self.init_loop()

    def post_hold(self, value):
        # type: (Hold) -> None
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
