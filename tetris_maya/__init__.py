from .game import Game
from .time2 import timer_precision


def launch_game():
    with timer_precision():
        Game.start()


# TODO bug de rotation quand collé a gauche
# TODO bug de rotation quand collé en haut
# TODO bug le harddrop ne descend pas toujours jusqu'en bas
