"""
Define slice types for customer groups: URLLC and mMTC
"""

__author__ = "Haorui Peng"

import numpy as np
import slices.node as node


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
        self.type = slice_type
        self.pool = np.array(node(self.type))
