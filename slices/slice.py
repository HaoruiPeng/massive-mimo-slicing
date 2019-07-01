"""
Define slice types for customer groups: URLLC and mMTC
"""

__author__ = "Haorui Peng"

import numpy as np
import slices.node as node
import json


class Slice:
    """
    Slice class, two types

    Attributes
    ----------
    type: URLLC or mMTC
    traffic requirement: high reliability, low reliability, short deadline, long deadline

    """

    _URLLC = 1
    _mMTC = 2

    def __init__(self, slice_type):
        with open('slice_config.json') as config_file:
            config = json.load(config_file)

        self.type = slice_type
        if self.type == Slice._URLLC:
            self.no_nodes = config.get("no_urllc_nodes")
        elif self.type == Slice.mMTC:
            self.no_nodes = config.get("no_mmtc_nodes")
        self.pool = [node(self.type) for i in range(self.no_nodes)]

