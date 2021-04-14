import random
import networkx as nx
import numpy as np
import numpy.random
import tools as t


def init_person(g):
    """
    set a random status of person
    I: Infected, S: Susceptible
    p_infection: probability of infection, p_infection ∈ [0, 1]
    risk: 𝑟(𝑣)=∑𝑅(𝑢)+∑[𝑓(𝑣_𝑖 )∗𝑝(𝑣,𝑣_𝑖 )]+𝑓(𝑣), r ∈ 𝑅
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
    """
    # minimum size of a facility
    min_person = 4
    # maximum size of a facility
    max_person = 10
    # generate f random numbers (integer >=0) which sum up to exactly 1
    rnb = np.random.dirichlet(np.ones(f), size=1)
    for i in range(f):
        facility = n + i
        g.add_node(facility)
        # Company attributes
        g.nodes[facility]['type'] = 'facility'
        g.nodes[facility]['min_person'] = random.randrange(min_person, max_person, 1)
        g.nodes[facility]['RNB'] = rnb[0, i]
        g.nodes[facility]['income'] = 0
        g.nodes[facility]['f_risk'] = 0
        g.nodes[facility]['id'] = facility

        rand = random.randrange(n/20, n/5, 1)
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

        g.nodes[facility]['workers'] = g.degree(facility)


def person_person_edges(g: nx):
    # distance: the probability that two people are in contact
    for edge in list(g.edges):
        distance = random.uniform(0.05, 1)
        if distance < 0.3:
            g.remove_edge(edge[0], edge[1])
        else:
            g[edge[0]][edge[1]]['distance'] = distance


def random_graph(n, f, p):
    # Create a random graph, N node
    g = nx.gnp_random_graph(n, p)
    # To make sur that the graph is connected
    while not nx.is_connected(g):
        g = nx.erdos_renyi_graph(n, p)

    init_person(g)
    init_facility(g, f, n)

    t.set_graph_attributes(g)

    return g
