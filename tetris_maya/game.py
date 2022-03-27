import random
import time
from enum import IntEnum

import maya.cmds as mc
from PySide2.QtCore import QObject, Signal, QEvent, Slot, QThread, Qt
from PySide2.QtWidgets import QWidget

from .constants import PREFIX, TIME_STEP, SCORE_TABLE
from .grid import Grid
from .maya2 import hud_countdown, get_main_window
from .tetrimino import TetriminoType

__all__ = ["Game"]


class Action(IntEnum):
    LEFT = Qt.Key.Key_Left
    RIGHT = Qt.Key.Key_Right
    SOFTD = Qt.Key.Key_Down
    HARDD = Qt.Key.Key_Space
    ROTATE = Qt.Key.Key_Up
    HOLD = Qt.Key.Key_C


class LoopWorker(QObject):
    step = Signal()
    finished = Signal()

    def __init__(self, row_count, time_step):
        self.__loop_count = row_count
        self.__time_step = time_step
        super().__init__()

    def run(self):
        self._isRunning = True
        start = time.perf_counter()

        for _ in range(self.__loop_count):
            if not self._isRunning:
                break
            else:
                time.sleep(self.__time_step)
                self.step.emit()

        print(time.perf_counter()-start)
        self.finished.emit()

    def stop(self):
        self._isRunning = False


class Game(QWidget):
    def __init__(self):
        self._score = 0
        self._level = 0
        self._lines = 0
        self._loop_counter = 0
        self.update_time_step(self._level)

        self.grid = Grid()

        self._thread = QThread()

        super().__init__(parent=get_main_window())

    def close(self) -> bool:
        self._thread.quit()
        self._thread.deleteLater()

        self.parent().removeEventFilter(self)

        return super().close()

    # --------------Game UI----------

    @staticmethod
    def clean_geo():
        mc.delete(f"{PREFIX}_*")

    SCORE_HUD = f"{PREFIX}_score_hud"
    LEVEL_HUD = f"{PREFIX}_level_hud"
    LINES_HUD = f"{PREFIX}_lines_hud"

    def _prepare_hud(self):
        # disable current hud
        self._hud_backup = {hud_name: False for hud_name in mc.headsUpDisplay(query=True, listHeadsUpDisplays=True)}

        for hud in list(self._hud_backup):
            if mc.headsUpDisplay(hud, query=True, visible=True) is True:
                mc.headsUpDisplay(hud, edit=True, visible=False)
                self._hud_backup[hud] = True

        # hud score
        mc.headsUpDisplay(
            self.SCORE_HUD,
            section=0,
            block=11,
            blockSize="small",
            label="Score :",
            command=self.get_score,
            labelFontSize="large",
            dataFontSize="large",
            attachToRefresh=True,
        )

        # hud level
        mc.headsUpDisplay(
            self.LEVEL_HUD,
            section=0,
            block=12,
            blockSize="small",
            label="Level :",
            command=self.get_level,
            labelFontSize="large",
            dataFontSize="large",
            attachToRefresh=True,
        )

        # hud lines
        mc.headsUpDisplay(
            self.LINES_HUD,
            section=0,
            block=13,
            blockSize="small",
            label="Lines :",
            command=self.get_lines,
            labelFontSize="large",
            dataFontSize="large",
            attachToRefresh=True,
        )

    def prepare_viewport(self):
        camera, _ = mc.camera(focalLength=300, nearClipPlane=10,
                           name=f"{PREFIX}_cam")
        mc.lookThru(camera)
        mc.viewFit(camera)
        for attr in ["translate", "rotate"]:
            mc.setAttr(f"{camera}.{attr}", lock=True)

        mc.modelEditor("modelPanel4", edit=True, hud=True,
                       grid=False, handles=False, shadows=False)  # hud on - grid off - handles off

        self._prepare_hud()

    def _restore_hud(self):
        mc.headsUpDisplay(self.SCORE_HUD, remove=True)
        mc.headsUpDisplay(self.LEVEL_HUD, remove=True)
        mc.headsUpDisplay(self.LINES_HUD, remove=True)

        for hud, state in self._hud_backup.items():
            mc.headsUpDisplay(hud, edit=True, visible=state)

    def restore_viewport(self):
        mc.modelEditor("modelPanel4", edit=True, hud=True, grid=True, handles=True, shadows=True)

        self._restore_hud()

    # -------------- Keyboard Catcher ----------

    def eventFilter(self, watched, event) -> bool:
        if event.type() == QEvent.KeyPress:
            self.move(event.key())
            return True  # Avoid pickWalk trigger
        return super().eventFilter(watched, event)

    # ---------------------- Game Actions ----------------------

    def move(self, value):
        x, y = 0, 0

        if value == Action.LEFT:
            x, y = -1, 0
        elif value == Action.RIGHT:
            x, y = 1, 0
        elif value == Action.SOFTD:
            x, y = 0, -1
            self._score += 1

        elif value == Action.HARDD:
            while self.grid.move(self.grid.active_tetrimino, 0, -1):
                pass
            self.loop_worker.stop()

        elif value == Action.HOLD:
            self.grid.hold()
        elif value == Action.ROTATE:
            self.grid.rotate(self.grid.active_tetrimino)

        self.grid.move(self.grid.active_tetrimino, x, y)

    def update_tetrimino_queue(self):
        types = TetriminoType.get_all()
        new_queue = random.choices(types, k=len(types))

        try:
            self.tetrimino_type_queue.extend(new_queue)
        except AttributeError:
            self.tetrimino_type_queue = new_queue

    @property
    def time_step(self) -> float:
        """Value is in second."""
        return self._time_step

    def update_time_step(self, level: int, multiplier: float = 0.75):
        self._time_step = TIME_STEP * (multiplier ** level)

    def remove_empty_groups(self):
        groups = mc.ls(f"{PREFIX}_*grp")
        for grp in groups:
            if not mc.listRelatives(grp, children=True):
                mc.delete(grp)

    def get_score(self) -> int:
        return self._score

    def update_score(self, rows: int):
        self._score += SCORE_TABLE.get(rows)

    def get_lines(self) -> int:
        return self._lines

    def get_level(self) -> int:
        return self._level

    def update_level(self, line_count: int):
        self._lines += line_count
        self._level = self._lines // 10
        self.update_time_step(self._level)

    def game_over(self):
        mc.confirmDialog(
            title="Score",
            button="Ok",
            message=f"Game Over\n\n"
                    f"Final Score: {self.get_score()}\n"
                    f"Lines: {self.get_lines()}\n"
                    f"Final Level: {self.get_level()}",
        )

        self.clean_geo()
        self.restore_viewport()
        self.close()

    # ---------------------- Game Loop ----------------------

    def init_loop(self):
        if self._loop_counter % len(TetriminoType.get_all()) == 0:
            self.update_tetrimino_queue()

        tetrimino_type = self.tetrimino_type_queue.pop(0)
        next_tetrimino = tetrimino_type.make(id=self._loop_counter)

        self.grid.put_to_next(next_tetrimino)

        if self.inplace_collision(self.grid.active_tetrimino):
            self.game_over()

        self.loop_worker = LoopWorker(self.grid.ROW_COUNT, self.time_step)
        self.loop_worker.step.connect(self.step)
        self.loop_worker.moveToThread(self._thread)
        self._thread.started.connect(self.loop_worker.run)
        self.loop_worker.finished.connect(self.post_loop)
        self.loop_worker.finished.connect(self.loop_worker.deleteLater)

        self._loop_counter += 1

    @Slot()
    def step(self):
        if not self.grid.move(self.grid.active_tetrimino, 0, -1):
            self.loop_worker.stop()

    @Slot()
    def post_loop(self):
        self.grid.reset_hold()
        self.grid.update_cells(self.grid.active_tetrimino)

        completed_rows = self.grid.process_completed_rows()

        self.update_score(completed_rows)
        self.update_level(completed_rows)

        self.remove_empty_groups()

        self.init_loop()

    @classmethod
    def start(cls):
        self = cls()
        self.showMinimized()
        self.parent().installEventFilter(self) # install keyboardCatcher

        hud_countdown("Starts in", sec=3)

        self.init_loop()