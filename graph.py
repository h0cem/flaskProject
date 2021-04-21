import random
import networkx as nx
import numpy as np
import numpy.random
import tools as t


class Graph:

    def __init__(self, persons, facilites, cnx, min_person, max_person, p_susceptible):
        self.min_person = min_person
        self.max_person = max_person
        self.p_susceptible = p_susceptible
        self.n = persons
        self.f = facilites
        self.p = cnx

        # Create a random graph, N node
        self.g = nx.gnp_random_graph(self.n, self.p)
        # To make sur that the graph is connected
        # while not nx.is_connected(self.g):
        #     g = nx.erdos_renyi_graph(self.n, self.p)

    def create_graph(self):
        self.init_person()
        self.init_facility()

        t.set_graph_attributes(self.g)
        return self.g

    def init_person(self):
        """
        set a random status of person
        I: Infected, S: Susceptible
        p_infection: probability of infection, p_infection ∈ [0, 1]
        risk: 𝑟(𝑣)=∑𝑅(𝑢)+∑[𝑓(𝑣_𝑖 )∗𝑝(𝑣,𝑣_𝑖 )]+𝑓(𝑣), r ∈ 𝑅
        risk :: how much does the person threaten(menace) the population
        vulnerability, vul ∈ [0, 1]
        S: 70%,    I: 30%  ==> 30% population is infected
        """
        for node in self.g.nodes:
            self.g.nodes[node]['type'] = 'person'
            self.g.nodes[node]['vulnerability'] = random.uniform(0.1, 1)
            self.g.nodes[node]['risk'] = 0
            self.g.nodes[node]['id'] = node
            rand = random.uniform(0, 1)
            if rand > self.p_susceptible:
                self.g.nodes[node]['status'] = 'I'
                self.g.nodes[node]['p_infection'] = random.uniform(0.3, 1)
            else:
                self.g.nodes[node]['status'] = 'S'
                self.g.nodes[node]['p_infection'] = random.uniform(0, 0.3)
        self.person_person_edges()

    def person_person_edges(self):
        # distance: the probability that two people are in contact
        for edge in list(self.g.edges):
            distance = random.uniform(0.05, 1)
            if distance < 0.3:
                self.g.remove_edge(edge[0], edge[1])
            else:
                self.g[edge[0]][edge[1]]['distance'] = distance

    def init_facility(self):
        """
        :param g: Graph
        :param f: Number of facility
        :param n: Number of person
        """
        # generate f random numbers (integer >=0) which sum up to exactly 1
        rnb = np.random.uniform(low=0.0, high=1.0, size=self.f)
        rnb /= np.sum(rnb)
        for i in range(self.f):
            facility = self.n + i
            self.g.add_node(facility)
            # Company attributes
            self.g.nodes[facility]['type'] = 'facility'
            self.g.nodes[facility]['min_person'] = random.randrange(self.min_person, int(self.min_person * 1.5), 1)
            self.g.nodes[facility]['RNB'] = rnb[i]
            self.g.nodes[facility]['income'] = 0
            self.g.nodes[facility]['f_risk'] = 0
            self.g.nodes[facility]['id'] = facility

            employers = random.randrange(self.min_person, self.max_person, 1)
            rate_of_participation = np.random.dirichlet(np.ones(employers), size=1)
            """
            create edges between facility and person 
            add attributes
                ∑rate_of_participation =1 in facility
                time_in: time spent in facility, random time [1, 12] hours / 24 
                    example time_in = 1/3 :: 12 * 1/3 = 4h
            """
            self.person_facility_edges(facility, employers, rate_of_participation)
            # degree of facility
            self.g.nodes[facility]['workers'] = self.g.degree(facility)

    def person_facility_edges(self, facility, employers, rate_of_participation):
        for j in range(employers):
            person = random.randrange(0, self.n, 1)
            if not (self.g.has_edge(person, facility)):
                self.g.add_edge(facility, person)
                self.g[person][facility]['rate_of_participation'] = rate_of_participation[0, j]
                self.g[person][facility]['time_in'] = random.randrange(1, 12, 1) / 12
            else:
                # if edge exist so person participate more in facility
                self.g[person][facility]['rate_of_participation'] += rate_of_participation[0, j]
