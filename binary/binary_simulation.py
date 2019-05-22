import numpy as np
from simulation import Simulation

__author__ = "Jon Stålhammar, Christian Lejdström, Emma Fitzgerald"


class BinarySimulation(Simulation):
    """
    Simulation for a massive MIMO network in discrete time
    """

    def __init__(self, config, stats, custom_alarm_arrivals=None, custom_control_arrivals=None, seed=None):
        """
        Initialize simulation object using binary exponential back-off for alarm collisions

        See super class for implementation details

        """

        super(BinarySimulation, self).__init__(config, stats, custom_alarm_arrivals, custom_control_arrivals, seed)
        self.__initialize_alarm_arrival_nodes()

    def __initialize_alarm_arrival_nodes(self):
        # Initialize event times for all alarm and control nodes

        for i in range(self.no_alarm_nodes):
            max_attempts = None
            self._handle_seed()

            # Extract custom arrival distribution
            if self.custom_alarm_arrivals is not None:
                max_attempts = self.custom_alarm_arrivals[i].get('max_attempts')
                next_arrival = self.alarm_arrivals[i].get_next()

                # Spread if distribution is constant
                if self.custom_alarm_arrivals[i].get('distribution') == 'constant':
                    self._handle_seed()
                    next_arrival *= np.random.rand()
            else:
                next_arrival = self.alarm_arrivals.get_next()

                # Spread if distribution is constant
                if self.alarm_arrival_distribution == 'constant':
                    self._handle_seed()
                    next_arrival *= np.random.rand()

            self.event_heap.push(self._ALARM_ARRIVAL, next_arrival, i, max_attempts)

    def __handle_alarm_arrival(self, event):
        # Handle an alarm arrival event
        self.stats.stats['no_alarm_arrivals'] += 1
        # Store event in send queue until departure (as LIFO)
        self.send_queue.insert(0, event)
        # Add a new alarm arrival event to the event list
        self._handle_seed()

        max_attempts = None

        if self.custom_alarm_arrivals is not None:
            max_attempts = self.custom_alarm_arrivals[event.node_id].get('max_attempts')
            next_arrival = self.alarm_arrivals[event.node_id].get_next()
        else:
            next_arrival = self.alarm_arrivals.get_next()

        self.event_heap.push(self._ALARM_ARRIVAL, self.time + next_arrival, event.node_id, max_attempts)

    def __assign_pilots(self):
        # Assign pilots to all alarm and control nodes. Note that the receiving base station
        # does not on before hand how many nodes want to send

        # Check for any missed alarms
        missed_alarm_attempts = 0
        for event in self.send_queue:
            if event.type == self._ALARM_ARRIVAL:
                missed_alarm_attempts = max(event.max_attempts - event.attempts_left, missed_alarm_attempts)

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
                if i == event.node_id and event.type == self._ALARM_ARRIVAL:
                    event.pilot_id = alarm_pilot_assignments[i]

        # Assign control pilots
        if control_pilots > 0:
            control_pilot_assignments = self.__generate_pilot_assignments(control_pilots, self.no_control_nodes,
                                                                          base=base_control_pilots)

            # Assign pilots to the events/nodes in the send queue
            for i in range(self.no_control_nodes):
                for event in self.send_queue:
                    if i == event.node_id and event.type == self._CONTROL_ARRIVAL:
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
