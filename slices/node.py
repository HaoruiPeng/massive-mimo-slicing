"""
Define customers subscribe to the underlying slices
"""

__author__ = "Haorui Peng"

import utilities.event_generator as EventGenerator
import json

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

    #the nodes generator the event periodically
    def __init__(self, slice_id, config):
        with open('node_config.json') as config_file:
            config = json.load(config_file)
        self.slice = slice_id

        if self.slice == Node._URLLC:
            self.data_rate = 10
            self.arrival = config.get('urllc_arrival_distribution')
            self.deadline = Node.LONG_DEADLINE
            self.pilot_samples = Node.LOW_RELIABILITY
            self.arrival_parameter = config.get('urllc_arrival_distributions_par').get(self.arrival)
            self.event_generator = EventGenerator(self.arrival, self.arrival_parameter)

        elif self.slice == Node._mMTC:
            self.data_rate = 10
            self.arrival = config.get("mmtc_arrival_distribution")  # TODO: Define arrival distribution here
            self.deadline = 100
            self.pilot_samples = Node.LOW_RELIABILITY
            self.arrival_parameter = config.get('mmtc_arrival_distributions_par').get(self.arrival)
            self.event_generator = EventGenerator(self.arrival, self.arrival_parameter)



