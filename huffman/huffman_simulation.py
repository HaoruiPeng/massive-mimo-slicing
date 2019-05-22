import numpy as np

from utilities.event import Event
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

    def __handle_alarm_arrival(self, event):
        # Handle alarm arrival event

        # Loop through alarm nodes and check for events
        for n in self.huffman_alarm_arrivals:
            self._handle_seed()
            if n.prob < np.random.rand() and n.consumed is False:
                self.stats.stats['no_alarm_arrivals'] += 1
                n.consumed = True
                self.send_queue.insert(0, Event(self._ALARM_ARRIVAL, event.event_time, n.node_id, self.max_attempts))

    def __assign_pilots(self):
        # Assign pilots to all alarm and control nodes. Note that the receiving base station
        # does not on before hand how many nodes want to send

        used_alarm_pilots = []
        base_pilot = []

        # Check for any missed alarms
        for event in self.send_queue:
            if event.type == self._ALARM_ARRIVAL:
                for node in self.huffman_alarm_arrivals:
                    if event.node_id == node.node_id:
                        missed_alarm_attempts = event.max_attempts - event.attempts_left

                        # This should only be able to occur when there are more alarm nodes than pilots
                        if missed_alarm_attempts > len(node.seq):
                            print('Complete Huffman sequence without success..., potential fail')

                        # Ensure simulation does not crash if the sequence runs out, this can happen if there are
                        # more alarm nodes than available pilots
                        seq_i = missed_alarm_attempts % len(node.seq)
                        pilot = node.seq[seq_i]

                        # Adjust the sequence number so that IF a new event arrives in a frame where there have already
                        # been collisions there is no new collisions, i.e. allocate one more pilot than Huffman tells us
                        # to
                        pilot += base_pilot[seq_i]

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
