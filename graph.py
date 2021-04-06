import random
from os import path
import networkx as nx
from networkx.readwrite import json_graph
import json
import numpy as np
import numpy.random
import cobb_douglas as cd

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


def init_person(g):
    """
    set a random status of person
    I: Infected, S: Susceptible
    p_infection: probability of infection, p_infection ∈ [0, 1]
    risk: 𝑟(𝑣)=∑𝑅(𝑢)+vul(𝑣)∑[𝑓(𝑣_𝑖 )∗𝑝(𝑣,𝑣_𝑖 )]+𝑓(𝑣), r ∈ 𝑅
    risk :: how much does the person threaten(menace) the population
    vulnerability, vul ∈ [0, 1]
    S: 70%,    I: 30%  ==> 30% population is infected
    """
    for node in g.nodes:
        rand = random.uniform(0, 1)
        g.nodes[node]['type'] = 'person'
        g.nodes[node]['vulnerability'] = random.uniform(0.1, 1)
        g.nodes[node]['risk'] = 0
        g.nodes[node]['id'] = node
        if rand > 0.7:
            g.nodes[node]['status'] = 'I'
            g.nodes[node]['p_infection'] = random.uniform(0.3, 1)
        else:
            g.nodes[node]['status'] = 'S'
            g.nodes[node]['p_infection'] = random.uniform(0, 0.3)
    person_person_edges(g)


def init_facility(g, f, n):
    """
    :param g: Graph
    :param f: Number of facility
    :param n: Number of person
    TODO:
     1. verified constraint (new one economics)
     2. start coding GA
    """
    # minimum size of a facility
    min_person = 4
    # maximum size of a facility
    max_person = 8
    # generate f random numbers (integer >=0) which sum up to exactly 1
    rnb = np.random.dirichlet(np.ones(f), size=1)
    for i in range(f):
        facility = n + i
        g.add_node(facility)
        # min_person = random.randrange(min_person, max_person, 1)
        # Company attributes
        g.nodes[facility]['type'] = 'facility'
        g.nodes[facility]['min_person'] = min_person
        g.nodes[facility]['RNB'] = rnb[0, i]
        g.nodes[facility]['income'] = 0
        g.nodes[facility]['f_risk'] = 0
        g.nodes[facility]['id'] = facility

        rand = random.randrange(min_person, max_person, 1)
        rate_of_participation = np.random.dirichlet(np.ones(rand), size=1)
        """
        create edges between facility and person 
        add attributes
            ∑rate_of_participation =1 in facility
            time_in: time spent in facility, random time [1, 12] hours / 24 
                example time_in = 1/3 :: 12 * 1/3 = 4h
        """
        for j in range(rand):
            person = random.randrange(0, n, 1)
            if not (g.has_edge(person, facility)):
                g.add_edge(facility, person)
                g[person][facility]['rate_of_participation'] = rate_of_participation[0, j]
                g[person][facility]['time_in'] = random.randrange(1, 12, 1) / 12
            else:
                # if edge exist so person participate more in facility
                g[person][facility]['rate_of_participation'] += rate_of_participation[0, j]
        # degree of facility :: number of person in facility
        g.nodes[facility]['degree'] = g.degree(facility)
        # attribute for calculate productivity function
        g.nodes[facility]['tfp'] = cd.total_factor_productivity(0, 2)  # total factor productivity :: A
        g.nodes[facility]['alpha'] = cd.get_alpha()  # output elasticity of capital α
        g.nodes[facility]['beta'] = cd.get_beta()  # output elasticity of labor β
        g.nodes[facility]['capital'] = cd.capital()
        g.nodes[facility]['productivity'] = cd.cobb_douglas(g, facility)


def person_person_edges(g: nx):
    # distance: the probability that two people are in contact
    for edge in list(g.edges):
        distance = random.uniform(0.05, 1)
        if distance < 0.3:
            g.remove_edge(edge[0], edge[1])
        else:
            g[edge[0]][edge[1]]['distance'] = distance


def update_facility_attributes(g):
    """
        f_risk: 𝑅(𝑢) = ∑(𝑓(𝑣𝑖) ∗ 𝑡𝑖𝑚𝑒𝐼𝑛(𝑢,𝑣𝑖))
    """
    for facility in g.nodes:
        if g.nodes[facility]['type'] == 'facility':
            # update productivity
            g.nodes[facility]['productivity'] = cd.cobb_douglas(g, facility)
            # get neighbors of facility
            for person in g.neighbors(facility):
                p_infection = g.nodes[person]['p_infection']
                time_in = g[person][facility]['time_in']
                g.nodes[facility]['f_risk'] += facility_risk(p_infection, time_in)
                g.nodes[facility]['income'] += facility_income(g, person, facility)


def risk_person(g):
    """
        𝑟(𝑣) = ∑𝑅(𝑢) + ∑(𝑓(𝑣)∗𝑝(𝑣,u)) + 𝑓(𝑣)
    """
    for person in g.nodes:
        if g.nodes[person]['type'] == 'person':
            # ∑𝑅(𝑢)
            sum_risk_facility = sum_f_risk(g, person)
            # ∑(𝑓(𝑣)∗𝑝(𝑣,u))
            sum_distance_infection = sum_dist_infection(g, person)
            p_infection = g.nodes[person]['p_infection']
            # r(v)
            risk = sum_risk_facility + sum_distance_infection + p_infection
            g.nodes[person]['risk'] = risk


def facility_income(g, person, facility):
    """
    income:: ℵ(𝑣) = ∑𝑡𝑎𝑢𝑥 𝑑𝑒 𝑝𝑎𝑟𝑡𝑖𝑐𝑖𝑝𝑎𝑡𝑖𝑜𝑛, ℵ(𝑣) ∈ [0, 1], it's start with 1.
    """
    return g[person][facility]['rate_of_participation']


def sum_f_risk(g, person):
    """
        ∑𝑅(𝑢)
    """
    sum_risk_facility = 0
    for facility in g.neighbors(person):
        if g.nodes[facility]['type'] == 'facility':
            sum_risk_facility += g.nodes[facility]['f_risk']
    return sum_risk_facility


def facility_risk(p_infection, time_in):
    return p_infection * time_in


def sum_dist_infection(g, person_1):
    """
        ∑(𝑓(𝑣)∗𝑝(𝑣,u))
    """
    sum_distance_infection = 0
    for person_2 in g.neighbors(person_1):
        if g.nodes[person_2]['type'] == 'person':
            sum_distance_infection += (g.nodes[person_2]['p_infection'] * g[person_1][person_2]['distance'])
    return sum_distance_infection


def random_graph(n, f, p):
    # Create a random graph, N node
    g = nx.gnp_random_graph(n, p)
    # To make sur that the graph is connected
    while not nx.is_connected(g):
        g = nx.erdos_renyi_graph(n, p)

    init_person(g)
    init_facility(g, f, n)
    return g
