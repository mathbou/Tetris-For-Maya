from .game import Game


def launch_game():
    Game.start()


# TODO bug de queue, ne respecte pas la règle des 7
# TODO bug de rotation quand collé a gauche
# TODO bug de rotation quand collé en haut
# TODO bug pas de score sur le harddrop
# TODO bug le harddrop ne descend pas toujours jusqu'en bas
