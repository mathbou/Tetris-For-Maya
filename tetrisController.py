import  tetris
reload(tetris)
from tetris import Tetris
import os

class Controller(object):
    def __init__(self, ui, name, parent=None):
        self.ui = ui(self, name, parent)

    def show(self):
        self.ui.show()

    def start_game(self):
        tetris = Tetris()
        tetris.launch_game_process()

    def get_icon(self):
        icon_path = "{0}/ressources/logo.ico".format(os.path.dirname(os.path.abspath(__file__)))
        return icon_path