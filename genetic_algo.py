import sys
import random
import tools as t  # covid graph
from termcolor import colored
import numpy as np


class GA:
    """
    size: population size
    graph: covid graph that was created randomly
    n: numpy vector have id of nodes
    population: population that have (size) m individuals
    """

    def __init__(self, graph, generation, size, budget, elite, selection_strategy, crossover_strategy, p_mutation,
                 p_crossover):
        self.graph = graph
        self.generation = generation
        self.size = size
        self.budget = budget
        self.elite = elite
        self.selection_strategy = selection_strategy
        self.crossover_strategy = crossover_strategy
        self.P_CROSSOVER = p_crossover
        self.P_MUTATION = p_mutation

        self.persons_id = t.get_persons_id(self.graph)
        self.population = self.initialization()

    """
    The genetic algorithm creates three types of children for the next generation:
    1° Elite are the individuals in the current generation with the best fitness values. These individuals automatically
    survive to the next generation. 
    2° Crossover are created by combining the vectors of a pair of parents.
    3° Mutation children are created by introducing random changes, or mutations, to a single parent.
"""

    def ga(self):
        print("Start Genetic Algo       ", end='   ')

        i = 0
        old_pop = self.population
        # plt.figure()
        # plt.title("risk")
        while i < self.generation:
            new_pop = []
            new_pop.extend(self.elitism(old_pop, self.elite))
            while len(new_pop) < self.size:
                # CrossOver if random > p_crossover
                while True:
                    parent_1, parent_2 = self.selection(old_pop), self.selection(old_pop)
                    if parent_1 != parent_2:
                        break
                if random.random() > self.P_CROSSOVER:
                    child_1, child_2 = self.crossover(parent_1, parent_2)
                    if self.fitness(child_1):
                        new_pop.append(child_1)
                    if len(new_pop) < self.size:
                        if self.fitness(child_2):
                            new_pop.append(child_2)
                    else:
                        break
                # if no crossover happens, we will chose the best of parents and add it to the population
                else:
                    if len(new_pop) < self.size:
                        if parent_1.fitness < parent_2.fitness:
                            new_pop.append(parent_1)
                        else:
                            new_pop.append(parent_2)

            # Mutation if random > p_mutation
            for index in range(self.elite, len(self.population)):
                if random.random() > self.P_MUTATION:
                    chromosome = self.mutation(new_pop[index])
                    if self.fitness(chromosome):
                        new_pop[index] = chromosome

            old_pop = new_pop
            i += 1
            # print("#", i, "")
            # plt.scatter(i, risk)
        # plt.show()

        risk = sys.maxsize
        for ind in old_pop:
            risk = min(risk, ind.fitness)
        print("best risk: ", risk)

    def create_individual(self):
        individual = []
        for i in range(len(self.persons_id)):
            individual.append(t.Gene(self.persons_id[i], random.choice([True, False])))
        return individual

    def create_population(self):
        # here we create the population
        population = []
        i = 0
        while i < self.size:
            g = self.graph.copy()
            individual = self.create_individual()
            # for j in individual:
            #     print(j.id, j.isolated, end='    ')
            # print('\n')
            t.update_copy_graph_attr(g, individual)
            if t.check_budget(g, self.budget):
                population.append(t.Individual(self.create_individual(), t.sum_risk_persons(g)))
                i += 1
        # print("--- %s seconds ---" % (time.time() - start_time))
        return population

    def initialization(self):
        """
            Initialization
        The search starts with a random population of N individuals. Each of those individuals corresponds to a
        'chromosome', which encodes a sequence of genes representing a particular solution to the problem we’re trying
        to optimize for. Depending on the problem at hand, the genes representing the solution could be bits
        (0’s and 1’s) or continuous (real valued).
        """
        return self.create_population()

    def fitness(self, individual):
        """
            Fitness
        The fitness of each individual is what defines what we are optimizing for, so that, given a chromosome
        encoding a specific solution to a problem, its fitness will correspond to how well that particular individual
        fares as a solution to the problem. Therefore, the higher its fitness value, the more optimal that solution is.

        After all, individuals have their fitness score calculated, they are sorted, so that the fittest individuals
        can be selected for crossover.
        """
        g = self.graph.copy()
        t.update_copy_graph_attr(g, individual.individual)
        if t.check_budget(g, self.budget):
            individual.fitness = t.sum_risk_persons(g)
            return True
        else:
            return False

    def selection(self, pop):
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
        if self.selection_strategy == "random":
            return self.random_selection(pop)
        elif self.selection_strategy == "roulette_wheel":
            return self.roulette_wheel_selection(pop)
        elif self.selection_strategy == "tournament":
            pass
        elif self.selection_strategy == "pairing":
            pass
        else:
            print(colored('Error: undefined selection strategy', 'red'))

    def random_selection(self, pop):
        """
            random: This strategy consists of randomly selecting individuals from the mating pool.
        :return: individual
        """
        # Return a random parent index from population between 0 and size of population (both included)
        index = random.randint(0, len(pop) - 1)
        return pop[index]

    def roulette_wheel_selection(self, pop):
        """
            This selection will have problems when fitness differs very much
            if chromosome_1 = 90% than other chromosomes will have very few chances to be selected
        """
        # Computes the totality of the population fitness
        population_fitness = sum([1 / chromosome.fitness for chromosome in pop])
        # Computes for each chromosome the probability
        chromosome_probabilities = [1 / chromosome.fitness / population_fitness for chromosome in pop]

        # Making the probabilities for a minimization problem
        chromosome_probabilities = np.array(chromosome_probabilities)

        # Selects one chromosome based on the computed probabilities
        selected = np.random.choice(pop, p=chromosome_probabilities)

        return selected

    def tounament_selection(self, pop):
        k = 3
        # first random selection
        selected = random.randint(len(pop))
        for index in random.randint(0, len(pop) - 1, k - 1):
            # check if better (e.g. perform a tournament)
            if pop[index].fitness < pop[selected].fitness:
                selected = index
        return pop[selected]

    def crossover(self, parent_1, parent_2):
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
        if self.crossover_strategy == "one_point":
            return self.one_point_crossover(parent_1, parent_2)
        elif self.crossover_strategy == "two_point":
            pass
        else:
            print(colored('Error: undefined CrossOver strategy', 'red'))

    def one_point_crossover(self, parent_1, parent_2):
        """
        TODO:
            1. check offset of crossOver value ... done
            3. pretty print
            4. random selection with same parent
        https://towardsdatascience.com/introducing-geneal-a-genetic-algorithm-python-library-db69abfc212c
        1. The crossover gene of each offspring is calculated according to the rule given by:
            P_new1 = P_1a - \beta [P_1a-P_2a]
            P_new2 = P_2a 2 \beta [P_1a-P_2a]
        """
        chromosome_1 = []
        chromosome_2 = []
        # generating the random number [0, n] to perform crossover, n is size of individual
        n = len(self.persons_id) - 1
        offset = random.randint(0, n)

        # interchanging the genes
        chromosome_1.extend(parent_1.individual[:offset])
        chromosome_1.extend(parent_2.individual[offset:])

        chromosome_2.extend(parent_2.individual[:offset])
        chromosome_2.extend(parent_1.individual[offset:])

        new_chromosome_1 = t.Individual(chromosome_1, sys.maxsize)
        new_chromosome_2 = t.Individual(chromosome_2, sys.maxsize)

        return new_chromosome_1, new_chromosome_2

    def mutation(self, chromosome):
        """
        Mutation is the process by which we introduce new genetic material in the population, allowing the algorithm
        to search a larger space. If it were not for mutation, the existing genetic material diversity in a
        population would not increase, and, due to some individuals “dying” between generations, would actually be
        reduced, with individuals tending to become very similar quite fast.
        In terms of the optimization problem, this means that without new genetic material the algorithm can converge
        to local optima before it explores an enough large size of the input space to make sure that we can reach
        the global optimum. Therefore, mutation plays a big role in maintaining diversity in the population
        and allowing it to evolve to fitter solutions to the problem.
        """
        n = len(self.persons_id) - 1
        offset = random.randint(0, n)
        if chromosome.individual[offset].isolated:
            chromosome.individual[offset].isolated = False
        else:
            chromosome.individual[offset].isolated = True
        return chromosome

    def elitism(self, pop, k):
        """
        Elitism reserves two slots in the next generation for the highest scoring chromosome of the current generation,
         without allowing that chromosome to be crossed over in the next generation
        :return: two chromosomes
        """
        sorted_pop = sorted(pop, key=lambda x: x.fitness, reverse=False)
        return sorted_pop[:k]
