import random
from flask import Flask, render_template, jsonify

import exact
import graph as G
import graph_to_d3 as d3
import simulated_annealing as sa
import genetic_algo as ga
import tools as t

app = Flask(__name__)


def create_random_d3_graph_dict():
    """
    Creates a random NetworkX graph and returns a dictionary
    representation of the graph formatted for visualization in d3
    """
    random.seed()
    min_person = 3
    max_person = 20
    # S: 70%,    I: 30%  ==> 30% population is infected
    p_susceptible = 0.7
    n = 25
    f = 5
    p = 0.2
    budget = 0.6

    # create graph
    g = G.Graph(n, f, p, min_person, max_person, p_susceptible).create_graph()

    exact.CPLEX(graph=g, budget=budget, n=n, f=f).build_covid_model()

    # simulated annealing
    initial_temp = 1
    final_temp = 0
    alpha = 0.01

    # genetic algo
    size = 20

    generation = 25
    p_mutation = 0.1
    p_crossover = 0.8

    elite = 0

    selection_strategy = ["random", "roulette_wheel", "tournament"]
    crossover_strategy = ["one_point", "two_point"]
    tournament_k = 2

    graph = sa.SimulatedAnnealing(g, budget=budget, initial_temp=initial_temp, final_temp=final_temp, alpha=alpha)

    graph2 = ga.GA(graph=g, generation=generation, size=size, elite=elite, budget=budget,
                   selection_strategy=selection_strategy[0], crossover_strategy=crossover_strategy[1],
                   p_mutation=p_mutation, p_crossover=p_crossover, k=tournament_k)

    print("############################################")
    print("Simulated Annealing              ", end='   ')
    graph.simulated_annealing()
    print("AG..                             ", end='   ')
    graph2.ga2()


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
