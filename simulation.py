import sys
import os
from events.event_heap import EventHeap
import numpy as np
import time
import csv
import heapq
from nodes.file_node import FileNode
from nodes.periodic_node import PeriodicNode

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

    _PERIODIC = 0
    _FILE = 1
    _SPORADIC = 2

    _ON = 1
    _OFF = 0


    _DECISION_ARRIVAL = 0
    _EXPIRE = 1
    _REPORT = 2
    _DECISION_MAKE = 3
    _ALLOCATE = 4
    _MODE_SWITCH = 5
    _PACKET_ARRIVAL = 6

    def __init__(self, config, stats, trace, no_file, no_periodic, mu, file_taffic, periodic_traffic=None, seed=None):
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
        mu : float
            Statistics of the delay
        file_taffic: (t_on, t_off, inner_periods)
        periodic_traffic: (list of periods?, variance)
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

        """
        Functiong mapping
        """
        self.strategy_mapping = {
            'FCFS': self.__fist_come_first_served,
            'RR_Q': self.__round_robin_queue_info,
            'RR_NQ': self.__round_robin_no_queue_info,
            'EDF': self.__earlist_deadline_first
        }

        self.arrival_mapping = {
            'FCFS': self.__arrival_queue,
            'RR_Q': self.__arrival_signal,
            'RR_NQ': self.__arrival_no_queue,
            'EDF': self.__arrival_queue
        }

        self.expired_mapping = {
            'FCFS': self.__handle_station_node_queue,
            'RR_Q': self.__handle_signaling,
            'RR_NQ': self.__handle__node_queue,
            'EDF': self.__handle_station_node_queue
        }

        self.event_heap = EventHeap()
        self.send_queue = []

        self.ignore = 0

        if periodic_traffic is None:
            periods = np.random.randint(1, 10, size=no_periodic)
            sum = 0
            for p in periods:
                sum += 1/p*0.5
            input(sum)
        else:
            periods = periodic_traffic[0]
            # TODO: What can beb teh input, distribution?
        inner_periods, inner_variance, t_on, t_off = file_taffic
        self.Nodes = [FileNode(inner_periods, inner_variance, t_on, t_off) for i in range(no_file)] + [PeriodicNode(p, inner_variance) for p in periods]

##########################################################################################################################################
        # Decision : A dict with all the decisicion that the actuator look up every coherence interval
        #TODO:The initial number of users should follow the traffic distributtion of each slice
        # Report-Decision Initialization
#########################################################################################################################################

        self.report_counter = 0
        self.decision_counter = 0
        self.Decision = {
                        'counter': self.decision_counter,
                        'strategy': "FCFS",
                        'users': round(no_periodic * 0.5/5.5)
        }
        #TODO:Report should be the infomation of all the previous information since last report
        self.Report = {
                        'time': self.time,
                        'counter': self.report_counter,
                        'users': 0
        }

        self.Report_prev = {
                            'time': self.time,
                            'counter': self.report_counter,
                            'users': 0
        }
        self.Decision_prev_time = 0


        self.report_queue = []
        self.decision_queue = []

########################################################################################################################################
#        Attributes Only used by only RR_NQ strategy
########################################################################################################################################"""
        self.frame_counter = 0
        self.frame_loops = self.Nodes[0].deadline / self.frame_length
        self.node_pointer = 0


########################################################################################################################################
#        Evnets Initialization
########################################################################################################################################"""
        node_index = 0
        for n in self.Nodes:
            # Initialize nodes and their arrival times
            self.__initialize_nodes(n, node_index)
            node_index += 1

        # Initialize departure event
        self.event_heap.push(self._EXPIRE, self.time + self.frame_length)
        self.event_heap.push(self._ALLOCATE, self.time + self.frame_length)

        first_send = self.time + self.sampling
        print("[Event] --> Schedule Report No.1 send at {}".format(first_send))
        self.event_heap.push(self._REPORT, first_send)

        # first_report_arrival = first_send + self.get_delay()
        # print("[Event] --> Schedule Report No.1 arrival at MAC layer at {}".format(first_report_arrival))
        # #The first decision will arrive after the report with a delay of RTT&Exec
        # self.event_heap.push(self._DECISION_MAKE, first_report_arrival)

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

    def __initialize_nodes(self, _node, _index):
        type = _node.get_type()
        if type == self._FILE:
            next_switch, next_mode = _node.mode_switch.get_init()
            self.event_heap.push(self._MODE_SWITCH,
                                 self.time + next_switch,
                                 node_id=_index, mode=self._ON)
        if type == self._PERIODIC:
            next_arrival = _node.packet_generator.get_init()
            self.event_heap.push(self._PACKET_ARRIVAL,
                                 self.time + next_arrival, dead_time=self.time + next_arrival + node.deadline,
                                 node_id=_index)
            self.stats.stats['no_arrivals'] += 1


#################################################################################################################
#    Evnets Handling
#################################################################################################################"""

    def __handle_event(self, event):
        # Event switcher to determine correct action for an event
        event_actions = {
            self._MODE_SWITCH: self._handle_mode_switch,
            self._PACKET_ARRIVAL: self.__handle_packet_arrival,
            self._EXPIRE: self.__handle_expired_events,
            self._REPORT: self.__handle_report,
            self._ALLOCATE: self.__assign_pilots,
            self._DECISION_MAKE: self.__handle_decision_make,
            self._DECISION_ARRIVAL: self.__handle_decision_arrival
        }
        event_actions[event.type](event)


#################################################################################################################
#    Mode switch Handling
#################################################################################################################"""

    def _handle_mode_switch(self, event):
        node = self.Nodes[event.get_node()]
        assert(node.node_type == self._FILE)
        node.mode = event.mode
        if event.mode == self._ON:
            print("[PHY]{} Turn Node.{} on".format(self.time, event.get_node()))
        elif event.mode == self._OFF:
            print("[PHY]{} Turn Node.{} off".format(self.time, event.get_node()))
        else:
            input("[PHY]{} Wrong mode {}:".format(self.time, event.mode))
        next_switch, next_mode = node.mode_switch.get_next(event.mode)
        self.event_heap.push(self._MODE_SWITCH,
                             self.time + next_switch,
                             node_id=event.get_node(), mode=next_mode)
        if node.mode == self._ON:
            print("[PHY][{}] Node.{} ON".format(self.time, event.get_node()))
            self.event_heap.push(self._PACKET_ARRIVAL,
                                 self.time, dead_time=self.time + node.deadline,
                                 node_id=event.get_node())
        else:
            print("[PHY][{}] Node.{} OFF".format(self.time, event.get_node()))

        del event

#################################################################################################################
#    Arrival Handling
#################################################################################################################"""

    def __handle_packet_arrival(self, event):
        self.arrival_mapping[self.Decision['strategy']](event)
        # Handle an alarm arrival event

    def __arrival_queue(self, event):
        self.stats.stats['no_arrivals'] += 1
        if self.Decision['counter'] <= 2000:
            self.ignore = self.stats.stats['no_arrivals']
            # self.ignore[queue_type[event.type]] = self.time
        # print("[Time {}] No. of urllc_arrivals: {}".format(self.time, self.stats.stats['no_urllc_arrivals']))
        assert(event.mode == None)
        node_index = event.get_node()
        node = self.Nodes[node_index]
        if node.node_type == self._FILE and node.mode == self._OFF:
            pass
        else:
            self.send_queue.append(event)
            node.push_event(event)
            next_arrival = node.packet_generator.get_next()
            self.event_heap.push(event.type,
                             self.time + next_arrival, self.time + next_arrival + node.deadline,
                             event.get_node())


#################################################################################################################
#    Non-dealt strategies RR_Q and RR_NQ
#################################################################################################################"""
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

        if self.Decision['counter'] == 0:
            self.ignore[queue_type[event.type]] = self.stats.stats[no_arrivals[event.type]]

        # print("[Time {}] No. of mmtc_arrivals: {}".format(self.time, self.stats.stats['no_mmtc_arrivals']))
        node = self.Slices[slice_type[event.type]].get_node(event.node_id)
        node.active = True
        # store the event in the node's departure queue (this is the queue not maintained by the base station)
        node.push_event(event)

        next_arrival = node.event_generator.get_next()
        self.event_heap.push(event.type,
                             self.time + next_arrival, self.time + next_arrival + node.deadline,
                             event.node_id)

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

        if self.Decision['counter'] <= 2000:
            self.ignore[queue_type[event.type]] = self.stats.stats[no_arrivals[event.type]]
        # print("[Time {}] No. of mmtc_arrivals: {}".format(self.time, self.stats.stats['no_mmtc_arrivals']))
        # Store event in send queue until departure (as LIFO)
        node = self.Slices[slice_type[event.type]].get_node(event.node_id)
        # store the event in the node's departure queue (this is the queue not maintained by the base station)
        node.push_event(event)

        next_arrival = node.event_generator.get_next()
        self.event_heap.push(event.type,
                             self.time + next_arrival, self.time + next_arrival + node.deadline,
                             event.node_id)

#################################################################################################################
#    Expiration handling
#################################################################################################################"""

    def __handle_expired_events(self, event):
        """
        Handle all the expired requests during the previous coherence interval
        """
        self.expired_mapping[self.Decision['strategy']]()
        self.event_heap.push(self._EXPIRE, self.time + self.frame_length)

    def __handle_station_node_queue(self):
        queue = self.send_queue.copy()
        queue_length = len(queue)
        remove_indices = []

        for i in range(queue_length):
            event = queue[i]
            if event.dead_time < self.time:
                remove_indices.append(i)
        print("[Event][{}] {} requests expired, remove.".format(self.time, len(remove_indices)))
        self.trace.write_loss(self.time, len(remove_indices))

        # Remove the events in reversed order to not shift subsequent indices
        for i in sorted(remove_indices, reverse=True):
            event = queue[i]
            node = self.Nodes[event.get_node()]
            node.remove_event(event)
            if self.Decision['counter'] > 0:
                self.stats.stats["no_missed"] += 1
            entry = event.get_entry(self.time, False)
            print("[Event][{}] Request expired, arrive at {}, deadline {}".format(self.time, entry['arrival_time'], entry['dead_time']))
            self.trace.write_trace(entry)
            del event
            del self.send_queue[i]

#################################################################################################################
#    Non-dealt expiration strategies RR_Q and RR_NQ
#################################################################################################################"""
    def __handle_signaling(self, slice_type):
        no_missed_event = ['no_missed_urllc', 'no_missed_mmtc']
        for node in self.Slices[slice_type].pool:
            if node.active:
                for event in node.request_queue:
                    if event.dead_time < self.time:
                        node.remove_event(event)
                        if self.Decision['counter'] > 0:
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
                        if self.Decision['counter'] > 0:
                            self.stats.stats[no_missed_event[slice_type]] += 1
                        entry = event.get_entry(self.time, False)
                        self.trace.write_trace(entry)
                        del event

#################################################################################################################
#    Report and Decision handling
#################################################################################################################"""

    def __handle_report(self, event):
        """
        Report is sent every sampling time
        """
        del event
        self.__send_report()

    def __handle_decision_make(self, event):
        """
        Descision is always passive and only triggered by a report
        """
        del event
        self.__update_report()


    def __handle_decision_arrival(self, event):
        self.__update_decision()


    def __send_report(self):
        """
        Send the report every sampling time, read the time of the old report
        """
        self.report_counter += 1
        print("[PHY]{} --> Report No.{} sent".format(self.time, self.report_counter))

        report = len(self.send_queue)

        Report_Sending = {
                        'time': self.time,
                        'counter': self.report_counter,
                        'users': report
                        }

        report_arrive = self.time + self.get_delay()
        print("[Event] --> Schedule the Report No.{} arrive at the MAC layer at {}".format(Report_Sending['counter'], report_arrive))
        heapq.heappush(self.report_queue, (report_arrive, Report_Sending))
        self.event_heap.push(self._DECISION_MAKE, report_arrive)

        next_send = self.time + self.sampling
        print("[Event] --> Schedule the next Report No.{} send at {}".format(Report_Sending['counter']+1, next_send))
        self.event_heap.push(self._REPORT, next_send)

    def __update_report(self):
        """Process the decision on the MAC and send out"""
        print("[MAC] {}".format(self.time))
        arrive, self.Report = heapq.heappop(self.report_queue)
        assert(arrive == self.time)
        print("[MAC]{} --> Report No.{} arrives".format(self.time, self.Report['counter']))
        interval = self.Report['time'] - self.Report_prev['time']
        print("[MAC]{} --> Last Report time: {}, This Report time: {}, report interval: {}".format(self.time, self.Report_prev['time'], self.Report['time'], interval))

        decision = self.Report['users'] if self.Report['users'] < 12 else 12
        strategy = "FCFS"
        self.decision_counter += 1
        Decision_Sending = {
                            'counter': self.decision_counter,
                            'strategy': strategy,
                            'users': decision
                            }
        self.Report_prev = self.Report

        decision_arrive = self.time + self.get_delay()
        print("[Event] --> Schedule the Decision No.{} arrive at the PHY layer at {}".format(Decision_Sending['counter'], decision_arrive))
        self.event_heap.push(self._DECISION_ARRIVAL, decision_arrive)
        heapq.heappush(self.decision_queue, (decision_arrive, Decision_Sending))


    def __update_decision(self):
        """Update the decision on the PHY"""

        arrive, self.Decision = heapq.heappop(self.decision_queue)
        assert(arrive == self.time)
        print("[PHY]{} --> Decision No.{} arrives".format(self.time, self.Decision['counter']))
        print("[PHY]{} --> Last decision arrives at {}, This decision arrives at: {}. Decision arrival  interval: {}".format(self.time, self.Decision_prev_time, self.time, self.time - self.Decision_prev_time))
        print("[PHY]{} --> New Decision: Schedule requests: {}\n".format(self.time, self.Decision['users']))

        # Update the previous report
        self.Decision_prev_time = self.time


#################################################################################################################
#    Assign pilots
#################################################################################################################"""
    def __assign_pilots(self, event):
        del event;
        self.no_pilots = 12
        self.stats.stats['no_pilots'] += 12
        decision = self.Decision['users']  #TODO: Decision never exceeds 12
        print("[PHY] Take Decision No. {}. Assign {} requests".format(self.Decision['counter'], decision))
        self.trace.write_decision(self.time, decision)
        self.strategy_mapping[self.Decision['strategy']](decision)
        self.event_heap.push(self._ALLOCATE, self.time + self.frame_length)

    def __fist_come_first_served(self, requests):
        no_pilots = self.no_pilots
        waste_count = 0
        queue = self.send_queue.copy()
        print("[PHY] Number of active request in the queue: {}".format(len(queue)))
        self.trace.write_queue_length(self.time, len(queue))

        # queue.sort(key=lambda x: x.dead_time)
        counter = requests
        while counter > 0:
            required_pilots = 1
            try:
                event = queue.pop(0)
                assert(event.mode == None)
                node = self.Nodes[event.get_node()]
                required_pilots = node.pilot_samples
                counter -= 1
                # remove the event that assigned the pilots from the list
                entry = event.get_entry(self.time, True)
                # print("[Event][{}] {} Request allocated, arrive at {}, deadline {}".format(self.time, key[slice_type] , entry['arrival_time'], entry['dead_time']))
                # print(entry)
                self.trace.write_trace(entry)
                self.send_queue.remove(event)
                node.remove_event(event)
            except:
                counter -= 1
                if self.Decision['counter'] > 2000:
                    self.stats.stats['no_waste_pilots'] += required_pilots
                waste_count += required_pilots

        self.trace.write_waste(self.time, waste_count)
        if self.Decision['counter'] <= 2000:
            self.stats.stats['no_pilots'] = 0

    def __earlist_deadline_first(requests):
        no_pilots = self.no_pilots
        waste_count = 0
        queue = self.send_queue.copy()
        print("[PHY] Number of active request in the queue: {}".format(len(queue)))
        self.trace.write_queue_length(self.time, len(queue))

        queue.sort(key=lambda x: x.dead_time)
        counter = requests
        while counter > 0:
            required_pilots = 1
            try:
                event = queue.pop(0)
                assert(event.mode == None)
                node = self.Nodes[event.get_node()]
                required_pilots = node.pilot_samples
                counter -= 1
                # remove the event that assigned the pilots from the list
                entry = event.get_entry(self.time, True)
                # print("[Event][{}] {} Request allocated, arrive at {}, deadline {}".format(self.time, key[slice_type] , entry['arrival_time'], entry['dead_time']))
                # print(entry)
                self.trace.write_trace(entry)
                self.send_queue.remove(event)
                node.remove_event(event)
            except:
                counter -= 1
                if self.Decision['counter'] > 2000:
                    self.stats.stats['no_waste_pilots'] += required_pilots
                waste_count += required_pilots

        self.trace.write_waste(self.time, waste_count)
        if self.Decision['counter'] <= 2000:
            self.stats.stats['no_pilots'] = 0

#################################################################################################################
#    Non-dealt pilot assignment for strategies RR_Q and RR_NQ
#################################################################################################################"""
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
#    Simulation Run
#################################################################################################################"""

    def run(self):
        """ Runs the simulation """
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
            self.__handle_event(next_event)

        print('\n[Time {}] Simulation complete.'.format(self.time))

    def write_result(self):
        result_dir = "results/"
        delay_mu = str(self.mu)

        ts_dir = "time_series/" + str(len(self.Nodes)) + '-' + str(self.seed) + '-' + delay_mu + "-" + str(round(time.time())) + "/"

        urllc_file_name = result_dir + "/" + "simulation_results.csv"

        loss = self.stats.stats['no_missed'] / (self.stats.stats['no_arrivals'] - self.ignore)
        # loss = self.stats.stats['no_missed_urllc'] / (self.stats.stats['no_urllc_arrivals'])
        # loss = self.trace.get_loss_rate(self.ignore['_URLLC'])[0]
        waste = self.stats.stats['no_waste_pilots'] / self.stats.stats['no_pilots']
        # print(self.stats.stats['no_waste_pilots'],self.stats.stats['no_pilots'])

        try:
            os.mkdir(result_dir)
        except OSError:
            pass
        try:
            os.makedirs(ts_dir)
        except OSError:
            pass
        #
        # keys = ["No.URLLC","seed","delay_mu","period_var","deadline_var","period_mean","deadline_mean","mean_ratio","variance_var","loss","waste"]
        # try:
        #     file = open(urllc_file_name, 'a')
        # except FileNotFoundError:
        #     print("No file found, create the file first")
        #     file = open(urllc_file_name, 'w')
        #     writer = csv.DictWriter(file, fieldnames=keys)
        #     writer.writeheader()
        #
        # file.write(str(self.Slices[0].no_nodes) + ','
        #            + str(self.seed) + ','
        #            + delay_mu + ','
        #            + ratio + ','
        #            + period + ','
        #            + deadline + ','
        #            + variance + ','
        #            + str(p_mean) + ','
        #            + str(d_mean) + ','
        #            + str(mean_ratio) + ','
        #            + str(loss) + ','
        #            + str(waste) + '\n'
        #            )
        # file.close()

        arrival_trace = self.trace.get_arrivals()
        departure_trace = self.trace.get_departures()

        with open(ts_dir + "arrivals.txt", 'w+') as f:
            for d in arrival_trace:
                f.write(str(d) + "\n")

        with open(ts_dir + "departures.txt", 'w+') as f:
            for d in departure_trace:
                f.write(str(d[0]) + "," + str(d[1]) +"\n")
        #
        # period_array, dealine_array = self.Slices[0].get_traffics()
        #
        # with open(ts_dir + "traffics.txt", 'w+') as f:
        #     for i in range(len(period_array)):
        #         f.write(str(period_array[i]) + "," + str(dealine_array[i]) +"\n")

        with open(ts_dir + "queue_length.txt", 'w+') as f:
            for d in self.trace.queue_length:
                f.write(str(d[0]) + "," + str(d[1]) +"\n")

        with open(ts_dir + "waste.txt", 'w+') as f:
            for d in self.trace.waste_trace:
                f.write(str(d[0]) + "," + str(d[1]) +"\n")

        with open(ts_dir + "loss.txt", 'w+') as f:
            for d in self.trace.loss_trace:
                f.write(str(d[0]) + "," + str(d[1]) +"\n")

        with open(ts_dir + "decision.txt", 'w+') as f:
            for d in self.trace.decision_trace:
                f.write(str(d[0]) + "," + str(d[1]) +"\n")
