import sys
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

        persons = self.get_persons()
        facilities = self.get_facilities()
        edges = self.get_edges_person_facility()

        # rate_of_participation = exact.get_rate_of_participation(g, n, f)
        mdl = Model(name='Covid-19')

        # --- decision variables ---
        # binary variable for persons
        x = mdl.binary_var_dict(range(self.n), name='x[%s]')

        # binary variable for facilities
        y = mdl.binary_var_dict(range(self.n, self.n + self.f), name='y[%s]')

        # binary variables for edges
        xy = {(i, j): mdl.binary_var(name='x({0}, {1})'.format(i, j)) for i in range(self.n)
              for j in range(self.n, self.n + self.f)}

        # ----------------------------------------------------------------------------
        # Constraint
        # ----------------------------------------------------------------------------

        # add budget constraint:
        facility_income = [mdl.sum(xy[i, j] * edges[i, j]['rate_of_participation']
                                   for i in range(self.n))
                           for j in range(self.n, self.n + self.f)
                           ]
        # facility_rnb = [y[j] * facilities.get(j)['RNB'] * facility_income[j - self.n]

        # total_rbn
        mdl.add_constraint(
            1 - mdl.sum(y[j] * facilities.get(j)['RNB'] * facility_income[j - self.n]
                        for j in range(self.n, self.n + self.f)
                        ) <= 0.5
        )

        # remove facility (min_persons)
        # -------------------------------------------------------------
        M = sys.maxsize
        for j in range(self.n, self.n + self.f):
            facility_degree = mdl.sum(xy[i, j] for i in range(self.n))
            mdl.add_constraint((facility_degree - facilities.get(j)['min_person']) + (1 - y[j]) * M >= 0)

        # remove edges
        # 1. facility
        for j in range(self.n, self.n + self.f):
            facility_degree = mdl.sum(xy[i, j] for i in range(self.n))
            mdl.add_constraint(y[j] * M - facility_degree >= 0)
            mdl.add_constraint((y[j] - 1) - facility_degree <= 0)

        # 2. persons
        for i in range(self.n):
            facility_degree = mdl.sum(xy[i, j] for j in range(self.n, self.n + self.f))
            mdl.add_constraint(x[i] * M - facility_degree >= 0)
            mdl.add_constraint((x[i] - 1) - facility_degree <= 0)

        # ----------------------------------------------------------------------------
        # objective function: minimize the risk
        # ----------------------------------------------------------------------------
        total_risk = mdl.minimize(mdl.sum(x[p] * persons.get(p)['risk'] for p in range(self.n)))
        # mdl.add_kpi(total_risk, 'Total cost')

        mdl_solution = mdl.solve()
        assert mdl_solution
        mdl_solution.display()

    def get_persons(self):
        persons = []
        ids = []
        for node in self.g.nodes():
            if self.g.nodes[node]['type'] == 'person':
                new_node = {"id": self.g.nodes[node]['id'],
                            "risk": self.g.nodes[node]['risk']}
                persons.append(new_node)
                ids.append(self.g.nodes[node]['id'])
        return dict(zip(ids, persons))

    def get_facilities(self):
        facilities = []
        ids = []
        for node in self.g.nodes():
            if self.g.nodes[node]['type'] != 'person':
                new_node = {"id": self.g.nodes[node]['id'],
                            "min_person": self.g.nodes[node]['min_person'],
                            "RNB": self.g.nodes[node]['RNB'],
                            "income": self.g.nodes[node]['income']}
                ids.append(self.g.nodes[node]['id'])
                facilities.append(new_node)

        return dict(zip(ids, facilities))

    def create_ids_edges(self):
        edges = []
        for i in range(self.n):
            for j in range(self.n, self.f + self.n):
                edges.append((i, j))
        return edges

    def get_edges_person_facility(self):
        edges = []
        ids = self.create_ids_edges()

        for edge in ids:
            if self.g.has_edge(edge[0], edge[1]):
                if 'rate_of_participation' in self.g[edge[0]][edge[1]]:
                    new_edge = {"source": edge[0],
                                "target": edge[1],
                                "rate_of_participation": self.g[edge[0]][edge[1]]['rate_of_participation']}
                    edges.append(new_edge)
            else:
                new_edge = {"source": edge[0],
                            "target": edge[1],
                            "rate_of_participation": 0}
                edges.append(new_edge)

        return dict(zip(ids, edges))

    def get_id_of_facilities(self):
        ids = []
        for node in self.g.nodes():
            if self.g.nodes[node]['type'] != 'person':
                ids.append(self.g.nodes[node]['id'])

        return ids

    def get_number_of_edges(self):
        count = 0

        for edge in self.g.edges():
            if 'rate_of_participation' in self.g[edge[0]][edge[1]]:
                count += 1

        return count
