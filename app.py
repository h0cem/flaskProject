import random
from datetime import datetime, timedelta

from flask import Flask, render_template, jsonify
import graph as G
import graph_to_d3 as d3
import simulated_annealing as sa
import genetic_algo as ga

app = Flask(__name__)


def create_random_d3_graph_dict():
    """
    Creates a random NetworkX graph and returns a dictionary
    representation of the graph formatted for visualization in d3
    """
    random.seed()
    min_person = 4
    max_person = 15
    # S: 70%,    I: 30%  ==> 30% population is infected
    p_susceptible = 0.7
    n = 20
    f = 4
    p = 0.2
    budget = 0.5

    # create graph
    g = G.Graph(n, f, p, min_person, max_person, p_susceptible).create_graph()

    # simulated annealing
    initial_temp = 1
    final_temp = 0
    alpha = 0.01

    # genetic algo
    size = 7

    generation = 15
    p_mutation = 0.05
    p_crossover = 0.9

    elite = 0

    selection_strategy = ["random", "roulette_wheel", "tournament"]
    crossover_strategy = ["one_point", "two_point"]

    graph = sa.SimulatedAnnealing(g, budget=budget, initial_temp=initial_temp, final_temp=final_temp, alpha=alpha)

    graph2 = ga.GA(graph=g, generation=generation, size=size, elite=elite, budget=budget,
                   selection_strategy=selection_strategy[0], crossover_strategy=crossover_strategy[1],
                   p_mutation=p_mutation, p_crossover=p_crossover)

    graph3 = ga.GA(graph=g, generation=generation, size=size, elite=elite, budget=budget,
                   selection_strategy=selection_strategy[1], crossover_strategy=crossover_strategy[1],
                   p_mutation=p_mutation, p_crossover=p_crossover)

    graph4 = ga.GA(graph=g, generation=generation, size=size, elite=elite, budget=budget,
                   selection_strategy=selection_strategy[2], crossover_strategy=crossover_strategy[1],
                   p_mutation=p_mutation, p_crossover=p_crossover)

    # while 1:
    print("############################################")
    print("Simulated Annealing              ", end='   ')
    graph.simulated_annealing()
    print("AG.. random selection            ", end='   ')
    graph2.ga()
    print("AG.. roulette wheel selection    ", end='   ')
    graph3.ga()
    print("AG.. tournament selection        ", end='   ')
    graph4.ga()

    graph_dict = d3.graph_to_dict(g)
    d3_graph = d3.d3_format(graph_dict)
    return d3_graph


d3_graph_dict = create_random_d3_graph_dict()


@app.route('/data')
def get_data():
    # create a random graph and return json via flask
    d3.export_json(d3_graph_dict)
    return jsonify(dict(data=d3_graph_dict))


@app.route('/')
def index():
    # client will ask for graph data from /data route
    d3.export_json(d3_graph_dict)
    return render_template("index.html", g=d3_graph_dict)


if __name__ == '__main__':
    host_name = 'localhost'
    port_num = 5000
    app.run(debug=True, host=host_name, port=port_num)
