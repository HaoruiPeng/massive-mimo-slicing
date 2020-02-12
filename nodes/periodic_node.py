"""
Define customers subscribe to the underlying slices
"""

__author__ = "Haorui Peng"

from events.packet_generator import PacketGenerator
import json


class PeriodicNode:

    """
    Define individual Node subscribe to slices
    Each one have specific traffic profile requirements

    Common traffic profile
    ----------------------
    data rate
    variance
    """

    _PERIODIC = 0
    _FILE = 1
    _SPORADIC = 2

    # the nodes generator the event periodically
    def __init__(self, period, variance):

        self.node_type = self._PERIODIC
        self.request_queue = []
        self.arrival = "constant"
        self.pilot_samples =  1
        self.deadline = period * 2

        self.packet_generator = PacketGenerator(self.arrival, (period, variance))

    def get_type(self):
        return self.node_type

    def push_event(self, event):
        self.request_queue.append(event)

    def remove_event(self, event):
        self.request_queue.remove(event)
