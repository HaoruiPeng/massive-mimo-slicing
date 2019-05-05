import numpy as np

from event_list import EventList
from event_generator import EventGenerator


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
    logger : Logger
        Logging object for writing measurements to file
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
    event_list : EventList
        List of all signalling events (arrivals, departures and measurements)
    send_queue : list of __Event
        List of all events that need to be processed
    alarm_arrival : EventGenerator
        Class for generating alarm event times with a specific distribution (determined from config file)
    control_arrival : EventGenerator
        Class for generating control event times with a specific distribution (determined from config file)

    Methods
    -------
    run()
        Runs the simulation the full simulation length with specified parameters
    """

    __ALARM_ARRIVAL = 1
    __CONTROL_ARRIVAL = 2
    __DEPARTURE = 3
    __MEASURE = 4

    def __init__(self, config, logger, stats):
        """
        Initialize simulation object

        Parameters
        ----------
        config : dict
            Dictionary containing all configuration parameters
        logger : Logger
            Logging object for writing measurements to file
        stats : Stats
            Statistics object for keeping track for measurements
        """

        self.logger = logger
        self.stats = stats
        self.time = 0

        self.max_attempts = config.get('max_attempts')
        self.base_alarm_pilot_share = config.get('base_alarm_pilot_share')
        self.no_alarm_nodes = config.get('no_alarm_nodes')
        self.no_control_nodes = config.get('no_control_nodes')
        self.no_pilots = config.get('no_pilots')
        self.simulation_length = config.get('simulation_length')
        self.frame_length = config.get('frame_length')
        self.measurement_period = config.get('measurement_period')
        self.control_node_buffer = config.get('control_nodes_buffer')

        self.event_list = EventList(self.max_attempts)
        self.send_queue = []

        # Set alarm arrival distribution function
        alarm_arrival_distribution = config.get('active_alarm_arrival_distribution')
        alarm_arrival_parameters = config.get('alarm_arrival_distributions').get(alarm_arrival_distribution)
        self.alarm_arrival = EventGenerator(alarm_arrival_distribution, alarm_arrival_parameters)

        # Set control arrival distribution function
        control_arrival_distribution = config.get('active_control_arrival_distribution')
        control_arrival_parameters = config.get('control_arrival_distributions').get(alarm_arrival_distribution)
        self.control_arrival = EventGenerator(control_arrival_distribution, control_arrival_parameters)

        # Initialize nodes and their arrival times
        self.__initialize_arrival_nodes()
        self.event_list.insert(self.__DEPARTURE, self.time + self.frame_length, 0)
        self.event_list.insert(self.__MEASURE, self.time + self.measurement_period, 0)

    def __initialize_arrival_nodes(self):
        # Initialize event times for all alarm and control nodes

        for i in range(self.no_alarm_nodes):
            self.event_list.insert(self.__ALARM_ARRIVAL, self.time + self.alarm_arrival.get_next(), i)

        for i in range(self.no_control_nodes):
            self.event_list.insert(self.__CONTROL_ARRIVAL, self.time + self.control_arrival.get_next(), i)

    def __handle_event(self, event):
        # Event switcher to determine correct action for an event

        event_actions = {
            self.__ALARM_ARRIVAL: self.__handle_alarm_arrival,
            self.__CONTROL_ARRIVAL: self.__handle_control_arrival,
            self.__DEPARTURE: self.__handle_departure,
            self.__MEASURE: self.__handle_measurement}

        event_actions[event.type](event)

    def __handle_alarm_arrival(self, event):
        # Handle an alarm arrival event

        self.stats.no_alarm_arrivals += 1
        # Store event in send queue until departure (as LIFO)
        self.send_queue.insert(0, event)
        # Add a new alarm arrival event to the event list
        self.event_list.insert(self.__ALARM_ARRIVAL, self.time + self.alarm_arrival.get_next(), event.node_id)

    def __handle_control_arrival(self, event):
        # Handle a control arrival event

        self.stats.no_control_arrivals += 1
        # Store event in send queue until departure (as LIFO)
        self.send_queue.insert(0, event)
        # Add new control arrival event to the event list
        self.event_list.insert(self.__CONTROL_ARRIVAL, self.time + self.control_arrival.get_next(), event.node_id)

    def __handle_departure(self, event):
        # Handle a departure event

        del event
        self.__handle_expired_events()
        self.__assign_pilots()
        self.__check_collisions()
        # Add new departure event to the event list
        self.event_list.insert(self.__DEPARTURE, self.time + self.frame_length, 0)

    def __check_collisions(self):
        # Check for pilot contamination, i.e. more than one node assigned the same pilot

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

            # Only remove events from send queue if no collision has occurred
            if not collision:
                self.stats.no_departures += 1
                remove_indices.append(i)

        # Remove the events in reversed order to not shift subsequent indices
        for i in sorted(remove_indices, reverse=True):
            del self.send_queue[i]

    def __assign_pilots(self):
        # Assign pilots to all alarm and control nodes. Note that the receiving base station
        # does not on before hand how many nodes want to send

        # If more pilots than total nodes -> handle all events
        if self.no_pilots >= self.no_control_nodes + self.no_alarm_nodes:
            self.stats.no_departures += len(self.send_queue)
            self.send_queue = []
        else:
            # Check for any missed alarms
            missed_alarm_attempts = 0
            for event in self.send_queue:
                if event.type == self.__ALARM_ARRIVAL:
                    missed_alarm_attempts = max(self.max_attempts - event.attempts_left, missed_alarm_attempts)

            # Exponential back-off is used to assign dedicated pilots to alarm packets, at most 100%
            alarm_pilot_share = max(self.base_alarm_pilot_share * np.power(2, missed_alarm_attempts), 1)
            alarm_pilots = int(alarm_pilot_share * self.no_pilots)
            control_pilots = self.no_pilots - alarm_pilots

            # Assign alarm pilots
            for i in range(self.no_alarm_nodes):
                # Only used dedicated alarm pilots if a collision has occurred
                if missed_alarm_attempts > 0:
                    pilot_id = i % alarm_pilots
                else:
                    pilot_id = i % self.no_pilots

                # Assign pilots to the events/nodes in the send queue
                for event in self.send_queue:
                    if i == event.node_id and event.type == self.__ALARM_ARRIVAL:
                        event.pilot_id = pilot_id

            # Assign control pilots
            for i in range(self.no_control_nodes):
                # Only used dedicated alarm pilots if a collision has occurred
                if missed_alarm_attempts > 0:
                    pilot_id = alarm_pilots + i % control_pilots
                else:
                    pilot_id = i % self.no_pilots

                # Assign pilots to the events/nodes in the send queue
                for event in self.send_queue:
                    if i == event.node_id and event.type == self.__CONTROL_ARRIVAL:
                        event.pilot_id = pilot_id

    def __handle_expired_events(self):
        # Handle expired alarm and control events

        send_queue_length = len(self.send_queue)
        remove_indices = []

        for i in range(send_queue_length - 1):
            event = self.send_queue[i]

            # Check for events with missed deadlines
            if event.attempts_left == 0:
                # Alarm events need to be handled regardless if the event has expired, i.e. do not
                # remove the event from the send queue
                if event.type == self.__ALARM_ARRIVAL:
                    self.stats.no_missed_alarms += 1
                else:
                    self.stats.no_missed_controls += 1
                    remove_indices.append(i)

                continue

            # If last event in send queue, no more other events to compare to
            if i == len(self.send_queue) - 1:
                continue

            # Disregard control events if the buffer is full, logic is that too old control signals are not relevant
            # Alarm signals should always be handled and never removed from the send queue
            event_matches = 0
            for j in range(i + 1, send_queue_length - 1):
                cmp_event = self.send_queue[j]

                if event.type == self.__CONTROL_ARRIVAL and event.node_id == cmp_event.node_id:
                    event_matches += 1

                    if event_matches > self.control_node_buffer and j not in remove_indices:
                        self.stats.no_missed_controls += 1
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

        avg_alarm_wait = float(total_alarm_wait / no_alarm_events)
        avg_control_wait = float(total_control_wait / no_control_events)

        return no_alarm_events, no_control_events, avg_alarm_wait, avg_control_wait, max_alarm_wait, max_control_wait

    def __handle_measurement(self, event):
        # Take measurement of the send queue

        del event
        self.stats.no_measurements += 1

        measurements = self.__get_send_queue_info()
        log_string = ''

        for m in measurements:
            log_string += str(m) + ','

        log_string = log_string[:-1]
        log_string += '\n'
        self.logger.write(log_string)

        # Add a new measure event to the event list
        self.event_list.insert(self.__MEASURE, self.time + self.measurement_period, 0)

    def run(self):
        """ Runs the simulation """

        while self.time < self.simulation_length:
            next_event = self.event_list.fetch()

            # Advance time before handling event
            self.time = next_event.time
            self.__handle_event(next_event)
