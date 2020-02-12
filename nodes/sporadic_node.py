"""
Define customers subscribe to the underlying slices
"""

__author__ = "Haorui Peng"

from events.event_generator import EventGenerator
import json


class Node:

    """
    Define individual Node subscribe to slices
    Each one have specific traffic profile requirements

    Common traffic profile
    ----------------------
    data rate
    arrival distribution
    pilot_samples
    deadline
    """

    # the nodes generator the event periodically
    def __init__(self, period, deadline):

        self.slice = slice_id
        self.request_queue = []

        if slice_id == self._URLLC:
            self.slice_name = "urllc"
        elif slice_id == self._mMTC:
            self.slice_name = "mmtc"

        self.arrival = "constant"

        self.period = period
        self.var_variance = var_variance

        self.deadline = deadline

        self.pilot_samples =  pilots

        self.event_generator = EventGenerator(self.arrival, (self.period, self.var_variance))
        self.active = False
        self.assigned = False

    def push_event(self, event):
        self.request_queue.append(event)

    def remove_event(self, event):
        self.request_queue.remove(event)
