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

    _URLLC = 1
    _mMTC = 2

    # the nodes generator the event periodically
    def __init__(self, slice_id):
        with open('slices/node_config.json') as config_file:
            config = json.load(config_file)
        self.slice = slice_id

        if slice_id == self._URLLC:
            self.slice_name = "urllc"
        elif slice_id == self._mMTC:
            self.slice_name = "mmtc"

        self.data_rate = 10
        self.arrival = config.get(self.slice_name).get(
            'distribution')
        deadline_profile = config.get(self.slice_name).get(
            'deadline')
        reliability_profile = config.get(self.slice_name).get(
            'reliability')
        self.deadline = config.get('deadline_par').get(
            deadline_profile)
        self.pilot_samples = config.get('reliability_par').get(
            reliability_profile)
        self.arrival_parameter = config.get('arrival_distributions_par').get(
            self.slice_name).get(
            self.arrival)
        self.event_generator = EventGenerator(self.arrival, self.arrival_parameter)




