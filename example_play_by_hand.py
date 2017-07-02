"""
Play mario interactively with the arrow keys.
"""
from gaming.nes.SuperMarioBros import SuperMarioBros

# The zeros are because we don't use Marios "sight".
mario_game = SuperMarioBros(True, 0, 0, 0, interactive=True)

while True:
    mario_game.run()  # run one frame
