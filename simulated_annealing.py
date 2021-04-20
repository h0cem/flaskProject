import math
import random
import tools as t
import matplotlib.pyplot as plt  # to plot
import sys


class SimulatedAnnealing:
    # initialize to max
    best_risk = sys.maxsize
    temperatures = []

    def __init__(self, graph, budget, initial_temp, final_temp, alpha):
        random.seed(1)
        self.graph = graph
        self.persons_id = t.get_persons_id(self.graph)
        self.budget = budget
        self.initial_temp = initial_temp
        self.final_temp = final_temp
        self.alpha = alpha

    def constraint(self, g):
        return t.check_budget(g, self.budget)

    def update_graph_attr(self, individual):
        g = self.graph.copy()
        t.update_copy_graph_attr(g, individual)
        return g

    def random_individual(self):
        individual = []
        for i in range(len(self.persons_id)):
            individual.append(t.Gene(self.persons_id[i], random.choice([True, False])))
        return individual

    def create_individual(self):
        individual = self.random_individual()

        g = self.update_graph_attr(individual)
        while not self.constraint(g):
            individual = self.random_individual()
            g = self.update_graph_attr(individual)
        return individual

    def create_neighbor(self, individual):
        neighbor = individual.copy()
        n = len(self.persons_id) - 1
        offset = random.randint(0, n)
        if neighbor[offset].isolated:
            neighbor[offset].isolated = False
        else:
            neighbor[offset].isolated = True
        return neighbor

    def simulated_annealing(self):
        solutions = []
        steps = []
        rand = False
        individual = self.create_individual()
        boolean = False
        current_temp = self.initial_temp
        final_step = int(current_temp / self.alpha)
        step = 0
        # plt.figure()
        # plt.title("risk")
        while current_temp > self.final_temp:
            g = self.graph.copy()

            # get neighbor
            neighbor = self.create_neighbor(individual)

            # update the new graph
            t.update_copy_graph_attr(g, neighbor)

            # calculate fitness
            if t.check_budget(g, self.budget):

                sum_risk = t.sum_risk_persons(g)

                d_risk = sum_risk - self.best_risk

                if d_risk < 0.0:
                    self.best_risk = sum_risk

                    solutions.append(sum_risk)
                    steps.append(current_temp)

                    individual = neighbor

                    boolean = True
                    rand = False
                    step += 1

                # if the new solution is not better, accept it with a probability of e^(-cost/temp)
                else:
                    metropolis = math.exp(-d_risk / current_temp)
                    if random.random() < metropolis:
                        self.best_risk = sum_risk

                        solutions.append(sum_risk)
                        steps.append(current_temp)

                        individual = neighbor

                        boolean = True
                        rand = True
                        step += 1
                # step += 1

                # self.print_solution(g, final_step, step, current_temp, sum_risk, rand)

                # decrement the temperature
                current_temp -= self.alpha
                # plt.scatter(step, self.best_risk)
            # else:
            #     self.print_error(self, final_step, step, current_temp)

        if boolean:
            print("best risk: ", self.best_risk)
            plt.figure()
            plt.title("risk")
            plt.plot(steps, solutions)
            plt.axis([max(steps), min(steps), min(solutions), max(solutions)])
            plt.show()
            # print("solution: \n", solution)
        else:
            print('No solution')
        return individual

    def print_solution(self, g, final_step, step, current_temp, sum_risk, rand):
        print("Step # ",
              final_step, "/", step,
              "  : T = ", current_temp,
              "  Total RNB = ", t.total_RNB(g),
              "  Risk = ", sum_risk,
              "  Best Risk = ", self.best_risk,
              "  Metropolis = ", rand
              )

    def print_error(self, final_step, step, current_temp):
        print("Step # ",
              final_step, "/", step,
              "  : T = ", current_temp,
              "  Budget condition Error"
              )
