"""
---------------------Tetris For Maya----------------------------------


Author: Mathieu BOUZARD
Date : 04-2022
Version : 3.0.0

Warnings:
    Only work on Maya 2022+

---------------------------------------------------------------------
"""
from .game import Game


def launch_game():
    Game.start()
