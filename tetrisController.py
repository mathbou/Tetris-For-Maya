import  tetris
reload(tetris)
from tetris import Tetris

class Controller(object):
    def __init__(self, ui, name, parent=None):
        self.ui = ui(self, name, parent)

    def show(self):
        self.ui.show()

    def start_game(self):
        tetris = Tetris()
        tetris.launch_game_process()

