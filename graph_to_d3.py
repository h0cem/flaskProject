from os import path
from networkx.readwrite import json_graph
import json

basepath = path.dirname(__file__)


def pretty_print(dictionary):
    """
    Prints the given dictionary in human readable format.
    """
    print(dict_to_json_string(dictionary))


def dict_to_json_string(dictionary):
    """
    Returns a json string representation of the given dictionary.
    """
    return json.dumps(dictionary, indent=4, default=lambda x: x.__dict__)


def graph_to_dict(graph):
    """
    Returns a dictionary representation of the given graph.
    """
    return json_graph.node_link_data(graph)


def d3_format(graph_dict):
    """
    Formats a graph dictionary for d3 visualization
    """
    graph_dict.pop("multigraph")
    graph_dict.pop("directed")
    graph_dict.pop("graph")
    return graph_dict


def export_json(dictionary):
    """
    Exports the given dictionary to a json file.
    """
    filepath = path.abspath(path.join(basepath, "static", "json", "graph.json"))
    with open(filepath, 'w') as file:
        json.dump(dictionary, file, indent=4, default=lambda x: x.__dict__)
