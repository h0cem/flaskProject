import networkx as nx
import numpy as np
import random
import graph as cg  # covid graph
import tools as t  # covid graph


class GA:
    """
    size: population size
    graph: covid graph that was created randomly
    n: numpy vector have id of nodes
    population: population that have (size) m individuals
    TODO:
        1. check if id correspond on value of risk // Done
        2. add risk in function !!! must be done
    """

    def __init__(self, size: int, graph: nx):
        self.size = size
        self.graph = graph

        self.n = t.get_number_of_person_in_graph(self.graph)
        self.population = self.initialization()

    """
        Initialization
    The search starts with a random population of N individuals. Each of those individuals corresponds to a
    'chromosome', which encodes a sequence of genes representing a particular solution to the problem we’re trying
    to optimize for. Depending on the problem at hand, the genes representing the solution could be bits
    (0’s and 1’s) or continuous (real valued).
    """

    def ga(self):
        g = self.graph.copy()
        # self.fitness(g)
        print(t.total_RNB(g))
        return g

    def initialization(self):
        individual_size = len(self.n)
        population = np.ones((self.size, individual_size), dtype=int)
        for i in range(self.size):
            for j in range(individual_size):
                a = 0
                if random.random() < 0.5:
                    a = 1
                population[i][j] = a

        return population

    """
        Fitness
    The fitness of each individual is what defines what we are optimizing for, so that, given a chromosome
    encoding a specific solution to a problem, its fitness will correspond to how well that particular individual
    fares as a solution to the problem. Therefore, the higher its fitness value, the more optimal that solution is.

    After all, individuals have their fitness score calculated, they are sorted, so that the fittest individuals
    can be selected for crossover.
    """

    def fitness(self, g):
        """
        calculate the fitness for all population
        """
        for individual in self.population:
            graph = g.copy()
            # print(g.nodes)
            # print(individual.size)
            t.individual_fitness(graph, individual, self.n)

    """
        Selection
    Selection is the process by which a certain proportion of individuals are selected for mating
    between each other and create new offsprings. Just like in real-life natural selection, individuals that are
    fitter have higher chances of surviving, and therefore, of passing on their genes to the next generation. Though
    versions with more individuals exist, usually the selection process matches two individuals, creating pairs of
    individuals. There are four main strategies:

    pairing: This is perhaps the most straightforward strategy, as it simply consists of pairing the top fittest
    chromosomes two-by-two (pairing odd rows with even ones).

    random: This strategy consists of randomly selecting individuals from the mating pool.

    roulette wheel: This strategy also follows a random principle, but fitter individuals have higher probabilities
    of being selected.

    tournament: With this strategy, the algorithm first selects a few individuals as candidates (usually 3),
    and then selects the fittest individual. This option has the advantage that it does not require the individuals
    to be sorted by fitness first.
    """

    def selection(self):
        pass

    def crossover(self):
        """
            Crossover
        This is the step where new offsprings are generated, which will then replace the least fit
        individuals in the population. The idea behind crossing over individuals is that, by combining different genes,
        we might produce even fitter individuals, which will be better solutions to our problem. Or not, and in that
        case, those solutions won’t survive to the next generations.
        In order to perform the actual crossover, each of the pairs coming from the selection step are combined
        to produce two new individuals each, which will both have genetic material from each of the parents.
        There are several different strategies for performing the crossover, so for brevity,
        we’ll only discuss one of them.
        """

    def facility_cost(self):
        pass

    def constraint(self):
        t.remove_facilities_minP(self.graph)
        # attribute :: facility_risk, income
        cg.update_facility_attributes(self.graph)
