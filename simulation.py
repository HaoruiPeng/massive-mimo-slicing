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

    _REPORT = 2
    _DECISION_MAKE = 3
    _DECISION_ARRIVAL = 4
    _DEPARTURE = 5
    _URLLC_ARRIVAL = 6
    _mMTC_ARRIVAL = 7
    
    def __init__(self, config, stats, trace, no_urllc, no_mmtc, mu, s1=None, s2=None, traffic_var=None, seed=None):
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
        self.seed = seed
        
        self.simulation_length = config.get('simulation_length')
        self.frame_length = config.get('frame_length')
        self.sampling = config.get('sampling')
        self.no_pilots = config.get('no_pilots')
        self.traffic_var = traffic_var
        
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
   
        # TODO: Here the traffic is canceled from taking new variables
        self.Slices = [Slice(self._URLLC, no_urllc, traffic_var), Slice(self._mMTC, no_mmtc)]
        
        #Decision : A dict with all the decisicion that the actuator look up every coherence interval
        #TODO:The initial number of users should follow the traffic distributtion of each slice
        
        self.report_counter = 0
        self.decision_counter = 0
        self.Decision = {
                        'counter': self.decision_counter,
                        'S1':{
                            'strategy': s1_strategy,
                            'users': round(no_urllc * 0.05)},
                        'S2':{
                            'strategy': s2_strategy,
                            'users': round(no_mmtc * 0.01)}
        }
        #TODO:Report should be the infomation of all the previous information since last report
        self.Report = {
                        'time': self.time,
                        'counter': self.report_counter,
                        'S1':{
                            'users': 0},
                        'S2':{
                            'users': 0}
        }
        
        self.Report_prev = {
                            'time': self.time,
                            'counter': self.report_counter,
                            'S1':{
                                'users': 0},
                            'S2':{
                                'users': 0}
        }
        
        self.report_queue = []
        
        self.Decision_prev = 0
   
        
        #Attributes used by only RR_NQ strategy
        self.frame_counter = 0
        self.frame_loops = self.Slices[self._URLLC].get_node(0).deadline / self.frame_length
        self.node_pointer = 0

        for s in self.Slices:
            # Initialize nodes and their arrival times
            self.__initialize_nodes(s)

        # Initialize departure event
        self.event_heap.push(self._DEPARTURE, self.time + self.frame_length)

        first_send = self.time + self.sampling
        print("[Event] --> Schedule Report No.1 send at {}".format(first_send))
        self.event_heap.push(self._REPORT, first_send)
        
        first_report_arrival = first_send + self.get_delay()
        print("[Event] --> Schedule Report No.1 arrival at MAC layer at {}".format(first_report_arrival))
        #The first decision will arrive after the report with a delay of RTT&Exec
        self.event_heap.push(self._DECISION_MAKE, first_report_arrival)

#        first_decision_arrival = first_report_arrival + self.get_delay()
#        print("[Event] --> Schedule Decision No.1 arrival at PHY layer at {}".format(first_decision_arrival))
#        self.event_heap.push(self._DECISION_ARRIVAL,first_decision_arrival)

        
    def get_delay(self):
        ##
        #Generate the delay value between PHY and MAC from a log-normal distribution
        #
        sigma = 0.02
        if self.mu <= 0:
            delay = 0
        else:
#        mu, sigma = 1.56, 0.05
            delay = np.random.lognormal(self.mu, sigma, 1) / 2.
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
            self.event_heap.push(_slice.type+6,
                                 self.time + next_arrival, self.time + next_arrival + _node.deadline,
                                 nodes.index(_node), counter)
        input("Pause")
#################################################################################################################
## Evnets Handling
#################################################################################################################
    
    def __handle_event(self, event):
        # Event switcher to determine correct action for an event
        event_actions = {
            self._URLLC_ARRIVAL: self.__handle_urllc_arrival,
            self._mMTC_ARRIVAL: self.__handle_mmtc_arrival,
            self._DEPARTURE: self.__handle_departure,
            self._REPORT: self.__handle_report,
            self._DECISION_MAKE: self.__handle_decision_make,
            self._DECISION_ARRIVAL: self.__handle_decision_arrival
        }
        event_actions[event.type](event)

    def __handle_urllc_arrival(self, event):
        self.arrival_mapping[self.Decision['S1']['strategy']](event)
        # Handle an alarm arrival event

    def __handle_mmtc_arrival(self, event):
        self.arrival_mapping[self.Decision['S2']['strategy']](event)
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

    
    def __handle_report(self, event):
        """
        Report is sent every sampling time
        """
        del event
        self.__send_report()
#        self.event_heap.push(self._REPORT, self.time + self.sampling)
#        self.event_heap.push(self._DECISION_MAKE, self.time + self.sampling + self.get_delay())
        

    def __handle_decision_make(self, event):
        """
        Descision is always passive and only triggered by a report
        """
        del event
        self.__update_report()
#        self.event_heap.push(self._DECISION_ARRIVAL, self.time + self.get_delay())
#        print("Handle decsion")

    
    def __handle_decision_arrival(self, event):
        self.__update_decision()

    
    def __handle_departure(self, event):
        """
        Handle a departure event
        """
        # print("[Time {}] Departure".format(self.time))
        # print("[Time {}] Send queue size {}" .format(self.time, len(self.send_queue)))
        del event
        self.__handle_expired_events()
        self.no_pilots = 12
        self.stats.stats['no_pilots'] += 12
        self.__assign_pilots()
        self.event_heap.push(self._DEPARTURE, self.time + self.frame_length)


    def __handle_expired_events(self):
        """
        Handle all the expired requests before assigning the pilots every coherence interval
        """

        self.__handle_urllc_expired_events()
        self.__handle_mmtc_expired_events()


    def __handle_urllc_expired_events(self):
        """
        remove the expired events in the send_queue
        """
        
        pilot_strategy = self.Decision['S1']['strategy']
        if pilot_strategy == "FCFS":
            self.__handle_station_node_queue(self._URLLC)
        if pilot_strategy == "RR_Q":
            self.__handle_signaling(self._URLLC)
        if pilot_strategy == "RR_NQ":
            self.__handle__node_queue(self._URLLC)


    def __handle_mmtc_expired_events(self):
        pilot_strategy = self.Decision['S2']['strategy']
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
        print("{} {} requests expired, remove.".format(len(remove_indices), key[slice_type]))
#        if slice_type == self._URLLC and len(remove_indices) > 0:
#            k = input("URLLC loss, pause for observe!")
        # Remove the events in reversed order to not shift subsequent indices
        for i in sorted(remove_indices, reverse=True):
            event = queue[i]
            node = self.Slices[slice_type].get_node(event.node_id)
            node.remove_event(event)
            self.stats.stats[no_missed_event[slice_type]] += 1
            entry = event.get_entry(self.time, False)
            print("[Event][{}] {} request expired, arrive at {}, deadline {}".format(self.time, key[slice_type], entry['arrival_time'], entry['dead_time']))
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
                        
#################################################################################################################
## Methods
#################################################################################################################
    
    def __send_report(self):
        """
        Send the report every sampling time, read the time of the old report
        """
        self.report_counter += 1
        print("[PHY]{} --> Report No.{} sent".format(self.time, self.report_counter))
        no_arrivals = {
            self._URLLC_ARRIVAL: 'no_urllc_arrivals',
            self._mMTC_ARRIVAL: 'no_mmtc_arrivals'
        }
        
#        report_urllc = self.stats.stats[no_arrivals[self._URLLC_ARRIVAL]]
#        report_mmtc = self.stats.stats[no_arrivals[self._mMTC_ARRIVAL]]
        
        report_urllc = len(self.send_queue['_URLLC'])
        report_mmtc = len(self.send_queue['_mMTC'])
        
        Report_Sending = {'time': self.time,
                        'counter': self.report_counter,
                        'S1':{
                            'users': report_urllc},
                        'S2':{
                            'users': report_mmtc}
        }
        self.report_queue.append(Report_Sending)
        next_send = self.time + self.sampling
        print("[Event] --> Schedule the next Report No.{} send at {}".format(Report_Sending['counter']+1, next_send))
        self.event_heap.push(self._REPORT, next_send)
        next_report_arrive = next_send +  self.get_delay()
        print("[Event] --> Schedule the next Report No.{} arrive at the MAC layer at {}".format(Report_Sending['counter']+1, next_report_arrive))
        self.event_heap.push(self._DECISION_MAKE, next_report_arrive)

    
    def __update_report(self):
        """Process the decision on the MAC and send out"""
        self.Report = self.report_queue.pop(0)
        print("[MAC]{} --> Report No.{} arrives".format(self.time, self.Report['counter']))
        interval = self.Report['time'] - self.Report_prev['time']
        print("[MAC]{} --> Last Report time: {}, This Report time: {}, report interval: {}".format(self.time, self.Report_prev['time'], self.Report['time'], interval))
        print("[MAC]{} --> Last Respot urllc {}, this Report urllc {}".format(self.time, self.Report_prev['S1']['users'], self.Report['S1']['users']))
        
        urllc_arrivals  = self.Report['S1']['users'] - self.Report_prev['S1']['users']
        mmtc_arrivals  = self.Report['S2']['users'] - self.Report_prev['S2']['users']

#        urllc_schedule = round(urllc_arrivals / (interval / self.frame_length))
#        mmtc_schedule =  round(mmtc_arrivals / (interval / self.frame_length))
        
        urllc_schedule = self.Report['S1']['users']
        mmtc_schedule = self.Report['S2']['users']
        
        self.decision_counter += 1
        self.Decision_Sending = {
                                'counter': self.decision_counter,
                                'S1':{
                                  'strategy': 'FCFS',
                                  'users': urllc_schedule},
                                'S2':{
                                  'strategy': 'FCFS',
                                  'users': mmtc_schedule}
        }
        self.Report_prev = self.Report
        decision_arrival = self.time + self.get_delay()
        print("[Event] --> Schedule the Decision No.{} arrive at the PHY layer at {}".format(self.Decision_Sending['counter'], decision_arrival))
        self.event_heap.push(self._DECISION_ARRIVAL, decision_arrival)

        
        
    def __update_decision(self):
        """Update the decision on the PHY"""
        
        self.Decision = self.Decision_Sending

        print("[PHY]{} --> Decision No.{} arrives".format(self.time, self.Decision['counter']))
        print("[PHY]{} --> Last decision arrives at {}, This decision arrives at: {}. Decision arrival  interval: {}".format(self.time, self.Decision_prev, self.time, self.Decision_prev - self.time))
        
        print("[PHY]{} --> New Decision: Scheduled URLLC:{} | Scheduled mMTC {}\n".format(self.time, self.Decision['S1']['users'], self.Decision['S2']['users']))
        
        # Update the previous report
        self.Decision_prev = self.time
        
    def __assign_pilots(self):
        self.__assign_urllc_pilots()
        if self.no_pilots > 0:
            self.__assign_mmtc_pilots()

    def __assign_urllc_pilots(self):
        no_urllc = self.Decision['S1']['users']
        print("[PHY] Take Decision No. {}. Assigned {} URLLC requests".format(self.Decision['counter'], no_urllc))
        self.strategy_mapping[self.Decision['S1']['strategy']](self._URLLC, no_urllc)

    def __assign_mmtc_pilots(self):
        no_mmtc = self.Decision['S2']['users']
        print("[PHY] Take Decision No. {}. Assigned {} mMTC requests".format(self.Decision['counter'], no_mmtc))
        self.strategy_mapping[self.Decision['S2']['strategy']](self._mMTC, no_mmtc)

    def __fist_come_first_served(self, slice_type, requests):
        no_pilots = self.no_pilots
        key = ['_URLLC', '_mMTC']
        events = self.send_queue[key[slice_type]].copy()
        print("[PHY] Number of active {} request in the queue: {}".format(key[slice_type], len(events)))
        events.sort(key=lambda x: x.dead_time)
        counter = requests
        while counter > 0 and no_pilots > 0:
            required_pilots = 1
            try:
                event = events.pop(0)
                node = self.Slices[slice_type].get_node(event.node_id)
                required_pilots = node.pilot_samples
                no_pilots -= required_pilots
                counter -= 1
                if no_pilots >= 0:
                    # remove the event that assigned the pilots from the list
                    entry = event.get_entry(self.time, True)
                    print("[Event][{}] {} Request allocated, arrive at {}, deadline {}".format(self.time, key[slice_type] , entry['arrival_time'], entry['dead_time']))
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
            except:
                counter -= 1
                no_pilots -= required_pilots
                if no_pilots >= 0:
                    print("[Event][{}] No {} requests in the queue, {} pilots wastes".format(self.time, key[slice_type], required_pilots))
                    self.stats.stats['no_waste_pilots'] += required_pilots
                else:
                    no_pilots += required_pilots
                    self.no_pilots = 0
                    return
        self.no_pilots = no_pilots

    def __round_robin_queue_info(self, slice_type, requests):
        no_pilots = self.no_pilots
        _nodes = self.Slices[slice_type].pool
        counter = requests
        for _node in self.Slices[slice_type].pool:
            if _node.active:
                for event in _node.request_queue:
                    no_pilots -= _node.pilot_samples
                    if no_pilots >= 0 and counter >= 0:
                        entry = event.get_entry(self.time, True)
                        counter -= 1
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

    def __round_robin_no_queue_info(self, slice_type, requests):
        assert slice_type == self._URLLC, "Method only applicable for slice 1"
        self.frame_counter = (self.frame_counter + 1) % self.frame_loops
        if self.frame_counter == 1:
            self.node_pointer = 0
        start_ind = self.node_pointer
        no_pilots = self.no_pilots
        counter = requests
        for i in range(start_ind, len(self.Slices[self._URLLC].pool)):
            _node = self.Slices[self._URLLC].get_node(i)
            no_pilots -= _node.pilot_samples
            if no_pilots >= 0 and counter >= 0:
                self.node_pointer += 1
                if len(_node.request_queue) > 0:
                    counter -= 1
                    event = self.Slices[self._URLLC].get_node(i).request_queue.pop(0)
                    entry = event.get_entry(self.time, True)
                    self.trace.write_trace(entry)
            else:
                no_pilots += _node.pilot_samples
                self.no_pilots = no_pilots
                return
        self.no_pilots = no_pilots
        
#################################################################################################################
## Simulation Run
#################################################################################################################

    def run(self):
        """ Runs the simulation """
        event_map = {
            self._URLLC_ARRIVAL: "URLLC_ARRIVAL",
            self._mMTC_ARRIVAL: "mMTC_ARRIVAL",
            self._DEPARTURE: "ALLOCATION",
            self._REPORT: "SEND_REPORT",
            self._DECISION_MAKE: "REC_REPORT_AND_SEND_DECISION ",
            self._DECISION_ARRIVAL:"DECISION_ARRIVAL"
        }
        current_progress = 0
        print("\n[Time {}] Simulation start.".format(self.time))
#        print("Size: {}".format(self.event_heap.get_size()))
        # for k in self.event_heap.get_heap():
        #     print(k)
        while self.time <= self.simulation_length:
#            print("[Time {}] Event heap size {}".format(self.time, self.event_heap.size()))
            next_event = self.event_heap.pop()[3]
            # print("Handle event: {} generated at time {}".format(next_event.type, next_event.time))

            # Advance time before handling event
            self.time = next_event.time
            progress = np.round(100 * self.time / self.simulation_length)

            if progress > current_progress:
                current_progress = progress
#                str1 = "\rProgress: {0}%".format(progress)
#                sys.stdout.write(str)
#                sys.stdout.flush()
#            if next_event.type not in [self._URLLC_ARRIVAL, self._mMTC_ARRIVAL]:
#                print("[Event]{} New {} event, press any key to handle".format(self.time, event_map[next_event.type]))
#                input()
            self.__handle_event(next_event)

        print('\n[Time {}] Simulation complete.'.format(self.time))

    def write_result(self):
#        result_dir = "results/" + self.Decision['S1']['strategy'] + "_" + self.Decision['S2']['strategy']
        result_dir = "results/"
        period = str(self.traffic_var[0])
        variance = str(self.traffic_var[1])
        delay_mu = str(self.mu)
        urllc_file_name = result_dir + "/" + "simulation_resultes.csv"

#        data = self.trace.get_waiting_time()
        waste = self.stats.stats['no_waste_pilots'] / self.stats.stats['no_pilots']

        try:
            os.mkdir(result_dir)
        except OSError:
            pass
            # print("Directory exists")

        try:
            file = open(urllc_file_name, 'a')
            file.write(str(self.Slices[0].no_nodes) + ','
                       + str(self.seed) + ','
                       + delay_mu + ','
                       + period + ','
                       + variance + ','
                       + str(self.trace.get_loss_rate()[0]) + ','
                       + str(waste) + '\n'
                       )
        except FileNotFoundError:
            print("No file found, create the file first")
            file = open(urllc_file_name, 'w+')
            file.write("No.URLLC,seed,delay_mu,period_var,variance_var,loss,waste\n")
            file.write(str(self.Slices[0].no_nodes) + ','
                        + str(self.seed) + ','
                        + delay_mu + ','
                        + period + ','
                        + variance + ','
                        + str(self.trace.get_loss_rate()[0]) + ','
                        + str(waste) + '\n'
                        )
        file.close()


