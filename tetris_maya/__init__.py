"""---------------------Tetris For Maya----------------------------------


Author: Mathieu BOUZARD
Date : 04-2022
Version : 3.0.0

Warnings:
    Only work on Maya 2022+

---------------------------------------------------------------------
"""
from pathlib import Path

import maya.mel as mel
import pkg_resources

from .game import Game


def launch():
    Game.start()


def install_shelf():
    shelf_location = Path(pkg_resources.resource_filename("tetris_maya", "resources/shelf_Game.mel"))
    mel.eval(f'loadNewShelf "{shelf_location.as_posix()}"')
