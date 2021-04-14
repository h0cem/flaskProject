from flask import Flask, render_template, jsonify
from graph import random_graph
import graph_to_d3 as d3
import simulated_annealing as sa

app = Flask(__name__)


def create_random_d3_graph_dict():
    """
    Creates a random NetworkX graph and returns a dictionary
    representation of the graph formatted for visualization in d3
    """
    n = 20
    f = 9
    p = 0.15
    g = random_graph(n, f, p)

    graph = sa.SimulatedAnnealing(g)
    graph.simulated_annealing(.4)
    graph.see_annealing()

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
