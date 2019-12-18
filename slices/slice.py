"""
Define slice types for customer groups: URLLC and mMTC
"""

__author__ = "Haorui Peng"

from nodes.node import Node
import json
import numpy as np


class Slice:
    """
    Slice class, two types

    Attributes
    ----------
    type : URLLC or mMTC
    no_nodes : The number of UEs subscribed to the slice
    traffic_var : dealine mean to priod mean ratio, period varianes, deadline variance, variace variances

    """

    _URLLC = 0
    _mMTC = 1

    def __init__(self, slice_type, no_nodes, traffic_var):
        self.type = slice_type
        self.no_nodes = no_nodes
        pilot_rq = 1
        n_period = 15
        
        ratio = traffic_var[0]
        period_var = traffic_var[1]
        deadline_var = traffic_var[2]
        variance_var = traffic_var[3]
        
        if period_var > 0:
            a, b = self.Beta_shape(0.5, period_var)
            period = self.Beta_Binomial(a, b, n_period, size=no_nodes)   #array mean = 7.5
        else:
            period = np.repeat(n_period/2, no_nodes)   #array of 7.5

        n_deadline = round(n_period * ratio)
        if deadline_var > 0:
            a, b = self.Beta_shape(0.5, deadline_var)
            deadline = self.Beta_Binomial(a, b, n_deadline, size=no_nodes)
        else:
            deadline = period * ratio
        
        if variance_var > 0:
            var_var = abs(np.random.normal(0, np.sqrt(variance_var), size=no_nodes))
        else:
            var_var = np.zeros(no_nodes)
            
        print(period)
        print(deadline)
        print(var_var)
        self.pool = [Node(self.type, pilot_rq, period[i] + 1, deadline[i] + 1, var_var[i]) for i in range(self.no_nodes)]


    def get_node(self, node_id):
        return self.pool[node_id]

    def get_index(self, node):
        return self.pool.index(node)

    
    def Beta_Binomial(self, a, b, n, size=None):
        p = np.random.beta(a, b, size=size)
        r = np.random.binomial(n, p, size=size)

        return r

    def Beta_shape(self, m, v):
        a = m**2 * (1 - m) / v - m
        b = a * (1/m -1 )
        return a, b
