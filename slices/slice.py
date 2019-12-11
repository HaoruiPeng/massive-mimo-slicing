"""
Define slice types for customer groups: URLLC and mMTC
"""

__author__ = "Haorui Peng"

from nodes.node import Node
import json
import numpy as np
import scipy.stats as stats
from scipy.stats import beta
from scipy.stats import binom


class Slice:
    """
    Slice class, two types

    Attributes
    ----------
    type : URLLC or mMTC
    no_nodes : The number of UEs subscribed to the slice
    traffic : traffic varianes, variace variances

    """

    _URLLC = 0
    _mMTC = 1

    def __init__(self, slice_type, no_nodes, traffic_var=None):
        self.type = slice_type
        self.no_nodes = no_nodes
        # TODO: Taffic is taken
        pilot_rq = 1
        if traffic_var is not None:
            a, b = self.Beta_shape(0.5, traffic_var[0])
            n = 15
            
            deadline = self.Beta_Binomial(a, b, n, size=no_nodes)
            print(deadline)
            var_var = abs(np.random.normal(0, np.sqrt(traffic_var[1]), size=no_nodes))
            print(var_var)
            self.pool = [Node(self.type, pilot_rq, deadline[i] + 1, var_var[i]) for i in range(self.no_nodes)]

        else:
            self.pool = [Node(self.type, pilot_rq, 50, 1) for i in range(self.no_nodes)] # mMTC type, not considered

        
        

    def get_node(self, node_id):
        return self.pool[node_id]

    def get_index(self, node):
        return self.pool.index(node)

    
    def Beta_Binomial(self, a, b, n, size=None):
        p = beta.rvs(a, b, size=size)
        r = binom.rvs(n, p, size=size)

        return r

    def Beta_shape(self, m, v):
        a = m**2 * (1 - m) / v - m
        b = a * (1/m -1 )
        return a, b
