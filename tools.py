import copy

import networkx as nx


# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# #######################  FUNCTIONS  ########################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

class Gene:
    def __init__(self, node_id, isolated):
        self.id = node_id
        self.isolated = isolated


class Individual:
    def __init__(self, individual, fitness):
        self.individual = individual
        self.fitness = fitness


def print_chromosome(chromosome):
    for gene in chromosome.individual:
        print(gene.id, gene.isolated, end=' ')
    print(chromosome.fitness)


def set_graph_attributes(g):
    risk_facilities(g)
    risk_persons(g)

    remove_infected_persons(g)
    remove_facilities_minP(g)

    income_facilities(g)
    rnb_facilities(g)

    facility_degree(g)


def facility_degree(g):
    for facility in list(g.nodes):
        if g.nodes[facility]['type'] == 'facility':
            g.nodes[facility]['workers'] = g.degree(facility)


def remove_infected_persons(g):
    for person in list(g.nodes):
        if is_infected_person(g, person):
            g.remove_node(person)


def is_infected_person(g, person):
    return g.nodes[person]['type'] == 'person' and g.nodes[person]['status'] == 'I'


def get_persons_id(g):
    # n_id identified of each node in new graph
    n = []
    for node in list(g.nodes):
        if g.nodes[node]['type'] == 'person':
            n.append(g.nodes[node]['id'])
    return n


def risk_facilities(g):
    """
        f_risk: π(π’) = β(π(π£π) β π‘ππππΌπ(π’,π£π))
    """
    for facility in g.nodes:
        if g.nodes[facility]['type'] == 'facility':
            g.nodes[facility]['f_risk'] = risk_facility(g, facility)


def risk_facility(g, facility):
    risk_f = 0
    # get neighbors of facility
    for person in g.neighbors(facility):
        p_infection = g.nodes[person]['p_infection']
        time_in = g[person][facility]['time_in']
        risk_f += f_risk(p_infection, time_in)
    return risk_f


def f_risk(p_infection, time_in):
    return p_infection * time_in


def rnb_facilities(g):
    for facility in g.nodes:
        if g.nodes[facility]['type'] == 'facility':
            g.nodes[facility]['RNB'] = rnb_facility(g, facility)
    return g


def rnb_facility(g, facility):
    return g.nodes[facility]['income'] * g.nodes[facility]['RNB']


def income_facilities(g):
    for facility in g.nodes:
        if g.nodes[facility]['type'] == 'facility':
            g.nodes[facility]['income'] = income_facility(g, facility)
    return g


def income_facility(g, facility):
    income = 0
    # get neighbors of facility
    for person in g.neighbors(facility):
        income += f_income(g, person, facility)
    return income


def f_income(g, person, facility):
    """
    income:: β΅(π£) = βπ‘ππ’π₯ ππ ππππ‘ππππππ‘πππ, β΅(π£) β [0, 1], it's start with 1.
    """
    return g[person][facility]['rate_of_participation']


def sum_risk_persons(g):
    sum_risk = 0
    for person in g.nodes:
        if g.nodes[person]['type'] == 'person':
            sum_risk += g.nodes[person]['risk']
    return sum_risk


def risk_persons(g):
    """
        π(π£) = βπ(v) + β(π(u)βπ(u,u)) + π(u)
    """
    for person in g.nodes:
        if g.nodes[person]['type'] == 'person':
            g.nodes[person]['risk'] = risk_person(g, person)


def risk_person(g, person):
    # βπ(π’)
    sum_risk_facility = sum_f_risk(g, person)
    # β(π(π£)βπ(π£,u))
    sum_distance_infection = sum_dist_infection(g, person)
    p_infection = g.nodes[person]['p_infection']
    # r(v)
    return sum_risk_facility + sum_distance_infection + p_infection


def sum_f_risk(g, person):
    """
        βπ(π’)
    """
    sum_risk_facility = 0
    for facility in g.neighbors(person):
        if g.nodes[facility]['type'] == 'facility':
            sum_risk_facility += g.nodes[facility]['f_risk']
    return sum_risk_facility


def sum_dist_infection(g, person_1):
    """
        β(π(u)βπ(u,v))
    """
    sum_distance_infection = 0
    for person_2 in g.neighbors(person_1):
        if g.nodes[person_2]['type'] == 'person':
            sum_distance_infection += (g.nodes[person_2]['p_infection'] * g[person_1][person_2]['distance'])
    return sum_distance_infection


def remove_facilities_minP(g1: nx):
    """
    if N_person < N_person_min:: remove facility
    """
    for facility in list(g1.nodes):
        if g1.nodes[facility]['type'] == 'facility':
            if facility_min_person(g1, facility):
                g1.remove_node(facility)
            # g.nodes[facility]['workers'] = g.degree(facility)
    return g1


def facility_min_person(g, facility):
    if g.degree(facility) < g.nodes[facility]['min_person']:
        return True


def check_budget(g, budget):
    return (1 - total_RNB(g)) <= budget


def total_RNB(g: nx):
    rnb = 0
    for facility in list(g.nodes):
        if g.nodes[facility]['type'] == 'facility':
            rnb += g.nodes[facility]['RNB']
    return rnb


def remove_isolated_persons(g, individual):
    for person in range(len(individual)):
        if individual[person].isolated:
            g.remove_node(individual[person].id)
    return g


def update_copy_graph_attr(g, individual):
    # for facility in list(g.nodes):
    #     if g.nodes[facility]['type'] == 'facility':
    #         print(g.nodes,g.nodes[facility]['income'], g.nodes[facility]['RNB'], g.degree(facility), sep='   ')

    g1 = copy.deepcopy(g)
    g1 = remove_isolated_persons(g1, individual)
    g1 = remove_facilities_minP(g1)
    g1 = income_facilities(g1)
    g1 = rnb_facilities(g1)

    # print('G1 ---> ', g1.nodes,sum_risk_persons(g1), 1 - total_RNB(g1), sep='   ')
    #
    # for facility in list(g1.nodes):
    #     if g1.nodes[facility]['type'] == 'facility':
    #         print(g1.nodes[facility]['income'], g1.nodes[facility]['RNB'], g1.degree(facility), sep='   ')
    # print()

    return g1
