import sys
import os
from events.event_heap import EventHeap
import numpy as np
from slices.slice import Slice


class Simulation:
    """
    Simulation for a network slicing strategy on MAC layer of a massive MIMO network

    Attributes
    ----------


    Methods
    -------
    run()
        Runs the simulation the full simulation length
    """

    _URLLC = 0
    _mMTC = 1

    _DEPARTURE = 2
    _URLLC_ARRIVAL = 3
    _mMTC_ARRIVAL = 4
    _REPORT = 5
    _DECISION = 6

    def __init__(self, config, stats, trace, no_urllc, no_mmtc, mu, s1=None, s2=None, traffic=None):
        """
        Initialize simulation object

        Parameters
        ----------
        config : dict
            Dictionary containing all configuration parameters
            no_pilots : the total number of pilots per coherence interval\
            frame_length : coherence interval
            sampling : The rate to send out the desicions
        stats : Stats
            Statistics object for keeping track for measurements
        trace : bool
            Indicate whether to trace the
        no_urllc : int
            TODO: will be sperated to the UE function
            Number of UEs in slice 1
        no_mmtc : int
           TODO: will be sperated to the UE function
           Number of UEs in slice 2
        mu : float
            Statistics of the delay
        s1 : String
            Initial strategy of slice 1
        s2 : String
            Initial strategy of slice 2
        traffic : tube of string
            TODO: will be sperated to the UE function
            Traffic type of the slice 1
        
        """

        self.stats = stats
        self.trace = trace
        self.mu = mu
        self.time = 0.0
        
        self.simulation_length = config.get('simulation_length')
        self.frame_length = config.get('frame_length')
        self.sampling = config.get('sampling')
        self.no_pilots = config.get('no_pilots')
        
        
        #Initial strategy of both slices, will be changed be the decisions
        if s1 is not None:
            s1_strategy = s1
        else:
            s1_strategy = config.get('strategy_s1')

        if s2 is not None:
            s2_strategy = s2
        else:
            s1_strategy = config.get('strategy_s2')

        self.strategy_mapping = {
            'FCFS': self.__fist_come_first_served,
            'RR_Q': self.__round_robin_queue_info,
            'RR_NQ': self.__round_robin_no_queue_info,
        }

        self.arrival_mapping = {
            'FCFS': self.__arrival_queue,
            'RR_Q': self.__arrival_signal,
            'RR_NQ': self.__arrival_no_queue,
        }
        
        self.event_heap = EventHeap()
        self.send_queue = {'_URLLC': [], '_mMTC': []}
   
        
        self.Slices = [Slice(self._URLLC, no_urllc, traffic), Slice(self._mMTC, no_mmtc)]
        
        #Decision : A dict with all the decisicion that the actuator look up every coherence interval
        #TODO:The initial number of users should follow the traffic distributtion of each slice
        self.Decision = {
                        'S1':{
                            'strategy': s1_strategy,
                            'users': round(no_urllc * 0.5)},
                        'S2':{
                            'strategy': s2_strategy,
                            'users': round(no_mmtc * 0.01)}
        }
        #TODO:Report should be the infomation of all the previous information since last report
        self.Report = {
                        'S1':{
                            'users': 0},
                        'S2':{
                            'users': 0}
        }
        
        #Attributes used by only RR_NQ strategy
        self.frame_counter = 0
        self.frame_loops = self.Slices[self._URLLC].get_node(0).deadline / self.frame_length
        self.node_pointer = 0

        for s in self.Slices:
            # Initialize nodes and their arrival times
            self.__initialize_nodes(s)

        # Initialize departure event
        self.event_heap.push(self._DEPARTURE, self.time + self.frame_length)
        self.event_heap.push(self._REPORT, self.time + self.sampling)
        #The first decision will arrive after the report with a delay of RTT&Exec
        self.event_heap.push(self._DECISION, self.time + self.sampling + self.get_delay())
        
    def get_delay(self):
        ##
        #Generate the delay value between PHY and MAC from a log-normal distribution
        #
        mu, sigma = 2.26, 0.02
        delay = np.random.lognormal(mu, sigma, 1)
        return delay
    

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
            self.event_heap.push(_slice.type+3,
                                 self.time + next_arrival, self.time + next_arrival + _node.deadline,
                                 nodes.index(_node), counter)

    def __handle_event(self, event):
        # Event switcher to determine correct action for an event
        event_actions = {
            self._URLLC_ARRIVAL: self.__handle_urllc_arrival,
            self._mMTC_ARRIVAL: self.__handle_mmtc_arrival,
            self._DEPARTURE: self.__handle_departure}
        event_actions[event.type](event)

    def __handle_urllc_arrival(self, event):
        self.arrival_mapping[self.Slices[self._URLLC].strategy](event)
        # Handle an alarm arrival event

    def __handle_mmtc_arrival(self, event):
        self.arrival_mapping[self.Slices[self._mMTC].strategy](event)
        # Handle a control arrival event

    def __arrival_queue(self, event):
        no_arrivals = {
            self._URLLC_ARRIVAL: 'no_urllc_arrivals',
            self._mMTC_ARRIVAL: 'no_mmtc_arrivals'
        }
        queue_type = {
            self._URLLC_ARRIVAL: '_URLLC',
            self._mMTC_ARRIVAL: '_mMTC'
        }
        slice_type = {
            self._URLLC_ARRIVAL: self._URLLC,
            self._mMTC_ARRIVAL: self._mMTC
        }
        self.stats.stats[no_arrivals[event.type]] += 1
        # print("[Time {}] No. of urllc_arrivals: {}".format(self.time, self.stats.stats['no_urllc_arrivals']))

        # Store event in send queue until departure (as LIFO)
        self.send_queue[queue_type[event.type]].append(event)
        node = self.Slices[slice_type[event.type]].get_node(event.node_id)
        # store the event in the node's departure queue (this is the queue not maintained by the base station)
        node.push_event(event)

        next_arrival = node.event_generator.get_next()
        self.event_heap.push(event.type,
                             self.time + next_arrival, self.time + next_arrival + node.deadline,
                             event.node_id, self.stats.stats[no_arrivals[event.type]])

    def __arrival_signal(self, event):
        no_arrivals = {
            self._URLLC_ARRIVAL: 'no_urllc_arrivals',
            self._mMTC_ARRIVAL: 'no_mmtc_arrivals'
        }
        slice_type = {
            self._URLLC_ARRIVAL: self._URLLC,
            self._mMTC_ARRIVAL: self._mMTC
        }
        self.stats.stats[no_arrivals[event.type]] += 1
        # print("[Time {}] No. of mmtc_arrivals: {}".format(self.time, self.stats.stats['no_mmtc_arrivals']))
        node = self.Slices[slice_type[event.type]].get_node(event.node_id)
        node.active = True
        # store the event in the node's departure queue (this is the queue not maintained by the base station)
        node.push_event(event)

        next_arrival = node.event_generator.get_next()
        self.event_heap.push(event.type,
                             self.time + next_arrival, self.time + next_arrival + node.deadline,
                             event.node_id, self.stats.stats[no_arrivals[event.type]])

    def __arrival_no_queue(self, event):
        no_arrivals = {
            self._URLLC_ARRIVAL: 'no_urllc_arrivals',
            self._mMTC_ARRIVAL: 'no_mmtc_arrivals'
        }
        slice_type = {
            self._URLLC_ARRIVAL: self._URLLC,
            self._mMTC_ARRIVAL: self._mMTC
        }
        self.stats.stats[no_arrivals[event.type]] += 1
        # print("[Time {}] No. of mmtc_arrivals: {}".format(self.time, self.stats.stats['no_mmtc_arrivals']))
        # Store event in send queue until departure (as LIFO)
        node = self.Slices[slice_type[event.type]].get_node(event.node_id)
        # store the event in the node's departure queue (this is the queue not maintained by the base station)
        node.push_event(event)

        next_arrival = node.event_generator.get_next()
        self.event_heap.push(event.type,
                             self.time + next_arrival, self.time + next_arrival + node.deadline,
                             event.node_id, self.stats.stats[no_arrivals[event.type]])

    def __handle_departure(self, event):
        # Handle a departure event
        # print("[Time {}] Departure".format(self.time))
        # print("[Time {}] Send queue size {}" .format(self.time, len(self.send_queue)))
        del event
        self.__handle_expired_events()
        self.no_pilots = 12
        self.__assign_pilots()
        # self.__check_collisions()
        # Add new departure event to the event list, pull the delay from a multi gussian distribution
#        mu, sigma = 2.26, 0.02
#        delay = np.random.lognormal(mu, sigma, 1)
        self.event_heap.push(self._DEPARTURE, self.time + self.frame_length)
    
    def __handle_decision(self, event):
    ##
    #Desision will arrival every smapling time, which descision the number of users every sampling time and the schduler to use
    ##
        
        self.event_heap.push(self.DE\\_DECISION_ARRIVAL, self.time + self.sampling + delay)

    def __handle_expired_events(self):
        self.__handle_urllc_expired_events()
        self.__handle_mmtc_expired_events()

    def __handle_urllc_expired_events(self):
        # remove the expired events in the send_queue
        pilot_strategy = self.Slices[self._URLLC].strategy
        if pilot_strategy == "FCFS":
            self.__handle_station_node_queue(self._URLLC)
        if pilot_strategy == "RR_Q":
            self.__handle_signaling(self._URLLC)
        if pilot_strategy == "RR_NQ":
            self.__handle__node_queue(self._URLLC)

    def __handle_mmtc_expired_events(self):
        pilot_strategy = self.Slices[self._mMTC].strategy
        if pilot_strategy == "FCFS":
            self.__handle_station_node_queue(self._mMTC)
        if pilot_strategy == "RR_Q":
            self.__handle_signaling(self._mMTC)
        if pilot_strategy == "RR_NQ":
            self.__handle__node_queue(self._mMTC)

    def __handle_station_node_queue(self, slice_type):
        key = ['_URLLC', '_mMTC']
        no_missed_event = ['no_missed_urllc', 'no_missed_mmtc']
        queue = self.send_queue[key[slice_type]]

        queue_length = len(queue)
        remove_indices = []

        for i in range(queue_length):
            event = queue[i]
            if event.dead_time < self.time:
                remove_indices.append(i)

        # Remove the events in reversed order to not shift subsequent indices
        for i in sorted(remove_indices, reverse=True):
            event = queue[i]
            node = self.Slices[slice_type].get_node(event.node_id)
            node.remove_event(event)
            self.stats.stats[no_missed_event[slice_type]] += 1
            entry = event.get_entry(self.time, False)
            self.trace.write_trace(entry)
            del event
            del self.send_queue[key[slice_type]][i]

        # if len(remove_indices) > 0:
        #       print("\n[Time {}] Lost {} URLLC packets, {} mMTC packets\n"
        #               .format(self.time, urllc_counter, mmtc_counter))

    def __handle_signaling(self, slice_type):
        no_missed_event = ['no_missed_urllc', 'no_missed_mmtc']
        for node in self.Slices[slice_type].pool:
            if node.active:
                for event in node.request_queue:
                    if event.dead_time < self.time:
                        node.remove_event(event)
                        self.stats.stats[no_missed_event[slice_type]] += 1
                        entry = event.get_entry(self.time, False)
                        self.trace.write_trace(entry)
                        del event
            if len(node.request_queue) == 0:
                node.active = False

    def __handle__node_queue(self, slice_type):
        no_missed_event = ['no_missed_urllc', 'no_missed_mmtc']
        for node in self.Slices[slice_type].pool:
            if len(node.request_queue) > 0:
                for event in node.request_queue:
                    if event.dead_time < self.time:
                        node.remove_event(event)
                        self.stats.stats[no_missed_event[slice_type]] += 1
                        entry = event.get_entry(self.time, False)
                        self.trace.write_trace(entry)
                        del event

    def __assign_pilots(self):
        self.__assign_urllc_pilots()
        if self.no_pilots > 0:
            self.__assign_mmtc_pilots()

    def __assign_urllc_pilots(self):
        self.strategy_mapping[self.Slices[self._URLLC].strategy](self._URLLC)

    def __assign_mmtc_pilots(self):
        self.strategy_mapping[self.Slices[self._mMTC].strategy](self._mMTC)

    def __fist_come_first_served(self, slice_type):
        no_pilots = self.no_pilots
        key = ['_URLLC', '_mMTC']
        events = self.send_queue[key[slice_type]].copy()
        events.sort(key=lambda x: x.dead_time)
        for event in events:
            node = self.Slices[slice_type].get_node(event.node_id)
            required_pilots = node.pilot_samples
            no_pilots -= required_pilots
            if no_pilots >= 0:
                # remove the event that assigned the pilots from the list
                entry = event.get_entry(self.time, True)
                # print(entry)
                self.trace.write_trace(entry)
                self.send_queue[key[slice_type]].remove(event)
                self.Slices[slice_type].get_node(event.node_id).remove_event(event)
                # print(no_pilots, len(self.send_queue['_URLLC']), len(urllc_events))
            else:
                # print("pilot not enough")
                no_pilots += required_pilots
                self.no_pilots = no_pilots
                return
        self.no_pilots = no_pilots

    def __round_robin_queue_info(self, slice_type):
        no_pilots = self.no_pilots
        _nodes = self.Slices[slice_type].pool
        for _node in self.Slices[slice_type].pool:
            if _node.active:
                for event in _node.request_queue:
                    no_pilots -= _node.pilot_samples
                    if no_pilots >= 0:
                        entry = event.get_entry(self.time, True)
                        self.trace.write_trace(entry)
                        _node.remove_event(event)
                        del event
                        if len(_node.request_queue) == 0:
                            _node.active = False
                    else:
                        no_pilots += _node.pilot_samples
                        self.no_pilots = no_pilots
                        return
        self.no_pilots = no_pilots

    def __round_robin_no_queue_info(self, slice_type):
        assert slice_type == self._URLLC, "Method only applicable for slice 1"
        self.frame_counter = (self.frame_counter + 1) % self.frame_loops
        if self.frame_counter == 1:
            self.node_pointer = 0
        start_ind = self.node_pointer
        no_pilots = self.no_pilots
        for i in range(start_ind, len(self.Slices[self._URLLC].pool)):
            _node = self.Slices[self._URLLC].get_node(i)
            no_pilots -= _node.pilot_samples
            if no_pilots >= 0:
                self.node_pointer += 1
                if len(_node.request_queue) > 0:
                    event = self.Slices[self._URLLC].get_node(i).request_queue.pop(0)
                    entry = event.get_entry(self.time, True)
                    self.trace.write_trace(entry)
            else:
                no_pilots += _node.pilot_samples
                self.no_pilots = no_pilots
                return
        self.no_pilots = no_pilots

    def run(self):
        """ Runs the simulation """

        current_progress = 0
        print("\n[Time {}] Simulation start.".format(self.time))
#        print("Size: {}".format(self.event_heap.get_size()))
        # for k in self.event_heap.get_heap():
        #     print(k)
        while self.time < self.simulation_length:
#            print("[Time {}] Event heap size {}".format(self.time, self.event_heap.size()))
            next_event = self.event_heap.pop()[3]
            # print("Handle event: {} generated at time {}".format(next_event.type, next_event.time))

            # Advance time before handling event
            self.time = next_event.time

            progress = np.round(100 * self.time / self.simulation_length)

            if progress > current_progress:
                current_progress = progress
                str1 = "\rProgress: {0}%".format(progress)
                sys.stdout.write(str1)
                sys.stdout.flush()

            self.__handle_event(next_event)

        print('\n[Time {}] Simulation complete.'.format(self.time))

    def write_result(self):
        result_dir = "results/" + self.s1_strategy + "_" + self.s2_strategy
        reliability = self.Slices[self._URLLC].get_node(0).reliability_profile
        deadline = self.Slices[self._URLLC].get_node(0).deadline_profile
        urllc_file_name = result_dir + "/" + reliability + "_" + deadline + "_" + str(self.mu)+"_URLLC.csv"
        mmtc_file_name = result_dir + "/" + reliability + "_" + deadline + "_" + str(self.mu)+"_mMTC.csv"

        data = self.trace.get_waiting_time()

        try:
            os.mkdir(result_dir)
        except OSError:
            pass
            # print("Directory exists")

        try:
            file = open(urllc_file_name, 'a')
            file.write(str(self.Slices[0].no_nodes) + ','
                       + str(self.Slices[1].no_nodes) + ','
                       + str(data[0][0]) + ','
                       + str(data[0][1]) + ','
                       + str(data[0][2]) + ','
                       + str(data[0][3]) + ','
                       + str(self.trace.get_loss_rate()[0]) + '\n'
                       )
        except FileNotFoundError:
            print("No file found, create the file first")
            file = open(urllc_file_name, 'w+')
            file.write("No.URLLC,No.mMTC,mean,var,conf_inter_up,conf_inter_low,loss\n")
            file.write(str(self.Slices[0].no_nodes) + ','
                       + str(self.Slices[1].no_nodes) + ','
                       + str(data[0][0]) + ','
                       + str(data[0][1]) + ','
                       + str(data[0][2]) + ','
                       + str(data[0][3]) + ','
                       + str(self.trace.get_loss_rate()[0]) + '\n'
                       )
        file.close()
        try:
            file = open(mmtc_file_name, 'a')
            file.write(str(self.Slices[0].no_nodes) + ','
                       + str(self.Slices[1].no_nodes) + ','
                       + str(data[1][0]) + ','
                       + str(data[1][1]) + ','
                       + str(data[1][2]) + ','
                       + str(data[1][3]) + ','
                       + str(self.trace.get_loss_rate()[1]) + '\n'
                       )
        except FileNotFoundError:
            print("No file found, create the file first")
            file = open(mmtc_file_name, 'w+')
            file.write("No.URLLC,No.mMTC,mean,var,conf_inter_up,conf_inter_low,loss\n")
            file.write(str(self.Slices[0].no_nodes) + ','
                       + str(self.Slices[1].no_nodes) + ','
                       + str(data[1][0]) + ','
                       + str(data[1][1]) + ','
                       + str(data[1][2]) + ','
                       + str(data[1][3]) + ','
                       + str(self.trace.get_loss_rate()[1]) + '\n'
                       )
        file.close()


