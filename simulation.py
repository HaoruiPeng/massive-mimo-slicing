import sys
import numpy as np
from utilities.event_heap import EventHeap
from utilities.event_generator import EventGenerator
from slices.slice import Slice
from slices.node import Node

__author__ = "Jon Stålhammar, Christian Lejdström, Emma Fitzgerald"


class Simulation:
    """
    Simulation for a massive MIMO network in discrete time

    This class needs to be inherited to work properly, please see binary_simulation.py for implementation example

    Attributes
    ----------


    Methods
    -------
    run()
        Runs the simulation the full simulation length with specified parameters
    """

    _URLLC = 1
    _mMTC = 2

    _URLLC_ARRIVAL = 1
    _mMTC_ARRIVAL = 2
    _DEPARTURE = 3
    _MEASURE = 4

    def __init__(self, config, stats, seed=None):
        """
        Initialize simulation object

        Parameters
        ----------
        config : dict
            Dictionary containing all configuration parameters
        stats : Stats
            Statistics object for keeping track for measurements
        """

        # TODO: Initialize slice objects and generate events in the nodes that subscribe to each slice
        # TODO: Complete event genertation in simulation first then in the nodes

        self.stats = stats
        self.time = 0.0

        # self.seed_counter = self.base_seed
        # self.use_seed = config.get('use_seed')
#        self.base_alarm_pilot_share = config.get('base_alarm_pilot_share')

        self.no_pilots = config.get('no_pilots')
        self.simulation_length = config.get('simulation_length') * 1000
        self.frame_length = config.get('frame_length')
        self.measurement_period = config.get('measurement_period')
        # number of control nodes
        self.control_node_buffer = config.get('control_nodes_buffer')
        self.event_heap = EventHeap()
        self.send_queue = []

        # The simulation slices parameters can be passed from the main fuction
        self.Slices = [Slice(self._URLLC), Slice(self._mMTC)]
        for s in self.Slices:
            self.__initialize_nodes(s)

        # If custom alarm arrivals specified, initialize these
        # TODO: Specify the event generator for every customer
        # if self.custom_alarm_arrivals is not None:
        #     self.alarm_arrivals = []
        #
        #     for i in range(self.no_alarm_nodes):
        #         d = self.custom_alarm_arrivals[i].get('distribution')
        #         d_settings = self.custom_alarm_arrivals[i].get('settings')
        #         self.alarm_arrivals.append(EventGenerator(d, d_settings))
        # else:
        #     # Set default alarm arrival distribution
        #     self.alarm_arrival_distribution = config.get('default_alarm_arrival_distribution')
        #     alarm_arrival_parameters = config.get('alarm_arrival_distributions').get(
        #         self.alarm_arrival_distribution)
        #     #generate the events from the specified distribution
        #     #Check Event generator
        #     self.alarm_arrivals = EventGenerator(self.alarm_arrival_distribution, alarm_arrival_parameters)
        #
        # # If custom control arrivals specified, initialize these
        # #arrivals -> list of event generators for each customer
        # if self.custom_control_arrivals is not None:
        #     self.control_arrivals = []
        #
        #     for i in range(self.no_control_nodes):
        #         d = self.custom_control_arrivals[i].get('distribution')
        #         d_settings = self.custom_control_arrivals[i].get('settings')
        #         self.control_arrivals.append(EventGenerator(d, d_settings))
        # else:
        #     # Set default control arrival distribution
        #     self.control_arrival_distribution = config.get('default_control_arrival_distribution')
        #     control_arrival_parameters = config.get('control_arrival_distributions').get(
        #         self.control_arrival_distribution)
        #     self.control_arrivals = EventGenerator(self.control_arrival_distribution, control_arrival_parameters)

        # Initialize nodes and their arrival times
        self.event_heap.push(self._DEPARTURE, self.time + self.frame_length, None, 0)
        self.event_heap.push(self._MEASURE, self.time + self.measurement_period, None, 0)

    def __initialize_nodes(self, _slice):
        # Initialize event times for all control nodes
        nodes = _slice.pool
        for _node in nodes:
            next_arrival = _node.event_generator.get_next()
            self.event_heap.push(_slice.type, self.time + next_arrival, self.time + _node.deadline, nodes.index(_node))

    def __handle_event(self, event):
        # Event switcher to determine correct action for an event
        event_actions = {
            self._URLLC_ARRIVAL: self._handle_urllc_arrival,
            self._mMTC_ARRIVAL: self.__handle_mmtc_arrival,
            self._DEPARTURE: self.__handle_departure,
            self._MEASURE: self.__handle_measurement}

        event_actions[event.type](event)

    def _handle_urllc_arrival(self, event):
        # Handle an alarm arrival event
        self.stats.stats['no_alarm_arrivals'] += 1
        # Store event in send queue until departure (as LIFO)
        self.send_queue.insert(0, event)
        # Add a new alarm arrival event to the event list
        node = self.Slices[self._URLLC-1].pool[event.node_id]
        next_arrival = node.event_generator.get_next()

        self.event_heap.push(self._URLLC_ARRIVAL, self.time + next_arrival, self.time + node.deadline, event.node_id)

    def __handle_mmtc_arrival(self, event):
        # Handle a control arrival event

        self.stats.stats['no_control_arrivals'] += 1
        # Store event in send queue until departure (as LIFO)
        self.send_queue.insert(0, event)
        # Add new control arrival event to the event list

        node = self.Slices[Simulation._mMTC-1].pool[event.node_id]
        next_arrival = node.event_generator.get_next()

        self.event_heap.push(self._mMTC_ARRIVAL, self.time + next_arrival, self.time + node.deadline, event.node_id)

    def __handle_departure(self, event):
        # Handle a departure event

        del event
        self.__handle_expired_events()
        self._assign_pilots()
        # self.__check_collisions()
        # Add new departure event to the event list
        self.event_heap.push(self._DEPARTURE, self.time + self.frame_length, None, 0)

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
        self.event_heap.push(self._MEASURE, self.time + self.measurement_period, None, 0)

    def __handle_expired_events(self):
        # remove the expired events in the send_queue

        send_queue_length = len(self.send_queue)
        remove_indices = []

        for i in range(send_queue_length):
            event = self.send_queue[i]
            if event.dead_time < self.time:
                remove_indices.append(i)
                # TODO: add number of missed events in the stats

            # Check for events with missed deadlines
            # if event.attempts_left == 0:
            #     # Alarm events need to be handled regardless if the event has expired, i.e. do not
            #     # remove the event from the send queue
            #     if event.type == self._ALARM_ARRIVAL:
            #         self.stats.stats['no_missed_alarms'] += 1
            #     else:
            #         self.stats.stats['no_missed_controls'] += 1
            #         if i not in remove_indices:
            #             remove_indices.append(i)
            #
            #     continue
            #
            # # If last event in send queue, no more other events to compare with
            # if i == send_queue_length - 1:
            #     continue
            #
            # # Disregard control events if the buffer is full, logic is that too old control signals are not relevant
            # # Alarm signals should always be handled and never removed from the send queue
            # event_matches = 0
            # for j in range(i + 1, send_queue_length):
            #     cmp_event = self.send_queue[j]
            #
            #     if event.type == self._CONTROL_ARRIVAL and event.node_id == cmp_event.node_id:
            #         event_matches += 1
            #
            #         if event_matches > self.control_node_buffer and j not in remove_indices:
            #             self.stats.stats['no_missed_controls'] += 1
            #             remove_indices.append(j)

        # Remove the events in reversed order to not shift subsequent indices
        for i in sorted(remove_indices, reverse=True):
            del self.send_queue[i]

    # def __check_collisions(self):
    #     # Check for pilot contamination, i.e. more than one node assigned the same pilot
    #     send_queue_length = len(self.send_queue)
    #     # pilot_collisions = []
    #     remove_indices = []
    #
    #     # Check for contaminated pilots
    #     for i in range(send_queue_length - 1):
    #         event = self.send_queue[i]
    #
    #         for j in range(i + 1, send_queue_length):
    #             cmp_event = self.send_queue[j]
    #
    #             if event.pilot_id == cmp_event.pilot_id and not event.node_id == cmp_event.node_id:
    #                 if event.pilot_id not in pilot_collisions:
    #                     pilot_collisions.append(event.pilot_id)
    #
    #     self.stats.stats['no_collisions'] += len(pilot_collisions)
    #
    #     handled_nodes = []
    #
    #     # Handle events with contaminated pilots, start with the first events in time (e.g. last in list)
    #     for i in reversed(range(send_queue_length)):
    #         event = self.send_queue[i]
    #
    #         if event.pilot_id in pilot_collisions:
    #             event.attempts_left -= 1
    #         elif i not in handled_nodes:
    #             handled_nodes.append(i)
    #             remove_indices.append(i)
    #
    #         # Reset pilot id to handle case where no pilots where assigned
    #         event.pilot_id = -1
    #
    #     # Remove the events in reversed order to not shift subsequent indices
    #     for i in sorted(remove_indices, reverse=True):
    #         self.stats.stats['no_departures'] += 1
    #         del self.send_queue[i]

    def _assign_pilots(self):
        # Assign pilots to all alarm and control nodes. Note that the receiving base station
        # does not on before hand how many nodes want to send
        no_pilots = self.no_pilots
        urllc_counter = 0
        urllc_events = []
        mmtc_events = []
        # Check for any missed alarms
        # missed_alarm_attempts = 0
        for event in self.send_queue:
            if event.type == self._URLLC_ARRIVAL:
                # missed_alarm_attempts = max(event.max_attempts - event.attempts_left, missed_alarm_attempts)
                urllc_counter += 1
                urllc_events.append(event)
            else:
                mmtc_events.append(event)
        # Limit the number of missed attempts, will cause overflow otherwise
        # missed_alarm_attempts = min(10, missed_alarm_attempts)

        # Exponential back-off is used to assign dedicated pilots to alarm packets, at most 100%
        # alarm_pilot_share = min(self.base_alarm_pilot_share * np.power(2, max(missed_alarm_attempts - 1, 0)), 1)

        # At least one alarm pilot if dedicated resources is used
        # alarm_pilots = max(int(alarm_pilot_share * self.no_pilots), 1)
        # control_pilots = self.no_pilots - alarm_pilots

        # Only used dedicated alarm pilots if a collision has occurred
        # Dedicated pilots is possible since all nodes in a collision know about the collision,
        # all other nodes can be informed by the base station since they have successfully received a pilot
        # if missed_alarm_attempts == 0:
        #     alarm_pilots = self.no_pilots
        #     control_pilots = self.no_pilots
        #     base_control_pilots = 0
        # else:
        #     # If missed alarm, use pilots AFTER alarm pilots for the control nodes
        #     base_control_pilots = alarm_pilots
        urllc_events.sort(key=lambda x: x.dead_time, reverse=True)
        for event in urllc_events:
            urllc_pilots = self.Slices[self._URLLC-1].pool[event.node_id].pilot_samples
            no_pilots -= urllc_pilots
            if no_pilots >= 0:
                # remove the event that assigned the pilots from the list
                self.send_queue.remove(event)
                del event
                continue
            else:
                break

        if no_pilots > 0:
            mmtc_events.sort(key=lambda x: x.dead_time, reverse=True)
            for event in mmtc_events:
                mmtc_pilots = self.Slices[self._mMTC-1].pool[event.node_id].pilot_samples
                no_pilots -= mmtc_pilots
                if no_pilots >= 0:
                    self.send_queue.remove(event)
                    del event
                    continue
                else:
                    break

    #     # Randomly assign pilots
    #     alarm_pilot_assignments = self.__generate_pilot_assignments(alarm_pilots, self.no_alarm_nodes)
    #
    #     # Assign alarm pilots to the events/nodes in the send queue
    #     for i in range(self.no_alarm_nodes):
    #         for event in self.send_queue:
    #             if i == event.node_id and event.type == self._ALARM_ARRIVAL:
    #                 event.pilot_id = alarm_pilot_assignments[i]
    #
    #     # Assign control pilots
    #     if control_pilots > 0:
    #         control_pilot_assignments = self.__generate_pilot_assignments(control_pilots, self.no_control_nodes,
    #                                                                       base=base_control_pilots)
    #
    #         # Assign pilots to the events/nodes in the send queue
    #         for i in range(self.no_control_nodes):
    #             for event in self.send_queue:
    #                 if i == event.node_id and event.type == self._CONTROL_ARRIVAL:
    #                     event.pilot_id = control_pilot_assignments[i]
    #
    # @staticmethod
    # def __generate_pilot_assignments(pilots, no_nodes, base=0):
    #     # Randomly assign pilots to the nodes, note that nodes cannot communicate with each other without pilots,
    #     # i.e. if node 1 uses pilot 1,
    #     # node 2 DOES NOT KNOW THIS and is equally likely (in base case) to select pilot 1
    #     # as well
    #
    #     pilot_assignments = []
    #
    #     while len(pilot_assignments) < no_nodes:
    #         pilot_assignments.append(base + np.random.randint(pilots))
    #
    #     return pilot_assignments

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
            if event.type == self._ALARM_ARRIVAL:
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

    def run(self):
        """ Runs the simulation """

        current_progress = 0

        while self.time < self.simulation_length:
            next_event = self.event_heap.pop()[3]

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
