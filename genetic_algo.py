import networkx as nx
import numpy as np
import random
import graph as cg  # covid graph


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

        print("graph_initial: ", graph.nodes)
        update_graph_attributes(self.graph)
        print("facility_min : ", graph.nodes)
        remove_infected_person(self.graph)
        print("graph_update : ", graph.nodes)

        self.n = get_number_of_person_in_graph(self.graph)
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
        print(total_RNB(g))
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
            individual_fitness(graph, individual, self.n)

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
        facility_min_person(self.graph)
        # attribute :: facility_risk, income
        cg.update_facility_attributes(self.graph)


# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# #######################  FUNCTIONS  ########################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

def update_graph_attributes(g):
    facility_min_person(g)
    cg.update_facility_attributes(g)
    # cg.risk_person(g)


def remove_infected_person(g):
    for person in list(g.nodes):
        if g.nodes[person]['type'] == 'person' and g.nodes[person]['status'] == 'I':
            g.remove_node(person)


def individual_fitness(g: nx, individual, n: np):
    """
    here we calculate the fitness of one individual

    Minimize ∑r(𝑣) sum of risks

    we must recalculate the risk of each person, after deleted or isolate persons, so firs we update facility
    attributes than persons risks and finally check if number of persons in facility is greater than n_min
    """
    # for person in list(g.nodes):
    #     if g.nodes[person]['type'] == 'person' and individual[person] == 0:
    #         g.remove_node(person)

    risk_individual = 0
    i = 0
    for person in n:
        risk_individual += (g.nodes[person]['risk'] * individual[i])
        i += 1
    print(risk_individual)
    print("_____________________")


def get_number_of_person_in_graph(g):
    # n_id identified of each node in new graph
    n = []
    for node in list(g.nodes):
        if g.nodes[node]['type'] == 'person':
            n.append(g.nodes[node]['id'])
    n_id = np.array(n)
    print(n_id)
    return n_id


def check_facility_min_person(g, facility):
    if g.degree(facility) < g.nodes[facility]['min_person']:
        return True


def facility_min_person(g: nx):
    """
    if N_person < N_person_min:: remove facility
    """
    for facility in list(g.nodes):
        if g.nodes[facility]['type'] == 'facility':
            if check_facility_min_person(g, facility):
                g.remove_node(facility)


def total_RNB(g: nx):
    rnb = 0
    for facility in list(g.nodes):
        if g.nodes[facility]['type'] == 'facility':
            rnb += g.nodes[facility]['RNB']
    return rnb
