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

    _URLLC = 0
    _mMTC = 1

    # the nodes generator the event periodically
    def __init__(self, slice_id):
        with open('nodes/node_config.json') as config_file:
            config = json.load(config_file)
        self.slice = slice_id

        if slice_id == self._URLLC:
            self.slice_name = "urllc"
        elif slice_id == self._mMTC:
            self.slice_name = "mmtc"

        self.data_rate = 10
        self.arrival = config.get(self.slice_name).get(
            'distribution')
        self.deadline_profile = config.get(self.slice_name).get(
            'deadline')
        self.reliability_profile = config.get(self.slice_name).get(
            'reliability')
        self.deadline = config.get('deadline_par').get(
            self.deadline_profile)
        self.pilot_samples = config.get('reliability_par').get(
            self.reliability_profile)
        self.arrival_parameter = config.get('arrival_distributions_par').get(
            self.slice_name).get(
            self.arrival)
        if len(self.arrival_parameter) == 0:
            self.arrival_parameter = self.deadline

        self.event_generator = EventGenerator(self.arrival, self.arrival_parameter)
        self.active = False
        self.assigned = False

