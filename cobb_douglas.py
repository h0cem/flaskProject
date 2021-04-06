import random

"""
The Cobb-Douglas production function calculator helps you calculate the total production of a product according
to Cobb-Douglas production function. Briefly, a production function shows the relationship between the output of
goods and the combination of factors used to obtain it.

The Cobb-Douglas production function formula for a single good with two factors of production
is expressed as following: Y = A * Lᵝ * Kᵅ,
    Y is the total production or output of goods. (the real value of all goods produced in a year or 365.25 days)
    A is the total factor productivity. It is a positive constant, and is used to show the change in output
        that is not the result of main production factors.
    L (workers) is the labor input which indicates the total number of labor that went into production.
        (person-hours worked in a year or 365.25 days)
    K is the capital input (a measure of all machinery, equipment, and buildings; the value of capital input
        divided by the price of capital)
    α ([0, 1] ) is the output elasticity of capital.
    β ([0, 1] ) is the output elasticity of labor.

For example, the firm could produce 25 units of output by using 25 units of capital and 25 of labor,
  or it could produce the same 25 units of output with 125 units of labor and only one unit of capital.

The yield is:       rendement
    constant   : α + β = 1,
    increasing : α + β > 1,
    decreasing : α + β < 1
"""


def total_factor_productivity(a, b):
    return random.uniform(a, b)


def get_alpha():
    return random.random()


def get_beta():
    return random.random()


def capital():
    return random.randrange(100, 1000, 1)


def cobb_douglas(g, facility):
    """
        Y = A * Lᵝ * Kᵅ,
    """
    tfp = g.nodes[facility]['tfp']
    alpha = g.nodes[facility]['alpha']
    beta = g.nodes[facility]['beta']
    k = g.nodes[facility]['capital']
    labor = g.nodes[facility]['degree']
    return tfp * (labor ** beta) * (k ** alpha)
