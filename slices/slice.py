"""
Define slice types for customer groups: URLLC and mMTC
"""

__author__ = "Haorui Peng"

from nodes.node import Node
import json


class Slice:
    """
    Slice class, two types

    Attributes
    ----------
    type: URLLC or mMTC
    traffic requirement: high reliability, low reliability, short deadline, long deadline

    """

    _URLLC = 0
    _mMTC = 1

    def __init__(self, slice_type, no_nodes, strategy, traffic=None):
        self.type = slice_type
        self.no_nodes = no_nodes
        self.strategy = strategy
        self.pool = [Node(self.type, traffic) for i in range(self.no_nodes)]

    def get_node(self, node_id):
        return self.pool[node_id]

    def get_index(self, node):
        return self.pool.index(node)


