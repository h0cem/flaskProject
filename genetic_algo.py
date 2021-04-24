import sys
import random
import tools as t  # covid graph
from termcolor import colored
import numpy as np
import matplotlib.pyplot as plt  # to plot
from datetime import datetime, timedelta


class GA:
    """
    size: population size
    graph: covid graph that was created randomly
    n: numpy vector have id of nodes
    population: population that have (size) m individuals
    """

    solution = []
    gen = []

    def __init__(self, graph, generation, size, budget, elite, selection_strategy, crossover_strategy, p_mutation,
                 p_crossover, k):
        self.graph = graph
        self.generation = generation
        self.size = size
        self.budget = budget
        self.elite = elite
        self.selection_strategy = selection_strategy
        self.crossover_strategy = crossover_strategy
        self.P_CROSSOVER = p_crossover
        self.P_MUTATION = p_mutation
        self.tournament_k = k

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
        generation = 0

        self.gen = []
        self.solution = []

        start_time = datetime.now()

        old_pop = self.population
        self.solution.append(min(old_pop, key=lambda x: x.fitness).fitness)
        self.gen.append(generation)

        random.seed()
        while generation < self.generation and datetime.now() - start_time < timedelta(seconds=50):
            # create a new population
            new_pop = []
            # the new population must have the same size
            while len(new_pop) < self.size and datetime.now() - start_time < timedelta(seconds=50):

                start = datetime.now()

                parent_1 = []
                parent_2 = []
                # SELECTION :: check if parent_1 != parent_2
                while True and datetime.now() - start < timedelta(seconds=8):
                    parent_1 = self.selection(old_pop)
                    parent_2 = self.selection(old_pop)
                    if not self.check_if_same_parents(parent_1, parent_2):
                        break

                # CrossOver if random < p_crossover
                if random.random() < self.P_CROSSOVER:
                    child_1, child_2 = self.crossover(parent_1, parent_2)

                    # Mutation
                    self.mutation(child_1)
                    # Add child
                    if not new_pop and self.fitness(child_1):
                        new_pop.append(child_1)
                    else:
                        if not self.check_if_in_population(new_pop, child_1) and self.fitness(child_1):
                            new_pop.append(child_1)
                    # check size of population then add child
                    if len(new_pop) < self.size:
                        # Mutation
                        self.mutation(child_2)
                        if not self.check_if_in_population(new_pop, child_2) and self.fitness(child_2):
                            new_pop.append(child_2)
                    else:
                        break

                # if no crossover happens, we will chose the best of parents and add it to the population
                else:
                    if len(new_pop) < self.size:
                        if parent_1.fitness < parent_2.fitness:
                            # Mutation
                            self.mutation(parent_1)
                            if not new_pop and self.fitness(parent_1):
                                new_pop.append(parent_1)
                            else:
                                if not self.check_if_in_population(new_pop, parent_1) and self.fitness(parent_1):
                                    new_pop.append(parent_1)
                        else:
                            # Mutation
                            self.mutation(parent_2)
                            if not new_pop and self.fitness(parent_2):
                                new_pop.append(parent_2)
                            else:
                                if not self.check_if_in_population(new_pop, parent_2) and self.fitness(parent_2):
                                    new_pop.append(parent_2)

            old_pop = new_pop
            generation += 1
            self.solution.append(min(old_pop, key=lambda x: x.fitness).fitness)
            self.gen.append(generation)

        plt.figure()
        plt.title("risk")
        # plt.plot(self.solution)
        plt.plot(sorted(self.solution, reverse=True))
        plt.show()

        print("best risk: ", min(self.solution))

    def print_chromosome(self, i):
        for j in i.individual:
            # print(j.id, end=' ')
            if j.isolated:
                print("0", end='  ')
            else:
                print("1", end='  ')
        print(i.fitness)

    def create_individual(self):
        individual = []
        for i in range(len(self.persons_id)):
            individual.append(t.Gene(self.persons_id[i], random.choice([True, False])))
        return individual

    def create_neighbor(self, individual):
        neighbor = individual.copy()
        n = len(self.persons_id) - 1
        # while True:
        offset = random.randint(0, n)
        if neighbor[offset].isolated:
            neighbor[offset].isolated = False
            # break
        return neighbor

    def create_population(self):
        # here we create the population
        population = []
        i = 0
        individual = self.create_individual()
        while i < self.size:
            g = self.graph.copy()
            t.update_copy_graph_attr(g, individual)
            if t.check_budget(g, self.budget):
                chromosome = t.Individual(individual, t.sum_risk_persons(g))
                if not population:
                    population.append(chromosome)
                    i += 1
                else:
                    if not self.check_if_in_population(population, chromosome):
                        population.append(chromosome)
                        i += 1
                individual = self.create_individual()
            else:
                individual = self.create_neighbor(individual)
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

    def fitness(self, child):
        """
            Fitness
        The fitness of each individual is what defines what we are optimizing for, so that, given a chromosome
        encoding a specific solution to a problem, its fitness will correspond to how well that particular individual
        fares as a solution to the problem. Therefore, the higher its fitness value, the more optimal that solution is.

        After all, individuals have their fitness score calculated, they are sorted, so that the fittest individuals
        can be selected for crossover.
        """
        g = self.update_graph_attr(child)
        if self.constraint(g):
            child.fitness = t.sum_risk_persons(g)
            return True
        else:
            return False
        #     g = self.reparation(child)
        #     child.fitness = t.sum_risk_persons(g)

    def reparation(self, chromosome):
        g = self.update_graph_attr(chromosome)
        n = len(self.persons_id) - 1
        while not self.constraint(g):
            offset = random.randint(0, n)
            if chromosome.individual[offset].isolated:
                chromosome.individual[offset].isolated = False
            else:
                chromosome.individual[offset].isolated = True

            g = self.update_graph_attr(chromosome)
        return g

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
        if random.random() < self.P_MUTATION:
            self.mutate(chromosome)

    def mutate(self, chromosome):
        n = len(self.persons_id) - 1
        offset = random.randint(0, n)
        if chromosome.individual[offset].isolated:
            chromosome.individual[offset].isolated = False
        else:
            chromosome.individual[offset].isolated = True

    def num_isolated(self, chromosome):
        count = 0
        for i in chromosome.individual:
            if i.isolated:
                count += 1
        return count

    def check_duplications(self, pop1, pop2):
        check = True
        for i in range(self.size):
            for j in range(self.size):
                if i == j:
                    continue
                if not self.check_if_same_parents(pop1[i], pop2[j]):
                    check = False
                else:
                    return True
        return check

    def check_if_in_population(self, pop, chromosome):
        check = False
        for i in pop:
            if self.check_if_same_parents(i, chromosome):
                return True
        return check

    def check_if_same_parents(self, parent_1, parent_2):
        check = False
        n = len(self.persons_id)
        for i in range(n):
            a = parent_1.individual[i].isolated
            b = parent_2.individual[i].isolated
            if a == b:
                check = True
            else:
                return False
        return check

    def print_parents(self, parent_1, parent_2):
        print('parent_1 == parent_2')
        for j in parent_1.individual:
            print(j.id, j.isolated, end='   ')
        print(parent_1.fitness)
        for j in parent_2.individual:
            print(j.id, j.isolated, end='   ')
        print(parent_2.fitness)

    def update_graph_attr(self, individual):
        g = self.graph.copy()
        t.update_copy_graph_attr(g, individual.individual)
        return g

    def constraint(self, g):
        return t.check_budget(g, self.budget)

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
            return self.tournament_selection(pop)
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

    def tournament_selection(self, pop):
        """
            In tournament selection, each parent is the fittest out of k randomly chosen chromosomes of the population
        """
        k = self.tournament_k
        n = len(pop) - 1
        # first random selection
        selected = random.randint(0, n)
        while k > 0:
            index = random.randint(0, n)
            # check if better (e.g. perform a tournament)
            if pop[index].fitness <= pop[selected].fitness:
                selected = index
            k -= 1
        return pop[selected]

    def best_selection(self, pop):
        return min(pop, key=lambda x: x.fitness)

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
            return self.two_points_crossover(parent_1, parent_2)
        else:
            print(colored('Error: undefined CrossOver strategy', 'red'))

    def one_point_crossover(self, parent_1, parent_2):
        """
        TODO:
            1. check offset of crossOver value ... done
            3. pretty print
            4. random selection with same parent
            5. check redandante ... in pop
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

    def two_points_crossover(self, parent_1, parent_2):
        """
        TODO:
            1. check offset of crossOver value ... done
            3. pretty print
            4. random selection with same parent
            5. check redandante ... in pop
        https://towardsdatascience.com/introducing-geneal-a-genetic-algorithm-python-library-db69abfc212c
        1. The crossover gene of each offspring is calculated according to the rule given by:
            P_new1 = P_1a - \beta [P_1a-P_2a]
            P_new2 = P_2a 2 \beta [P_1a-P_2a]
        """
        chromosome_1 = []
        chromosome_2 = []
        # generating the random number [0, n] to perform crossover, n is size of individual
        n = len(self.persons_id) - 1
        start = random.randint(0, n)
        end = random.randint(start, n)
        # interchanging the genes
        chromosome_1.extend(parent_1.individual[:start])
        chromosome_1.extend(parent_2.individual[start:end])
        chromosome_1.extend(parent_1.individual[end:])

        chromosome_2.extend(parent_2.individual[:start])
        chromosome_2.extend(parent_1.individual[start:end])
        chromosome_2.extend(parent_2.individual[end:])

        new_chromosome_1 = t.Individual(chromosome_1, sys.maxsize)
        new_chromosome_2 = t.Individual(chromosome_2, sys.maxsize)

        return new_chromosome_1, new_chromosome_2

    def elitism(self, pop, k):
        """
        Elitism reserves two slots in the next generation for the highest scoring chromosome of the current generation,
         without allowing that chromosome to be crossed over in the next generation
        :return: two chromosomes
        """
        sorted_pop = sorted(pop, key=lambda x: x.fitness, reverse=False)
        return sorted_pop[:k]
