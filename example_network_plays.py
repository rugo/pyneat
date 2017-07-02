"""
Let a trained neuronal network play Mario.
"""
from sys import exit
from gaming.emulator import NES
from gaming.nes.SuperMarioBros import SuperMarioBros

try:
    import MultiNEAT as NEAT
except ImportError:
    print("For this example you need the MultiNeat package "
          "with Python bindings from: https://github.com/peter-ch/MultiNEAT")
    exit(1)

# Where we stored the trained network
GENOME_FILE = "res/network.gen"

mario_game = SuperMarioBros(True, 4, 2, 4)
mario_game.press_key(NES.KEY_RIGHT)

# this creates a neural network (phenotype) from the genome
genome = NEAT.Genome(GENOME_FILE)
net = NEAT.NeuralNetwork()
genome.BuildPhenotype(net)

# Run the game
while True:
    mario_game.run() # run one frame frame

    inputs = mario_game.get_normalized_inputs()
    net.Input(inputs)
    net.Activate()
    output = net.Output()

    if output[0] > 0.7:
        mario_game.press_key(NES.KEY_A)  # jump
