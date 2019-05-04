import time

import numpy as np

from event_list import EventList
from event_generator import EventGenerator


class Simulation:
    ALARM_ARRIVAL = 1
    CONTROL_ARRIVAL = 2
    DEPARTURE = 3
    MEASURE = 4

    def __init__(self, config, logger, stats):
        # Declare all variables
        self.stats = stats
        self.max_attempts = config.get('max_attempts')
        self.time = 0
        self.event_list = EventList(self.max_attempts)
        self.base_alarm_pilot_share = config.get('base_alarm_pilot_share')
        self.logger = logger
        self.no_alarm_nodes = config.get('no_alarm_nodes')
        self.no_control_nodes = config.get('no_control_nodes')
        self.control_node_buffer = config.get('control_node_buffer')
        self.simulation_length = config.get('simulation_length')
        self.no_pilots = config.get('no_pilots')
        self.frame_length = config.get('frame_length')
        self.measurement_period = config.get('measurement_period')
        self.send_queue = []

        # Set alarm arrival distribution function
        alarm_arrival_distribution = config.get('active_alarm_arrival_distribution')
        alarm_arrival_parameters = config.get('alarm_arrival_distributions').get(alarm_arrival_distribution)
        self.alarm_arrival = EventGenerator(alarm_arrival_distribution, alarm_arrival_parameters)

        # Set control arrival distribution function
        control_arrival_distribution = config.get('active_control_arrival_distribution')
        control_arrival_parameters = config.get('control_arrival_distributions').get(alarm_arrival_distribution)
        self.control_arrival = EventGenerator(control_arrival_distribution, control_arrival_parameters)

        # Initialize start nodes and their arrival times
        self.initialize_nodes()
        self.event_list.insert(self.DEPARTURE, self.time + self.frame_length, 0)
        self.event_list.insert(self.MEASURE, self.time + self.measurement_period, 0)

    # Initialize event times for all nodes
    def initialize_nodes(self):
        for i in range(self.no_alarm_nodes):
            self.event_list.insert(self.ALARM_ARRIVAL, self.time + self.alarm_arrival.get_next(), i)

        for i in range(self.no_control_nodes):
            self.event_list.insert(self.CONTROL_ARRIVAL, self.time + self.control_arrival.get_next(), i)

    # Event switcher
    def handle_event(self, event):
        event_actions = {
            self.ALARM_ARRIVAL: self.handle_alarm_arrival,
            self.CONTROL_ARRIVAL: self.handle_control_arrival,
            self.DEPARTURE: self.handle_departure,
            self.MEASURE: self.handle_measurement
        }

        event_actions[event.type](event)

    # Handle alarm arrival
    def handle_alarm_arrival(self, event):
        self.stats.no_alarm_arrivals += 1
        # Store event until a departure
        self.send_queue.insert(0, event)
        # Add new arrival event
        self.event_list.insert(self.ALARM_ARRIVAL, self.time + self.alarm_arrival.get_next(), event.node_id)

    # Handle control arrival
    def handle_control_arrival(self, event):
        self.stats.no_control_arrivals += 1
        # Store event until a departure
        self.send_queue.insert(0, event)
        # Add new arrival event
        self.event_list.insert(self.CONTROL_ARRIVAL, self.time + self.control_arrival.get_next(), event.node_id)

    # Handle departure event
    def handle_departure(self, event):
        del event
        self.remove_expired_events()
        self.assign_pilots()
        self.check_collisions()
        # Add new depart event
        self.event_list.insert(self.DEPARTURE, self.time + self.frame_length, 0)

    # Check for pilot contamination
    def check_collisions(self):
        send_queue_length = len(self.send_queue)
        remove_indices = []

        for i in range(send_queue_length - 2):
            event = self.send_queue[i]
            collision = False

            for j in range(i + 1, send_queue_length - 1):
                cmp_event = self.send_queue[j]

                if event.pilot_id == cmp_event.pilot_id:
                    collision = True
                    event.attempts_left -= 1
                    cmp_event.attempts_left -= 1
                    self.stats.no_collisions += 1

            if not collision:
                self.stats.no_departures += 1
                remove_indices.append(i)

        # Actually remove the events from the event queue
        for i in sorted(remove_indices, reverse=True):
            del self.send_queue[i]

    # NOTE: the receiving base station does not know how many nodes want to send
    def assign_pilots(self):
        # If more pilots than total nodes, handle all events
        if self.no_pilots >= self.no_control_nodes + self.no_alarm_nodes:
            self.stats.no_departures += len(self.send_queue)
            self.send_queue = []
        else:
            # Check for missed alarm deadlines
            missed_alarm_attempts = 0

            for event in self.send_queue:
                attempts_diff = self.max_attempts - event.attempts_left
                if event.type == self.ALARM_ARRIVAL and attempts_diff > missed_alarm_attempts:
                    missed_alarm_attempts = attempts_diff

            # Exponential share assignment if missed alarm
            alarm_pilot_share = max(self.base_alarm_pilot_share * np.power(2, missed_alarm_attempts), 1)
            alarm_pilots = int(alarm_pilot_share * self.no_pilots)
            control_pilots = self.no_pilots - alarm_pilots

            # Assign alarm pilots
            for i in range(self.no_alarm_nodes):
                # Check if exclusive alarm pilots should be used
                if missed_alarm_attempts > 0:
                    pilot_id = i % alarm_pilots
                else:
                    pilot_id = i % self.no_pilots

                # Assign pilot to correct event in queue
                for event in self.send_queue:
                    if i == event.node_id and event.type == self.ALARM_ARRIVAL:
                        event.pilot_id = pilot_id

            # Assign control pilots
            for i in range(self.no_control_nodes):
                # Check if exclusive alarm pilots should be used
                if missed_alarm_attempts > 0:
                    pilot_id = alarm_pilots + i % control_pilots
                else:
                    pilot_id = i % self.no_pilots

                # Assign pilots to correct event in queue
                for event in self.send_queue:
                    if i == event.node_id and event.type == self.CONTROL_ARRIVAL:
                        event.pilot_id = pilot_id

    def remove_expired_events(self):
        send_queue_length = len(self.send_queue)
        remove_indices = []

        for i in range(send_queue_length - 1):
            event = self.send_queue[i]

            # Remove events with passed deadlines
            if event.attempts_left == 0:
                if event.type == self.ALARM_ARRIVAL:
                    self.stats.missed_alarms += 1
                    # Expired alarm events still need to be handled, do not remove from queue
                else:
                    self.stats.missed_controls += 1
                    # Only remove control events
                    remove_indices.append(i)

                continue

            if i == len(self.send_queue) - 1:
                continue

            # Remove events with a new version (assuming old control signals should be discarded)
            for j in range(i + 1, send_queue_length - 1):
                cmp_event = self.send_queue[j]

                if event.node_id == cmp_event.node_id:
                    if event.type == self.ALARM_ARRIVAL:
                        self.stats.missed_alarms += 1
                    else:
                        self.stats.missed_controls += 1

                    remove_indices.append(j)

        # Actually remove the events from the event queue
        for i in sorted(remove_indices, reverse=True):
            del self.send_queue[i]

    def handle_measurement(self, event):
        del event
        self.stats.no_measurements += 1
        self.logger.write(str(self.stats.alarm_in_queue) + ',' + str(self.stats.control_in_queue))
        # Add new measure event
        self.event_list.insert(self.MEASURE, self.time + self.measurement_period, 0)

    def start(self):
        while self.time < self.simulation_length:
            next_event = self.event_list.fetch()

            # Advance time before handling event
            self.time = next_event.time
            self.handle_event(next_event)
