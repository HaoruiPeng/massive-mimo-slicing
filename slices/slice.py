"""
Define slice types for customer groups: URLLC and mMTC
Define customers subscribe to the underlying slices
"""

__author__ = "Haorui Peng"

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

    def __init__(self, type):
        self.type = type
        self.max_customer = None
