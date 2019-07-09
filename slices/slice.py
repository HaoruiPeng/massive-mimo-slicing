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

    def __init__(self, slice_type):
        with open('slices/slice_config.json') as config_file:
            config = json.load(config_file)

        self.type = slice_type
        if self.type == self._URLLC:
            self.no_nodes = config.get("no_urllc_nodes")
        elif self.type == self._mMTC:
            self.no_nodes = config.get("no_mmtc_nodes")

        self.pool = [Node(self.type) for i in range(self.no_nodes)]

    def get_node(self, node_id):
        return self.pool[node_id]


