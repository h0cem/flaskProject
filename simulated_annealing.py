import math
import random
from datetime import datetime, timedelta

import tools as t
import matplotlib.pyplot as plt  # to plot
import copy


class SimulatedAnnealing:

    def __init__(self, graph, budget, initial_temp, final_temp, alpha):
        self.graph = graph
        self.persons_id = t.get_persons_id(self.graph)
        self.budget = budget
        self.initial_temp = initial_temp
        self.final_temp = final_temp
        self.alpha = alpha

    def simulated_annealing(self):

        # init random
        random.seed(1)
        solutions, steps = [], []

        neighbor = self.create_individual()
        sol = copy.deepcopy(neighbor)

        g = t.update_copy_graph_attr(self.graph, neighbor)
        best_risk = t.sum_risk_persons(g)

        current_temp = self.initial_temp

        solutions.append(best_risk)
        steps.append(current_temp)

        start_time = datetime.now()

        # simulated annealing loop
        while current_temp > self.final_temp and datetime.now() - start_time < timedelta(seconds=15):
            # get neighbor
            # neighbor = self.create_neighbor(sol)
            neighbor = self.create_individual()
            # neighbor = self.create_individual()

            # print("solution: ", len(sol), '..', end=' ')
            # for i in sol:
            #     if not i.isolated:
            #         print(i.id, end=' ')
            # print()
            # print("neighbor: ", len(neighbor), '..', end=' ')
            # for i in neighbor:
            #     if not i.isolated:
            #         print(i.id, end=' ')
            # print('\n')

            # update the new graph
            g = t.update_copy_graph_attr(self.graph, neighbor)

            # calculate fitness
            if self.constraint(g):
                sum_risk = t.sum_risk_persons(g)
                d_risk = sum_risk - best_risk
                if d_risk < 0.0:
                    best_risk = sum_risk
                    sol = copy.deepcopy(neighbor)
                    solutions.append(sum_risk)
                    steps.append(current_temp)
                    # print(g.nodes, end='  ')
                    # print('   ', t.sum_risk_persons(g), 1 - t.total_RNB(g), sep='   ')

                # if the new solution is not better, accept it with a probability of e^(-cost/temp)
                else:
                    metropolis = math.exp(-d_risk / current_temp)
                    if metropolis >= random.uniform(0,1):
                        best_risk = sum_risk
                        sol = copy.deepcopy(neighbor)
                        solutions.append(sum_risk)
                        steps.append(current_temp)
                        # print(g.nodes, end='  ')
                        # print('*** ', t.sum_risk_persons(g), 1 - t.total_RNB(g), sep='   ')

                # decrement the temperature
                current_temp -= self.alpha

        # print(len(solutions))
        self.display(steps=steps, solutions=solutions, sol=sol)

        return sol

    def display(self, steps, solutions, sol):
        # plot
        plt.figure()
        plt.title("risk")
        plt.plot(list(reversed(steps)), solutions)
        plt.show()

        g = t.update_copy_graph_attr(self.graph, sol)

        print("best risk: ", t.sum_risk_persons(g))
        print("cost     : ", 1 - t.total_RNB(g))
        # print(g.nodes)

    def constraint(self, g):
        return t.check_budget(g, self.budget)

    def update_graph_attr(self, individual):
        g = t.update_copy_graph_attr(self.graph, individual)
        return g

    def random_individual(self):
        individual = []
        for i in range(len(self.persons_id)):
            individual.append(t.Gene(self.persons_id[i], random.choice([True, False])))
        return individual

    def no_person_is_isolated(self):
        individual = []
        for i in range(len(self.persons_id)):
            individual.append(t.Gene(self.persons_id[i], False))
        return individual

    def create_individual(self):
        individual = self.random_individual()
        # individual = self.no_person_is_isolated()
        g = self.update_graph_attr(individual)
        while not self.constraint(g):
            individual = self.random_individual()
            g = self.update_graph_attr(individual)

        return individual

    def create_neighbor(self, individual):
        neighbor = copy.deepcopy(individual)
        n = len(self.persons_id) - 1
        while True:
            offset = random.randint(0, n)
            if not neighbor[offset].isolated:
                neighbor[offset].isolated = True
                break
        return neighbor

    def print_solution(self, g, final_step, step, current_temp, sum_risk, rand):
        print("Step # ",
              final_step, "/", step,
              "  : T = ", current_temp,
              "  Total RNB = ", t.total_RNB(g),
              "  Risk = ", sum_risk,
              "  Best Risk = ", self.best_risk,
              "  Metropolis = ", rand
              )
