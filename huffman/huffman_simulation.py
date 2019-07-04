import numpy as np

from events.event import Event
from simulation import Simulation

__author__ = "Jon Stålhammar, Christian Lejdström, Emma Fitzgerald"


class HuffmanSimulation(Simulation):
    """
    Simulation for a massive MIMO network in discrete time

    """

    def __init__(self, config, stats, huffman_alarm_arrivals, custom_control_arrivals=None, seed=None):
        super(HuffmanSimulation, self).__init__(config, stats, None, custom_control_arrivals, seed)

        """
        Initialize simulation object

        Parameters
        ----------
        config : dict
            Dictionary containing all configuration parameters
        stats : Stats
            Statistics object for keeping track for measurements
        """

        self.huffman_alarm_arrivals = huffman_alarm_arrivals
        self.event_heap.push(self._ALARM_ARRIVAL, self.time + self.frame_length, 0)

    def _handle_alarm_arrival(self, event):
        # Handle alarm arrival event

        # Loop through alarm nodes and check for events
        for n in self.huffman_alarm_arrivals:
            self._handle_seed()
            if np.random.rand() <= n.prob and n.consumed is False:
                self.stats.stats['no_alarm_arrivals'] += 1
                n.consumed = True
                self.send_queue.insert(0, Event(self._ALARM_ARRIVAL, event.time, n.node_id, self.max_attempts))

        self.event_heap.push(self._ALARM_ARRIVAL, self.time + self.frame_length, 0)

    def _assign_pilots(self):
        # Assign pilots to all alarm and control nodes. Note that the receiving base station
        # does not on before hand how many nodes want to send

        # Always use one pilot for alarm traffic
        used_alarm_pilots = [0]

        # If no missed alarm attempts, start with normal index
        base_pilots = {0: 0}

        # Check for any missed alarms
        for event in self.send_queue:
            if event.type == self._ALARM_ARRIVAL:
                for node in self.huffman_alarm_arrivals:
                    if event.node_id == node.node_id:
                        missed_alarm_attempts = event.max_attempts - event.attempts_left

                        # Tries to avoid that pilot 0 is occupied if one or more collisions
                        # it may happen when the number of alarm nodes are more than the number of pilots
                        # that the sequence will start over due to running out of pilots
                        # this chance increases since we are generating a random number in the pilot range
                        if missed_alarm_attempts not in base_pilots.keys():
                            self._handle_seed()
                            base_pilots[missed_alarm_attempts] = max(base_pilots.values()) + 5

                        # This should only be able to occur when there are more alarm nodes than pilots
                        if missed_alarm_attempts >= len(node.seq):
                            print('Complete Huffman sequence without success..., potential fail')

                        # Ensure simulation does not crash if the sequence runs out, this can happen if there are
                        # more alarm nodes than available pilots
                        seq_i = missed_alarm_attempts % len(node.seq)

                        # If selecting a pilot that's not available, loop around
                        # Only way to ensure success having less alarm nodes than pilots
                        pilot = (base_pilots[missed_alarm_attempts] + node.seq[seq_i]) % self.no_pilots

                        used_alarm_pilots.append(pilot)
                        event.pilot_id = pilot

        # Any unused pilots can be used by the control nodes, note that this is possible since an offline
        # strategy has been determined
        control_pilots = []

        for i in range(self.no_pilots):
            if i not in used_alarm_pilots:
                control_pilots.append(i)

        # Assign control pilots
        if len(control_pilots) > 0:
            # Assign pilots to the events/nodes in the send queue
            for i in range(self.no_control_nodes):
                for event in self.send_queue:
                    if i == event.node_id and event.type == self._CONTROL_ARRIVAL:
                        event.pilot_id = np.random.choice(control_pilots)
