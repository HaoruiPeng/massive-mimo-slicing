"""
Define customers subscribe to the underlying slices
"""

__author__ = "Haorui Peng"

from events.packet_generator import PacketGenerator
from events.mode_switch import ModeSwitch
import json


class FileNode:

    """
    Define individual Node subscribe to slices
    Each one have specific traffic profile requirements

    Common traffic profile
    ----------------------
    d_on: minimum interval for on states
    d_off: minimum interval for off states
    period_inner: the inter-ariival for the requests
    variance_inner: the variance on the inner period for each arrival
    """
    _OFF = 0
    _ON = 1

    _PERIODIC = 0
    _FILE = 1
    _SPORADIC = 2

    # the nodes generator the event periodically
    def __init__(self, period_inner, variance_inner, d_on, d_off):

        self.request_queue = []
        self.node_type = self._FILE
        self.arrival = "exponential"
        self.deadline = period_inner * 2

        self.mode = self._OFF
        self.pilot_samples =  1

        self.packet_generator = PacketGenerator(self.arrival, (period_inner, variance_inner))
        self.mode_switch = ModeSwitch(self.mode, d_on, d_off)

    def get_type(self):
        return self.node_type

    def push_event(self, event):
        self.request_queue.append(event)

    def remove_event(self, event):
        self.request_queue.remove(event)
