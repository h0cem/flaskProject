import math
import random
import tools as t
import numpy as np
import matplotlib.pyplot as plt  # to plot
import sys


class SimulatedAnnealing:
    # defaults
    initial_temp = 10.0
    final_temp = 0
    alpha = 0.0001
    # initialize to max
    best_risk = sys.maxsize
    solutions = []
    temperatures = []

    def __init__(self, graph):
        random.seed(1)
        self.graph = graph
        self.n = t.get_number_of_person_in_graph(self.graph)

    def create_individual(self):
        individual = np.zeros((len(self.n), 2), dtype=int)
        for i in range(len(self.n)):
            individual[i][0] = self.n[i]
            if random.random() > 0.4:
                individual[i][1] = 1
        return individual

    def update_copy_graph_attr(self, g, individual):
        t.remove_isolated_persons(g, individual)
        t.remove_facilities_minP(g)
        t.income_facilities(g)
        t.rnb_facilities(g)

    def append_output_solution(self, current_temp, sum_risk):
        self.temperatures.append(current_temp)
        self.solutions.append(sum_risk)

    def simulated_annealing(self, budget):
        rand = False
        solution = self.create_individual()
        boolean = False
        current_temp = self.initial_temp
        final_step = int(current_temp / self.alpha)
        step = int(self.initial_temp)
        print("Start simulated_annealing")
        while current_temp > self.final_temp:
            g = self.graph.copy()

            individual = self.create_individual()
            # update the new graph
            self.update_copy_graph_attr(g, individual)
            # calculate fitness
            sum_risk = t.sum_risk_persons(g)
            d_risk = sum_risk - self.best_risk
            if t.check_budget(g, budget):
                if d_risk < 0.0:
                    self.append_output_solution(current_temp, sum_risk)
                    self.best_risk = sum_risk
                    solution = individual
                    boolean = True
                    rand = False
                # if the new solution is not better, accept it with a probability of e^(-cost/temp)
                else:
                    metropolis = math.exp(-d_risk / current_temp)
                    if random.random() < metropolis:
                        self.append_output_solution(current_temp, sum_risk)
                        self.best_risk = sum_risk
                        solution = individual
                        boolean = True
                        rand = True
                self.print_solution(g, final_step, step, current_temp, sum_risk, rand)
                # decrement the temperature
                current_temp -= self.alpha
                step += 1
            # else:
            #     self.print_error(self, final_step, step, current_temp)
        if boolean:
            print("best risk: ", self.best_risk)
            # print("solution: \n", solution)
        else:
            print('No solution')
        return solution

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

    def see_annealing(self):
        plt.figure()
        plt.title("risk")
        plt.plot(self.temperatures, self.solutions)
        plt.title("Costs")
        plt.show()
