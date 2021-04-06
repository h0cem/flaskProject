import numpy as np
import matplotlib.pyplot as plt
import operator

from scipy.stats import poisson
import networkx as nx
from networkx.algorithms import bipartite

from scipy.stats import expon


def power_law(k_min, k_max, y, gamma):
    return ((k_max ** (-gamma + 1) - k_min ** (-gamma + 1)) * y + k_min ** (-gamma + 1.0)) ** (1.0 / (-gamma + 1.0))


TESTS = 1

# Number of facilities
Facilities = 500

# Minimum size of a company
k_min = 4

# Maximum size of a company
k_max = 1000

# Power law exponent for the size of the factories
gamma = 1.1

# Average number of activities per day
activities = 4

# Power law exponent for the infection chance of people
gamma2 = 10

# The percentage of the total budget
how_much_budget = 0.01

# How many people can be quarantined with our given budget
frac_people = 0.01

# Cost of the facilities
norm_mean = 1.1
norm_std = 0.4

# We divide the available budget
dB = 0.2

my_plot_rules = []

for dB in np.arange(0, 1.01, 0.05):
    avg_risk = 0
    max_risk = 0
    min_risk = 10000

    for tests in range(TESTS):

        # Distributing people to facilities
        size_fac = np.zeros(Facilities, int)
        y = np.zeros(Facilities, float)
        for n in range(Facilities):
            y[n] = np.random.uniform(0, 1)
            size_fac[n] = int(power_law(k_min, k_max, y[n], gamma))

        # plt.plot(range(1,Facilities+1),sorted(size_fac,reverse=True),'ro')
        # plt.show()

        # exit()

        # this is the total number of visits to facilities
        Total_visitors = int(sum(size_fac))
        # print("Total visitors " + str(Total_visitors))

        # Population size
        People = int(Total_visitors / activities)
        # print("Population " + str(People))

        # Creating the graph
        G = nx.Graph()

        # People are numbered from 0 to People and Facilities from People + 1 to People + Facilities -1
        nodes = list(range(People)) + list(map(lambda x: x + People, range(Facilities)))
        G.add_nodes_from(nodes)
        # print(nodes)

        neighbor = list([] for i in range(People))

        count = np.zeros(People, int)
        adj_list = []
        for i in range(Facilities):
            adj_list.append(list(np.random.randint(0, People, size_fac[i])))
            # print(adj_list[i])
            for j in adj_list[i]:
                count[j] = count[j] + 1
                neighbor[j].append(i)
                # G.add_edge(j,i+People)

        # nx.draw(G)
        ### Sanity check 1 ###

        pois = np.zeros(int(max(count)) + 1, int)
        for i in range(People):
            pois[int(count[i])] = pois[int(count[i])] + 1

        # print (sorted(pois))
        # plt.plot(range(int(max(count))+1),pois,'ro')
        # plt.show()

        #### Sanity check 1 End: We have indeed poisson distribution

        for i in range(People):
            data_expon = expon.rvs(scale=6, loc=1, size=count[i])
            z = sum(data_expon)
            data_norm = list(map(lambda x: float(x / z), data_expon))
            # print(len(data_norm))
            # print(len(neighbor[i]))
            # print(count[i])
            # plt.plot(range(count[i]),sorted(data_norm,reverse=True),'ro')
            # plt.show()

            k = 0
            # print(data_norm)
            for j in neighbor[i]:
                G.add_edge(i, People + j, weight=data_norm[k])
                k = k + 1

        # print(nx.is_bipartite(G))
        # nx.draw(G)

        f = np.zeros(People)
        for n in range(People):
            f[n] = power_law(0.01, 0.99, np.random.uniform(0, 1), gamma2)

        # Calculating the risk of a facility
        R = np.zeros(Facilities)
        for i in range(Facilities):
            for j in G.edges(People + i, data='weight'):
                R[i] = R[i] + f[j[1]] * j[2]

        # plt.plot(scale_free_distribution,R,'ro')
        # plt.show()

        # Calculating the risk of the people
        r = np.zeros(People)
        for i in range(People):
            for j in G.edges(i, data='weight'):
                r[i] = r[i] + R[j[1] - People] * j[2]

        # plt.plot(range(People),sorted(r),'ro')
        # plt.show()

        OriginalRisk = sum(r)

        # Cost of the facilities
        cost = np.zeros(Facilities)
        for i in range(Facilities):
            # select poisson variable
            x = np.random.normal(norm_mean, norm_std)
            cost[i] = size_fac[i] ** x

        # plt.plot(size_fac,cost,'ro')
        # plt.show()

        efficiency = np.zeros((Facilities, 2))
        for i in range(Facilities):
            efficiency[i][0] = i
            efficiency[i][1] = cost[i] / R[i]

        # print (sorted(efficiency,key = operator.itemgetter(1)))

        # set the the budget
        B = how_much_budget * sum(cost)

        # set the parameters for quaranteening people
        a = B / People * 1 / frac_people
        b = 0

        # print("Budget " + str(B))
        # print("Quarantine budget " + str(dB*B))
        # print(cost)
        # list of quarantined people
        qp = []

        # list of closed facilities
        cf = []

        # deciding the list of people that have to be quarantined
        r2 = np.zeros((People, 2))
        for i in range(People):
            r2[i][0] = i
            r2[i][1] = r[i]

        sorted_r2 = sorted(r2, key=operator.itemgetter(1), reverse=True)
        q_budget = 0

        # print(sorted_r2)

        for i in range(People):
            if q_budget + a + b > dB * B:
                break
            qp.append(int(sorted_r2[i][0]))
            q_budget = q_budget + a + b

        # print(qp,q_budget)

        # Recompute risk R_prime
        R_prime = np.zeros(Facilities)
        for i in range(Facilities):
            for j in G.edges(People + i, data='weight'):
                if j[1] not in qp:
                    R_prime[i] = R_prime[i] + f[j[1]] * j[2]

        efficiency2 = np.zeros((Facilities, 2))
        for i in range(Facilities):
            efficiency2[i][0] = i
            efficiency2[i][1] = cost[i] / R_prime[i]

        sorted_efficiency = sorted(efficiency2, key=operator.itemgetter(1))

        # Close the facilities
        q_fac = 0

        for i in range(Facilities):
            if q_fac + cost[int(sorted_efficiency[i][0])] <= B - q_budget:
                cf.append(int(sorted_efficiency[i][0]))
                q_fac = q_fac + cost[int(sorted_efficiency[i][0])]

        # print(q_fac)
        # print(cf)
        # print(cost)
        # print(cost[cf])

        # Compute the risk of the population
        # Calculating the risk of the people
        r_prime = np.zeros(People)
        for i in range(People):
            for j in G.edges(i, data='weight'):
                if i not in qp:
                    if (j[1] - People) not in cf:
                        r_prime[i] = r_prime[i] + R_prime[j[1] - People] * j[2]
                else:
                    r_prime[i] = 0

        # print("Db " + str(dB))
        # print(sum(r_prime) / OriginalRisk)

        s = sum(r_prime / OriginalRisk)

        avg_risk = avg_risk + s
        if s > max_risk:
            max_risk = s
        if s < min_risk:
            min_risk = s

        ## Some nice plots

        # plt.plot(range(People),sorted(r_prime, reverse=True),'ro',range(People),sorted(r,reverse=True),'bo')
        # plt.show()

        # print(R)
        # print(R_prime)
        # plt.plot(range(Facilities),sorted(R, reverse=True),'ro',range(Facilities),sorted(R_prime,reverse=True),'bo')
        # plt.show()

        ## Calculate the total risk

        # plt.plot(sorted(y,reverse=True),sorted(scale_free_distribution, reverse=True),'ro')
        # plt.show()

        # data_binom = poisson.rvs(mu=4, size=10000)
        # print (sum(data_binom))
    print(People, max_risk, min_risk, avg_risk / TESTS)
    my_plot_rules.append(avg_risk / TESTS)

plt.plot(np.arange(0, 1.01, 0.05), my_plot_rules)
# plt.xlabel('Risk per person after the algorithm is run / Initial risk per person')
# plt.ylabel('Size of the facilities')
plt.show()