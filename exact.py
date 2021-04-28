from datetime import datetime

from docplex.mp.model import Model


class CPLEX:

    def __init__(self, graph, budget, n, f):
        self.g = graph
        self.budget = budget
        self.n = n
        self.f = f

    def build_covid_model(self):
        # ----------------------------------------------------------------------------
        # Initialize the problem data
        # ----------------------------------------------------------------------------

        start_time = datetime.now()

        persons = self.get_persons()
        facilities = self.get_facilities()
        edges = self.get_edges_person_facility()

        # rate_of_participation = exact.get_rate_of_participation(g, n, f)
        mdl = Model(name='Covid-19')

        # --- decision variables ---
        # binary variable for persons
        x = {i: mdl.binary_var(name='x[{0}]'.format(i)) for i in persons}

        # binary variable for facilities
        y = {j: mdl.binary_var(name='y[{0}]'.format(j)) for j in facilities}

        # binary variables for edges
        xy = {(e[0], e[1]): mdl.binary_var(name='x({0}, {1})'.format(e[0], e[1])) for e in edges}

        # ----------------------------------------------------------------------------
        # Constraint
        # ----------------------------------------------------------------------------

        # add budget constraint:
        facility_income = {j: mdl.sum(xy.get((i, j), 0) * edges.get((i, j), 0) for i in persons) for j in facilities}
        # facility_rnb = [y[j] * facilities.get(j)['RNB'] * facility_income[j - self.n]

        s = mdl.sum(y.get(j) * facilities.get(j)['RNB'] * facility_income.get(j) for j in facilities)

        # total_cost
        a = mdl.add_constraint(
            1 - mdl.sum(y.get(j) * facilities.get(j)['RNB'] * facility_income.get(j)
                        for j in facilities
                        ) <= self.budget
        )

        M = 999
        # remove facility (min_persons)
        for j in facilities:
            facility_degree = mdl.sum(xy.get((i, j), 0) for i in persons)
            # print(facilities.get(j)['min_person'])
            mdl.add_constraint((1 - y.get(j)) * M + facility_degree - facilities.get(j)['min_person'] >= 0)

        # remove edges
        # 1. facility
        for j in facilities:
            facility_degree = mdl.sum(xy.get((i, j), 0) for i in persons)
            mdl.add_constraint(y.get(j) * M - facility_degree >= 0)
            mdl.add_constraint((y.get(j) - 1) - facility_degree <= 0)

        # 2. persons
        for i in persons:
            person_degree = mdl.sum(xy.get((i, j), 0) for j in facilities)
            mdl.add_constraint(x.get(i) * M - person_degree >= 0)
            mdl.add_constraint((x.get(i) - 1) - person_degree <= 0)

        # ----------------------------------------------------------------------------
        # objective function: minimize the risk
        # ----------------------------------------------------------------------------
        # total_risk
        mdl.minimize(mdl.sum(x.get(i) * persons.get(i)['risk'] for i in persons))

        # ----------------------------------------------------------------------------
        # Solve the model and display the result
        # ----------------------------------------------------------------------------
        mdl.print_information()

        mdl_solution = mdl.solve()
        assert mdl_solution
        mdl_solution.display()
        print(datetime.now() - start_time)

    def get_persons(self):
        ids = []
        persons = []

        for node in self.g.nodes():
            if self.g.nodes[node]['type'] == 'person':
                new_node = {"id": self.g.nodes[node]['id'],
                            "risk": self.g.nodes[node]['risk'],
                            "p_infection": self.g.nodes[node]['p_infection']}
                persons.append(new_node)
                ids.append(node)

        return dict(zip(ids, persons))

    def get_facilities(self):
        ids = []
        facilities = []

        for node in self.g.nodes():
            if self.g.nodes[node]['type'] != 'person':
                new_node = {"id": self.g.nodes[node]['id'],
                            "min_person": self.g.nodes[node]['min_person'],
                            "RNB": self.g.nodes[node]['RNB'],
                            "income": self.g.nodes[node]['income']}
                facilities.append(new_node)
                ids.append(node)

        return dict(zip(ids, facilities))

    def get_edges_person_facility(self):
        edges = []
        ids = []

        for edge in self.g.edges():
            if 'rate_of_participation' in self.g[edge[0]][edge[1]]:
                edges.append(self.g[edge[0]][edge[1]]['rate_of_participation'])
                ids.append(edge)

        return dict(zip(ids, edges))
