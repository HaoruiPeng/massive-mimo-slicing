"""
Define customers subscribe to the underlying slices
"""

__author__ = "Haorui Peng"

class Node:

    """
    Define individual Node subscribe to slices
    Each one have specific traffic profile requirements

    Common traffic profile
    ----------------------
    packet size
    data rate
    arrival distribution
    pilot_samples



    URLLC specific
    --------------
    LOW_RELIABILITY: 1 pilot samples
    HIGH_RELIABILITY: 3 pilot samples
    SHORT_DEADLINE: 3ms
    LONG_DEALINE: 10ms
    """

    LOW_RELIABILITY = 1
    HIGH_RELIABILITY = 2
    SHORT_DEADLINE = 1
    LONG_DEADLINE = 10

    _URLLC = 1
    _mMTC = 2

    def __init__(self, slice_id):
        self.slice = slice_id
        self.packet_size = None
        self.arrival = None
        self.deadline = None
        self.pilot_samples = 1
        self.setup()

    def setup(self):
        if self.slice == Node._URLLC:
            self.packet_size = 4
            self.data_rate = 10
            self.arrival = None  #TODO: Define arrival distribution here
            self.deadline = Node.LONG_DEADLINE
            self.pilot_samples = Node.LOW_RELIABILITY
        elif self.slice == Node._mMTC:
            self.packet_size = 4
            self.data_rate = 10
            self.arrival = None  # TODO: Define arrival distribution here
            self.deadline = 100
            self.pilot_samples = Node.LOW_RELIABILITY

