import sys
from events.event_heap import EventHeap
from slices.slice import Slice


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

    _URLLC = 0
    _mMTC = 1

    _DEPARTURE = 2
    _MEASURE = 1
    _URLLC_ARRIVAL = 3
    _mMTC_ARRIVAL = 4

    def __init__(self, config, stats, trace):
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
        self.trace = trace
        self.time = 0.0

        self.no_pilots = config.get('no_pilots')
        self.simulation_length = config.get('simulation_length')
        self.frame_length = config.get('frame_length')
        self.measurement_period = config.get('measurement_period')
        self.pilot_strategy = config.get('strategy')

        self.strategy_mapping = {
            'FCFS': self.__fist_come_first_served,
            'RR_Q': self.__round_robin_queue_info,
            'RR_NQ': self.__round_robin_no_queue_info
        }

        self.event_heap = EventHeap()
        self.send_queue = []
        # used only in method "RR_NQ"

        self.Slices = [Slice(self._URLLC), Slice(self._mMTC)]
        self.frame_counter = 0
        self.frame_loops = self.Slices[self._URLLC].get_node(0).deadline / self.frame_length

        for s in self.Slices:
            # Initialize nodes and their arrival times
            self.__initialize_nodes(s)

        # Initialize departure and measurement event
        self.event_heap.push(self._DEPARTURE, self.time + self.frame_length)
        self.event_heap.push(self._MEASURE, self.time + self.measurement_period)

    def __initialize_nodes(self, _slice):
        nodes = _slice.pool
        # counter = 0
        # print("[Time {}] Initial {} nodes.".format(self.time, len(nodes)))
        for _node in nodes:
            next_arrival = _node.event_generator.get_init()
            if _slice.type == self._URLLC:
                self.stats.stats['no_urllc_arrivals'] += 1
                counter = self.stats.stats['no_urllc_arrivals']
            else:
                self.stats.stats['no_mmtc_arrivals'] += 1
                counter = self.stats.stats['no_mmtc_arrivals']
            self.event_heap.push(_slice.type+2,
                                 self.time + next_arrival, self.time + next_arrival + _node.deadline,
                                 nodes.index(_node), counter)

    def __handle_event(self, event):
        # Event switcher to determine correct action for an event
        event_actions = {
            self._URLLC_ARRIVAL: self.__handle_urllc_arrival,
            self._mMTC_ARRIVAL: self.__handle_mmtc_arrival,
            self._DEPARTURE: self.__handle_departure,
            self._MEASURE: self.__handle_measurement}

        event_actions[event.type](event)

    def __handle_urllc_arrival(self, event):
        # Handle an alarm arrival event
        self.stats.stats['no_urllc_arrivals'] += 1
        # print("[Time {}] No. of urllc_arrivals: {}".format(self.time, self.stats.stats['no_urllc_arrivals']))
        # Store event in send queue until departure (as LIFO)
        self.send_queue.insert(0, event)
        # Add a new alarm arrival event to the event list
        node = self.Slices[self._URLLC].pool[event.node_id]
        node.active = True
        next_arrival = node.event_generator.get_next()

        self.event_heap.push(self._URLLC_ARRIVAL,
                             self.time + next_arrival, self.time + next_arrival + node.deadline,
                             event.node_id, self.stats.stats['no_urllc_arrivals'])

    def __handle_mmtc_arrival(self, event):
        # Handle a control arrival event
        self.stats.stats['no_mmtc_arrivals'] += 1
        # print("[Time {}] No. of mmtc_arrivals: {}".format(self.time, self.stats.stats['no_mmtc_arrivals']))
        # Store event in send queue until departure (as LIFO)
        self.send_queue.insert(0, event)
    # Add new control arrival event to the event list

        node = self.Slices[self._mMTC].get_node(event.node_id)
        node.active = True
        next_arrival = node.event_generator.get_next()
        self.event_heap.push(self._mMTC_ARRIVAL,
                             self.time + next_arrival, self.time + next_arrival + node.deadline,
                             event.node_id, self.stats.stats['no_mmtc_arrivals'])

    def __handle_departure(self, event):
        # Handle a departure event
        # print("[Time {}] Departure".format(self.time))
        # print("[Time {}] Send queue size {}" .format(self.time, len(self.send_queue)))
        del event
        self.__handle_expired_events()
        self.__assign_pilots()
        # self.__check_collisions()
        # Add new departure event to the event list
        self.event_heap.push(self._DEPARTURE, self.time + self.frame_length)

    def __handle_measurement(self, event):
        # Take measurement of the send queue

        del event
        self.stats.stats['no_measurements'] += 1

        # measurements = self.__get_send_queue_info()
        # print("[Time {}] No.URLLC: {} No.mMTC: {}".format(self.time, measurements[0], measurements[1]))
        # Add a new measure event to the event list
        self.event_heap.push(self._MEASURE, self.time + self.measurement_period)

    def __handle_expired_events(self):
        # remove the expired events in the send_queue

        send_queue_length = len(self.send_queue)
        remove_indices = []

        for i in range(send_queue_length):
            event = self.send_queue[i]
            if event.dead_time < self.time:
                remove_indices.append(i)

        # Remove the events in reversed order to not shift subsequent indices
        for i in sorted(remove_indices, reverse=True):
            event = self.send_queue[i]
            if event.type == self._URLLC_ARRIVAL:
                node = self.Slices[self._URLLC].get_node(event.node_id)
                node.active = False
                self.stats.stats['no_missed_urllc'] += 1
                entry = event.get_entry(self.time, False)
                self.trace.write_trace(entry)
            elif event.type == self._mMTC_ARRIVAL:
                node = self.Slices[self._mMTC].get_node(event.node_id)
                node.active = False
                self.stats.stats['no_missed_mmtc'] += 1
                entry = event.get_entry(self.time, False)
            # print(entry)
                self.trace.write_trace(entry)
            del self.send_queue[i]

        # if len(remove_indices) > 0:
        #       print("\n[Time {}] Lost {} URLLC packets, {} mMTC packets\n"
        #               .format(self.time, urllc_counter, mmtc_counter))

    def __assign_pilots(self):
        self.strategy_mapping[self.pilot_strategy]()

    def __handle_send_queue(self):
        # Extract statistics from the send queue
        no_urllc_events = 0
        no_mmtc_events = 0

        for event in self.send_queue:
            if event.type == self._URLLC_ARRIVAL:
                no_urllc_events += 1
            else:
                no_mmtc_events += 1

        return no_urllc_events, no_mmtc_events

    def run(self):
        """ Runs the simulation """

        current_progress = 0
        print("\n[Time {}] Simulation start.".format(self.time))
        # print("Size: {}".format(self.event_heap.get_size()))
        # for k in self.event_heap.get_heap():
        #     print(k)
        while self.time < self.simulation_length:
            # print("[Time {}] Event heap size {}".format(self.time, self.event_heap.size()))
            next_event = self.event_heap.pop()[3]
            # print("Handle event: {} generated at time {}".format(next_event.type, next_event.time))

            # Advance time before handling event
            self.time = next_event.time

            progress = round(100 * self.time / self.simulation_length)

            if progress > current_progress:
                current_progress = progress
                str1 = "\rProgress: {0}%".format(progress)
                sys.stdout.write(str1)
                sys.stdout.flush()

            self.__handle_event(next_event)

        print('\n[Time {}] Simulation complete. Results:'.format(self.time))

    def write_result(self):
        file = open("results/result.csv", 'a')
        file.write(str(self.Slices[0].no_nodes) + ','
                   + str(self.Slices[1].no_nodes) + ','
                   + str(self.trace.get_waiting_time()[0]) + ','
                   + str(self.trace.get_waiting_time()[1]) + ','
                   + str(self.trace.get_loss_rate()[0]) + ','
                   + str(self.trace.get_loss_rate()[1]) + '\n'
                   )
        file.close()

    def __fist_come_first_served(self):
        no_pilots = self.no_pilots
        urllc_counter = 0
        urllc_events = []
        mmtc_events = []

        for event in self.send_queue:
            if event.type == self._URLLC_ARRIVAL:
                # missed_alarm_attempts = max(event.max_attempts - event.attempts_left, missed_alarm_attempts)
                urllc_counter += 1
                urllc_events.append(event)
            else:
                mmtc_events.append(event)

        urllc_events.sort(key=lambda x: x.dead_time, reverse=True)
        for event in urllc_events:
            urllc_pilots = self.Slices[self._URLLC].get_node(event.node_id).pilot_samples
            no_pilots -= urllc_pilots
            if no_pilots >= 0:
                # remove the event that assigned the pilots from the list
                entry = event.get_entry(self.time, True)
                # print(entry)
                self.trace.write_trace(entry)
                self.send_queue.remove(event)
                del event
            else:
                return

        if no_pilots > 0:
            mmtc_events.sort(key=lambda x: x.dead_time, reverse=True)
            for event in mmtc_events:
                mmtc_pilots = self.Slices[self._mMTC].get_node(event.node_id).pilot_samples
                no_pilots -= mmtc_pilots
                if no_pilots >= 0:
                    entry = event.get_entry(self.time, True)
                    # print(entry)
                    self.trace.write_trace(entry)
                    self.send_queue.remove(event)
                    del event
                else:
                    return

    def __round_robin_queue_info(self):
        no_pilots = self.no_pilots
        _urllc_nodes = self.Slices[self._URLLC].pool
        for _node in _urllc_nodes:
            ind = _urllc_nodes.index(_node)
            events = list(filter(lambda e: e.type == self._URLLC_ARRIVAL and e.node_id == ind, self.send_queue))
            for event in events:
                no_pilots -= _node.pilot_samples
                if no_pilots >= 0:
                    entry = event.get_entry(self.time, True)
                    self.trace.write_trace(entry)
                    self.send_queue.remove(event)
                    del event
                else:
                    return

        if no_pilots > 0:
            _mmtc_nodes = self.Slices[self._mMTC].pool
            for _node in _mmtc_nodes:
                ind = _mmtc_nodes.index(_node)
                events = list(filter(lambda e: e.type == self._mMTC_ARRIVAL and e.node_id == ind, self.send_queue))
                for event in events:
                    no_pilots -= _node.pilot_samples
                    if no_pilots >= 0:
                        entry = event.get_entry(self.time, True)
                        self.trace.write_trace(entry)
                        self.send_queue.remove(event)
                        del event
                    else:
                        return

    def __round_robin_no_queue_info(self):
        self.frame_counter = (self.frame_counter + 1) % self.frame_loops
        no_pilots = self.no_pilots
        node_pointer = 0
        for _node in self.Slices[self._URLLC]:
            no_pilots -= _node.pilot_samples

        self.__handle_send_queue()



