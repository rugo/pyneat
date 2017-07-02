"""
Let mario jump over enemies by using its sight.
"""
from gaming.emulator import NES
from gaming.nes.SuperMarioBros import SuperMarioBros

# These define the "sight" of mario
SIGHT_Y_UP = 4  # see 4 blocks up
SIGHT_Y_DOWN = 2  # 2 blocks down
SIGHT_X = 4  # 4 blocks wide

mario_game = SuperMarioBros(True,  # show the UI
                            SIGHT_Y_UP,
                            SIGHT_Y_DOWN,
                            SIGHT_X)

# Lets run to the right!
mario_game.press_key(NES.KEY_RIGHT)

while True:
    inputs = mario_game.get_normalized_inputs()  # Get the normalized inputs (the "sight")

    # Print the inputs row wise (as seen on screen)
    print(mario_game.pretty_inputs_string())
    print()

    if -1 in inputs:  # -1 is the normalized rep. of an enemy
        mario_game.press_key(NES.KEY_A)  # jump if there is an enemy in sight

    mario_game.run()  # run one frame
