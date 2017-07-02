"""
Train neuronal networks to play mario using HyperNeat.
"""
from gaming.nes.SuperMarioBros import SuperMarioBros
from gaming.emulator import NES
from sys import exit
from time import time
from sys import argv

try:
    import MultiNEAT as NEAT
except ImportError:
    print("For this example you need the MultiNeat package "
          "with Python bindings from: https://github.com/peter-ch/MultiNEAT")
    exit(1)

if len(argv) < 2:
    print("Call as {} experiment_name".format(argv[0]))
    print("Every tenth generation will be saved to disk under this name.")
    exit(2)

# NEAT parameters
params = NEAT.Parameters()
params.PopulationSize = 50

# Create a genome
genome = NEAT.Genome(0,  # id
                     24,  # number of inputs
                     0,  # number of hidden nodes (ignored)
                     1,  # number of output nodes (here only "jump")
                     False,
                     NEAT.ActivationFunction.TANH,  # activation function output
                     NEAT.ActivationFunction.TANH,
                     0,  # seed type
                     params)  # parameters

# Create the population
pop = NEAT.Population(genome, params, True, 5.0, time())  # time() is the RNG seed

# Create the game with a default sight
mario_game = SuperMarioBros(True, 4, 2, 4)
mario_game.press_key(NES.KEY_RIGHT)


def evaluate(genome):
    """
    This function calculates the fitness for a given genome.
    The fitness is the global x position in the game.
    :param genome: Genome to play Mario
    :return: Fitness of genome
    """
    # this creates a neural network (phenotype) from the genome
    net = NEAT.NeuralNetwork()
    genome.BuildPhenotype(net)
    fitness = 0
    stagnating = 0

    # Reset mario to the savegame
    mario_game.reset()

    while True:
        # Run for one frame and get inputs
        mario_game.run()
        inputs = mario_game.get_normalized_inputs()

        # Give inputs to network and get output
        net.Input(inputs)
        net.Activate()
        output = net.Output()
        if output[0] > 0.7:
            mario_game.press_key(NES.KEY_A)

        new_fitness = mario_game.fitness()

        # Kill mario if he doesn't move for 150 frames
        if new_fitness > fitness:
            fitness = new_fitness
        elif fitness - 8 <= new_fitness <= fitness + 8:
            stagnating += 1
            if stagnating >= 150:
                print("Individual was killed. Final fitness: {}".format(fitness))
                break
        else:
            stagnating = 0
    return fitness


fittest = None

for generation in range(100):  # run for 100 generations

    print("Generation {}".format(generation))

    # retrieve a list of all genomes in the population
    genome_list = NEAT.GetGenomeList(pop)

    # apply the evaluation function to all genomes
    for genome in genome_list:
        fitness = evaluate(genome)
        genome.SetFitness(fitness)
        if not fittest or fitness > fittest.Fitness:
            fittest = genome

    print("Fittest: {}".format(fittest.Fitness))

    if not generation % 10:  # save every 10th generation to disk
        pop.Save(argv[1] + ".generation")  # You can later load the population with pop.Load(...)

    # advance to the next generation
    pop.Epoch()
