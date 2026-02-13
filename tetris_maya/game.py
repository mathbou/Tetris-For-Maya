import random
import time
from enum import IntEnum

import maya.cmds as mc
import maya.mel as mel
from PySide2.QtCore import QObject, Signal, QEvent, Slot, QThread, Qt
from PySide2.QtWidgets import QWidget

from .time2 import timer_precision
from .constants import PREFIX, TIME_STEP, SCORE_TABLE, SCORE_HUD_NAME, LEVEL_HUD_NAME, LINES_HUD_NAME
from .grid import Grid, Hold
from .maya2 import hud_countdown, get_main_window
from .tetrimino import TetriminoType

__all__ = ["Game"]


class Action(IntEnum):
    LEFT = Qt.Key.Key_Left
    RIGHT = Qt.Key.Key_Right
    SOFTD = Qt.Key.Key_Down
    HARDD = Qt.Key.Key_Space
    ROTATE_LEFT = Qt.Key.Key_Z
    ROTATE_RIGHT = Qt.Key.Key_Up
    HOLD = Qt.Key.Key_C


class LoopWorker(QObject):
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
                    elif self._is_canceled:
                        self.canceled.emit()
                        return
                    else:
                        time.sleep(f_step)
                    duration += time.perf_counter() - start

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
        self.update_time_step(self._level)
        self.update_tetrimino_queue()

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

    def _prepare_hud(self):
        self._hud_backup = {hud_name: mc.headsUpDisplay(hud_name, query=True, visible=True) for hud_name in mc.headsUpDisplay(query=True, listHeadsUpDisplays=True)}

        # disable current hud
        for hud, visible in self._hud_backup.items():
            if visible:
                mc.headsUpDisplay(hud, edit=True, visible=False)


        # hud score
        mc.headsUpDisplay(
            SCORE_HUD_NAME,
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
            LEVEL_HUD_NAME,
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
            LINES_HUD_NAME,
            section=0,
            block=13,
            blockSize="small",
            label="Lines :",
            command=self.get_lines,
            labelFontSize="large",
            dataFontSize="large",
            attachToRefresh=True,
        )

    def _create_game_camera(self) -> str:
        camera, _ = mc.camera(focalLength=300, nearClipPlane=10,
                              name=f"{PREFIX}_cam")
        mc.lookThru(camera)
        mc.viewFit(camera)
        for attr in ["translate", "rotate"]:
            mc.setAttr(f"{camera}.{attr}", lock=True)

        return camera

    def prepare_viewport(self):
        mel.eval('setNamedPanelLayout("Single Perspective View")')

        self._create_game_camera()

        self._panel_backup = {}
        for attr in ("hud", "grid", "handles"):
            self._panel_backup[attr] = mc.modelEditor("modelPanel4", query=True, **{attr: True})

        mc.modelEditor("modelPanel4", edit=True, hud=True, grid=False, handles=False)

        self._prepare_hud()

    def _restore_hud(self):
        mc.headsUpDisplay(SCORE_HUD_NAME, remove=True)
        mc.headsUpDisplay(LEVEL_HUD_NAME, remove=True)
        mc.headsUpDisplay(LINES_HUD_NAME, remove=True)

        for hud, state in self._hud_backup.items():
            mc.headsUpDisplay(hud, edit=True, visible=state)

    def restore_viewport(self):
        for attr, value in self._panel_backup.items():
            mc.modelEditor("modelPanel4", edit=True, **{attr: value})

        self._restore_hud()

    # -------------- Keyboard Catcher ----------

    def eventFilter(self, watched, event) -> bool:
        if event.type() == QEvent.KeyPress:
            self.move(event.key())
            return True  # Avoid pickWalk trigger
        return super().eventFilter(watched, event)

    # ---------------------- Game Actions ----------------------

    def move(self, value: Action):
        x, y = 0, 0

        if value == Action.LEFT:
            x, y = -1, 0
        elif value == Action.RIGHT:
            x, y = 1, 0
        elif value == Action.SOFTD:
            x, y = 0, -1
            self._score += 1

        elif value == Action.ROTATE_RIGHT:
            self.grid.rotate(self.grid.active_tetrimino, angle=-90)
        elif value == Action.ROTATE_LEFT:
            self.grid.rotate(self.grid.active_tetrimino, angle=90)
        elif value == Action.HARDD:
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
        new_queue = TetriminoType.get_all().copy()
        random.shuffle(new_queue)

        try:
            self.tetrimino_type_queue.extend(new_queue)
        except AttributeError:
            self.tetrimino_type_queue = new_queue

    @property
    def time_step(self) -> float:
        """Value is in second."""
        return self._time_step

    def update_time_step(self, level: int, multiplier: float = 0.5):
        self._time_step = TIME_STEP * (multiplier ** level)

    def remove_empty_groups(self):
        groups = mc.ls(f"{PREFIX}_*grp", exactType="transform")
        for grp in groups:
            if not mc.listRelatives(grp, children=True):
                mc.delete(grp)

    def get_score(self) -> int:
        return self._score

    def update_score(self, rows: int):
        self._score += SCORE_TABLE.get(rows, 0)

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
            self.init_loop()
        elif self.grid.inplace_collision(self.grid.active_tetrimino):
            self.game_over()
        else:
            self.launch_loop_worker()

    @Slot()
    def step(self):
        if not self.grid.move(self.grid.active_tetrimino, 0, -1):
            self.stop_loop_worker()

    @Slot()
    def post_loop(self):
        self.grid.reset_hold()
        self.grid.update_cells(self.grid.active_tetrimino)

        completed_rows = self.grid.process_completed_rows()

        self.update_score(completed_rows)
        self.update_level(completed_rows)

        self.remove_empty_groups()

        self.init_loop()

    def post_hold(self, value: Hold):
        if value is Hold.SWAP:
            self.launch_loop_worker()
        elif value is Hold.PUSH:
            self.init_loop()

    @classmethod
    def start(cls):
        self = cls()
        self.prepare_viewport()
        self.showMinimized()
        self.parent().installEventFilter(self) # install keyboardCatcher

        hud_countdown("Starts in", sec=3)

        self.init_loop()