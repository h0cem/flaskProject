import math
import random
import tools as t
import matplotlib.pyplot as plt  # to plot
import sys


class SimulatedAnnealing:
    # initialize to max
    best_risk = sys.maxsize
    solutions = []
    temperatures = []

    def __init__(self, graph, budget, initial_temp, final_temp, alpha):
        random.seed(1)
        self.graph = graph
        self.persons_id = t.get_persons_id(self.graph)
        self.budget = budget
        self.initial_temp = initial_temp
        self.final_temp = final_temp
        self.alpha = alpha

    def create_individual(self):
        individual = []
        for i in range(len(self.persons_id)):
            individual.append(t.Gene(self.persons_id[i], random.choice([True, False])))
        return individual

    def append_output_solution(self, current_temp, sum_risk):
        self.temperatures.append(current_temp)
        self.solutions.append(sum_risk)

    def simulated_annealing(self):
        rand = False
        solution = self.create_individual()
        boolean = False
        current_temp = self.initial_temp
        final_step = int(current_temp / self.alpha)
        step = int(self.initial_temp)
        print("Start simulated_annealing", end='   ')
        # plt.figure()
        # plt.title("risk")
        while current_temp > self.final_temp:
            g = self.graph.copy()

            individual = self.create_individual()
            # update the new graph
            t.update_copy_graph_attr(g, individual)
            # calculate fitness
            if t.check_budget(g, self.budget):
                sum_risk = t.sum_risk_persons(g)
                d_risk = sum_risk - self.best_risk
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
                # self.print_solution(g, final_step, step, current_temp, sum_risk, rand)
                # decrement the temperature
                current_temp -= self.alpha
                step += 1
                # plt.scatter(step, self.best_risk)
            # else:
            #     self.print_error(self, final_step, step, current_temp)
        # plt.show()
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
        plt.plot(self.solutions)
        plt.title("Costs")
        plt.show()
