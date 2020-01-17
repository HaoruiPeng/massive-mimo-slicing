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
        self.deadline = []
        self.period = []

        ratio = traffic_var[0]
        period_var = traffic_var[1]
        deadline_var = traffic_var[2]
        variance_var = traffic_var[3]

        if period_var > 0:
            a, b = self.Beta_shape(0.5, period_var)
            self.period = self.Beta_Binomial(a, b, n_period, size=no_nodes) + 1  #array mean = 7.5
        else:
            self.period = np.repeat(n_period/2, no_nodes) + 1  #array of 7.5

        if deadline_var > 0:
            ar, br = self.Beta_shape(0.5, deadline_var)
            n_ratio = (np.random.beta(ar, br, size=no_nodes) + 0.5 ) * ratio
            self.deadline = self.period * n_ratio
        else:
            self.deadline = self.period * ratio

        #
        # if deadline_var > 0:
        #     a, b = self.Beta_shape(0.5, deadline_var)
        #     self.deadline = self.Beta_Binomial(a, b, n_deadline, size=no_nodes)
        # else:
        #     self.deadline = self.period * ratio

        if variance_var > 0:
            var_var = abs(np.random.normal(0, np.sqrt(variance_var), size=no_nodes))
        else:
            var_var = np.zeros(no_nodes)

        # print(self.period)
        # print(self.deadline)
        # input()

        self.pool = [Node(self.type, pilot_rq, self.period[i], self.deadline[i], var_var[i]) for i in range(self.no_nodes)]

    def get_means(self):
        period_mean = np.mean(self.period)
        deadline_mean = np.mean(self.deadline)

        return period_mean, deadline_mean

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
