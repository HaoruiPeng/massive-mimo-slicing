import sys
import time

import numpy as np

from event_heap import EventHeap
from event_generator import EventGenerator
from event import Event
from huffman.huffman_tree import HuffmanTree

__author__ = "Jon Stålhammar, Christian Lejdström, Emma Fitzgerald"


class Simulation:
    """
    Simulation for a massive MIMO network in discrete time

    Attributes
    ----------
    __ALARM_ARRIVAL : int
        Type id for an alarm arrival event
    __CONTROL_ARRIVAL : int
        Type id for a control arrival event
    __DEPARTURE : int
        Type id for a departure event
    __MEASURE : int
        Type id for a measure event
    stats : Stats
        Statistics object for keeping track for measurements
    time : int
        Current simulation time (default 0)
    max_attempts : int
        Maximum number of attempts or frames before a packet misses its deadline
    base_alarm_pilot_share : float
        Start share of dedicated pilots for alarm packets after pilot contamination involving an alarm packet
    no_alarm_nodes : int
        Number of alarm nodes in simulation
    no_control_nodes : int
        Number of control nodes in simulation
    no_pilots : int
        Number of available pilots
    simulation_length : int
        Simulation length in (in ms)
    frame_length : int
        Frame length (in ms), determining the frequency of departure events
    measurement_period : int
        Time in ms of how often measurements of the system should be taken
    control_node_buffer : int
        Number of control events allowed in send queue for a certain node
    event_heap : EventHeap
        Binary heap of all signalling events (arrivals, departures and measurements)
    send_queue : list of __Event
        List of all events that need to be processed
    alarm_arrivals : list
        (List of) object for generating alarm event times with a specific distribution
    control_arrivals : list
        (List of) object for generating control event times with a specific distribution
    custom_alarm_arrivals : list
        Optional list for per node specific arrival distribution and deadline
    custom_control_arrivals : list
        Optional list for per node specific arrival distribution and deadline

    Methods
    -------
    run()
        Runs the simulation the full simulation length with specified parameters
    """

    __ALARM_ARRIVAL = 1
    __CONTROL_ARRIVAL = 2
    __DEPARTURE = 3
    __MEASURE = 4

    def __init__(self, config, stats, custom_control_arrivals=None, seed=None):
        """
        Initialize simulation object

        Parameters
        ----------
        config : dict
            Dictionary containing all configuration parameters
        stats : Stats
            Statistics object for keeping track for measurements
        """

        self.stats = stats
        self.time = 0.0

        if seed is None:
            self.base_seed = int(time.time())
        else:
            self.base_seed = seed

        self.seed_counter = self.base_seed
        self.custom_control_arrivals = custom_control_arrivals
        self.use_seed = config.get('use_seed')
        self.max_attempts = config.get('max_attempts')
        self.base_alarm_pilot_share = config.get('base_alarm_pilot_share')
        self.no_alarm_nodes = config.get('no_alarm_nodes')
        self.no_control_nodes = config.get('no_control_nodes')
        self.no_pilots = config.get('no_pilots')
        self.simulation_length = config.get('simulation_length') * 1000
        self.frame_length = config.get('frame_length')
        self.measurement_period = config.get('measurement_period')
        self.control_node_buffer = config.get('control_nodes_buffer')
        self.event_heap = EventHeap(self.max_attempts)
        self.send_queue = []

        # Generate random alarm probabilities
        self.__handle_seed()
        self.alarm_node_probabilities = np.random.rand(len(config.get('no_alarm_nodes')), 1) * 0.5

        # Generate pilot sequences based on huffman tree
        huffman_tree = HuffmanTree(self.alarm_node_probabilities)
        self.alarm_node_pilot_sequences = huffman_tree.pilot_sequences

        # If custom control arrivals specified, initialize these
        if self.custom_control_arrivals is not None:
            self.control_arrivals = []

            for i in range(self.no_control_nodes):
                d = self.custom_control_arrivals[i].get('distribution')
                d_settings = self.custom_control_arrivals[i].get('settings')
                self.control_arrivals.append(EventGenerator(d, d_settings, self.use_seed))
        else:
            # Set default control arrival distribution
            self.control_arrival_distribution = config.get('default_control_arrival_distribution')
            control_arrival_parameters = config.get('control_arrival_distributions').get(
                self.control_arrival_distribution)
            self.control_arrivals = EventGenerator(self.control_arrival_distribution, control_arrival_parameters,
                                                   self.use_seed)

        # Initialize nodes and their arrival times
        self.__initialize_arrival_nodes()
        self.event_heap.push(self.__ALARM_ARRIVAL, self.time + self.frame_length, 0)
        self.event_heap.push(self.__DEPARTURE, self.time + self.frame_length, 0)
        self.event_heap.push(self.__MEASURE, self.time + self.measurement_period, 0)

    def __initialize_arrival_nodes(self):
        # Initialize event times for all control nodes
        for i in range(self.no_control_nodes):
            max_attempts = None
            self.__handle_seed()

            # Extract custom arrival distribution
            if self.custom_control_arrivals is not None:
                max_attempts = self.custom_control_arrivals[i].get('max_attempts')
                next_arrival = self.control_arrivals[i].get_next()

                # Spread if distribution is constant
                if self.custom_control_arrivals[i].get('distribution') == 'constant':
                    self.__handle_seed()
                    next_arrival *= np.random.rand()
            else:
                next_arrival = self.control_arrivals.get_next()

                # Spread if distribution is constant
                if self.control_arrival_distribution == 'constant':
                    self.__handle_seed()
                    next_arrival *= np.random.rand()

            self.event_heap.push(self.__CONTROL_ARRIVAL, self.time + next_arrival, i, max_attempts)

    def __handle_event(self, event):
        # Event switcher to determine correct action for an event

        event_actions = {
            self.__ALARM_ARRIVAL: self.__handle_alarm_arrival,
            self.__CONTROL_ARRIVAL: self.__handle_control_arrival,
            self.__DEPARTURE: self.__handle_departure,
            self.__MEASURE: self.__handle_measurement}

        event_actions[event.type](event)

    def __handle_alarm_arrival(self, event):
        # Handle alarm arrival event

        for i in range(self.alarm_node_probabilities):
            if self.alarm_node_probabilities[i] < np.random.rand():
                self.send_queue.insert(0, Event(self.__ALARM_ARRIVAL, event.event_time, i, self.max_attempts))

    def __handle_control_arrival(self, event):
        # Handle a control arrival event

        self.stats.stats['no_control_arrivals'] += 1
        # Store event in send queue until departure (as LIFO)
        self.send_queue.insert(0, event)
        # Add new control arrival event to the event list
        self.__handle_seed()

        max_attempts = None

        if self.custom_control_arrivals is not None:
            max_attempts = self.custom_control_arrivals[event.node_id].get('max_attempts')
            next_arrival = self.control_arrivals[event.node_id].get_next()
        else:
            next_arrival = self.control_arrivals.get_next()

        self.event_heap.push(self.__CONTROL_ARRIVAL, self.time + next_arrival, event.node_id, max_attempts)

    def __handle_departure(self, event):
        # Handle a departure event

        del event
        self.__handle_expired_events()
        self.__assign_pilots()
        self.__check_collisions()
        # Add new departure event to the event list
        self.event_heap.push(self.__DEPARTURE, self.time + self.frame_length, 0)

    def __check_collisions(self):
        # Check for pilot contamination, i.e. more than one node assigned the same pilot
        send_queue_length = len(self.send_queue)
        pilot_collisions = []
        remove_indices = []

        # Check for contaminated pilots
        for i in range(send_queue_length - 1):
            event = self.send_queue[i]

            for j in range(i + 1, send_queue_length):
                cmp_event = self.send_queue[j]

                if event.pilot_id == cmp_event.pilot_id and not event.node_id == cmp_event.node_id:
                    if event.pilot_id not in pilot_collisions:
                        pilot_collisions.append(event.pilot_id)

        self.stats.stats['no_collisions'] += len(pilot_collisions)

        handled_nodes = []

        # Handle events with contaminated pilots, start with the first events in time (e.g. last in list)
        for i in reversed(range(send_queue_length)):
            event = self.send_queue[i]

            if event.pilot_id in pilot_collisions:
                event.attempts_left -= 1
            elif i not in handled_nodes:
                handled_nodes.append(i)
                remove_indices.append(i)

            # Reset pilot id to handle case where no pilots where assigned
            event.pilot_id = -1

        # Remove the events in reversed order to not shift subsequent indices
        for i in sorted(remove_indices, reverse=True):
            self.stats.stats['no_departures'] += 1
            del self.send_queue[i]

    def __assign_pilots(self):
        # Assign pilots to all alarm and control nodes. Note that the receiving base station
        # does not on before hand how many nodes want to send

        # Check for any missed alarms
        missed_alarm_attempts = 0
        for event in self.send_queue:
            if event.type == self.__ALARM_ARRIVAL:
                missed_alarm_attempts = max(self.max_attempts - event.attempts_left, missed_alarm_attempts)

        # Limit the number of missed attempts, will cause overflow otherwise
        missed_alarm_attempts = min(10, missed_alarm_attempts)

        # Exponential back-off is used to assign dedicated pilots to alarm packets, at most 100%
        alarm_pilot_share = min(self.base_alarm_pilot_share * np.power(2, max(missed_alarm_attempts - 1, 0)), 1)

        # At least one alarm pilot if dedicated resources is used
        alarm_pilots = max(int(alarm_pilot_share * self.no_pilots), 1)
        control_pilots = self.no_pilots - alarm_pilots

        # Only used dedicated alarm pilots if a collision has occurred
        # Dedicated pilots is possible since all nodes in a collision know about the collision,
        # all other nodes can be informed by the base station since they have successfully received a pilot
        if missed_alarm_attempts == 0:
            alarm_pilots = self.no_pilots
            control_pilots = self.no_pilots
            base_control_pilots = 0
        else:
            # If missed alarm, use pilots AFTER alarm pilots for the control nodes
            base_control_pilots = alarm_pilots

        # Randomly assign pilots
        alarm_pilot_assignments = self.__generate_pilot_assignments(alarm_pilots, self.no_alarm_nodes)

        # Assign alarm pilots to the events/nodes in the send queue
        for i in range(self.no_alarm_nodes):
            for event in self.send_queue:
                if i == event.node_id and event.type == self.__ALARM_ARRIVAL:
                    event.pilot_id = alarm_pilot_assignments[i]

        # Assign control pilots
        if control_pilots > 0:
            control_pilot_assignments = self.__generate_pilot_assignments(control_pilots, self.no_control_nodes,
                                                                          base=base_control_pilots)

            # Assign pilots to the events/nodes in the send queue
            for i in range(self.no_control_nodes):
                for event in self.send_queue:
                    if i == event.node_id and event.type == self.__CONTROL_ARRIVAL:
                        event.pilot_id = control_pilot_assignments[i]

    @staticmethod
    def __generate_pilot_assignments(pilots, no_nodes, base=0):
        # Randomly assign pilots to the nodes, note that nodes cannot communicate with each other without pilots,
        # i.e. if node 1 uses pilot 1, node 2 DOES NOT KNOW THIS and is equally likely (in base case) to select pilot 1
        # as well

        pilot_assignments = []

        while len(pilot_assignments) < no_nodes:
            pilot_assignments.append(base + np.random.randint(pilots))

        return pilot_assignments

    def __handle_expired_events(self):
        # Handle expired alarm and control events

        send_queue_length = len(self.send_queue)
        remove_indices = []

        for i in range(send_queue_length):
            event = self.send_queue[i]

            # Check for events with missed deadlines
            if event.attempts_left == 0:
                # Alarm events need to be handled regardless if the event has expired, i.e. do not
                # remove the event from the send queue
                if event.type == self.__ALARM_ARRIVAL:
                    self.stats.stats['no_missed_alarms'] += 1
                else:
                    self.stats.stats['no_missed_controls'] += 1
                    if i not in remove_indices:
                        remove_indices.append(i)

                continue

            # If last event in send queue, no more other events to compare with
            if i == send_queue_length - 1:
                continue

            # Disregard control events if the buffer is full, logic is that too old control signals are not relevant
            # Alarm signals should always be handled and never removed from the send queue
            event_matches = 0
            for j in range(i + 1, send_queue_length):
                cmp_event = self.send_queue[j]

                if event.type == self.__CONTROL_ARRIVAL and event.node_id == cmp_event.node_id:
                    event_matches += 1

                    if event_matches > self.control_node_buffer and j not in remove_indices:
                        self.stats.stats['no_missed_controls'] += 1
                        remove_indices.append(j)

        # Remove the events in reversed order to not shift subsequent indices
        for i in sorted(remove_indices, reverse=True):
            del self.send_queue[i]

    def __get_send_queue_info(self):
        # Extract statistics from the send queue

        no_alarm_events = 0
        no_control_events = 0
        max_alarm_wait = 0
        max_control_wait = 0
        total_alarm_wait = 0
        total_control_wait = 0
        avg_alarm_wait = 0
        avg_control_wait = 0

        for event in self.send_queue:
            if event.type == self.__ALARM_ARRIVAL:
                no_alarm_events += 1

                wait = self.max_attempts - event.attempts_left
                max_alarm_wait = max(max_alarm_wait, wait)
                total_alarm_wait += wait
            else:
                no_control_events += 1

                wait = self.max_attempts - event.attempts_left
                max_control_wait = max(max_control_wait, wait)
                total_control_wait += wait

        if not no_alarm_events == 0:
            avg_alarm_wait = round(float(total_alarm_wait / no_alarm_events), 2)

        if not no_control_events == 0:
            avg_control_wait = round(float(total_control_wait / no_control_events), 2)

        return no_alarm_events, no_control_events, avg_alarm_wait, avg_control_wait, max_alarm_wait, max_control_wait

    def __handle_measurement(self, event):
        # Take measurement of the send queue

        del event
        self.stats.stats['no_measurements'] += 1

        measurements = self.__get_send_queue_info()
        log_string = ''

        for m in measurements:
            log_string += str(m) + ','

        log_string = log_string[:-1]
        log_string += '\n'
        self.stats.write_log(log_string)

        # Add a new measure event to the event list
        self.event_heap.push(self.__MEASURE, self.time + self.measurement_period, 0)

    def __handle_seed(self):
        # If use of seed is specified this will ensure the same seed pattern is used every simulations, but without
        # using the same random number every time a new event is generated in the heap
        # Since event signaling is used this is the only way to recreate results (alternative is to pre-calculate all
        # events which)

        if self.use_seed:
            np.random.seed(self.seed_counter)
            self.seed_counter += 1

    def run(self):
        """ Runs the simulation """

        current_progress = 0

        while self.time < self.simulation_length:
            next_event = self.event_heap.pop()[2]

            # Advance time before handling event
            self.time = next_event.time

            progress = round(100 * self.time / self.simulation_length)

            if progress > current_progress:
                current_progress = progress
                str1 = "\r Progress [{0}]".format('#' * (progress + 1) + ' ' * (100 - progress))
                sys.stdout.write(str1)
                sys.stdout.flush()

            self.__handle_event(next_event)

        print('\n Simulation complete. Results: \n')
