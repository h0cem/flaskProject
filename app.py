from flask import Flask, render_template, jsonify
from graph import random_graph, graph_to_dict, d3_format, export_json
import genetic_algo as ga
import graph as cg  # covid graph

app = Flask(__name__)


def create_random_d3_graph_dict():
    """
    Creates a random NetworkX graph and returns a dictionary 
    representation of the graph formatted for visualization in d3
    """
    g = random_graph(20, 5, .05)
    ga.update_graph_attributes(g)
    # size = 10
    # test = ga.GA(size, g)
    # graph = test.ga()
    graph_dict = graph_to_dict(g)
    d3_graph_dict = d3_format(graph_dict)
    return d3_graph_dict


@app.route('/data')
def get_data():
    # create a random graph and return json via flask
    d3_graph_dict = create_random_d3_graph_dict()
    return jsonify(dict(data=d3_graph_dict))


@app.route('/')
def index():
    # client will ask for graph data from /data route
    d3_graph_dict = create_random_d3_graph_dict()
    export_json(d3_graph_dict)
    return render_template("index.html")


if __name__ == '__main__':
    host_name = 'localhost'
    port_num = 5000
    app.run(debug=True, host=host_name, port=port_num)
