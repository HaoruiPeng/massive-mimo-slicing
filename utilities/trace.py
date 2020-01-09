import numpy as np
import scipy.stats as st


class Trace:
    _URLLC_ARRIVAL = 7
    _mMTC_ARRIVAL = 8

    def __init__(self, trace_file_path, log=False):
        self.log = log
        if log is True:
            self.__trace_file = open(trace_file_path, 'w+')
            self.__trace_file.write('Event,Node,Counter,Arrival,Dead,Departure,Pilot\n')
        else:
            self.__trace_file = None
        self.keys = ['event_type', 'node_id', 'counter', 'arrival_time', 'dead_time', 'departure_time', 'pilot']
        self.Dict = dict((key, []) for key in self.keys)
        self.plot_path = None
        self.urllc = {}

        self.queue_length = np.empty((0,2), int)
        self.waste_trace = np.empty((0,2), int)
        self.loss_trace = np.empty((0,2), int)
        self.decision_trace = np.empty((0,2), int)


    def close(self):
        if self.log is True:
            self.__trace_file.close()
        else:
            pass

    def write_trace(self, entry):
        if self.log is True:
            self.__trace_file.write(str(entry[self.keys[0]]) + ',' + str(entry[self.keys[1]]) + ','
                                    + str(entry[self.keys[2]]) + ',' + str(entry[self.keys[3]]) + ','
                                    + str(entry[self.keys[4]]) + ',' + str(entry[self.keys[5]]) + ','
                                    + str(entry[self.keys[6]]) + '\n')

        for i in range(len(entry)):
            k = self.keys[i]
            self.Dict[k] = np.append(self.Dict[k], entry[k])

    def write_queue_length(self, time_sp, queue_len):
        self.queue_length = np.append(self.queue_length, np.array([[time_sp, queue_len]]), axis=0)

    def write_loss(self, time_sp, no_loss):
        self.loss_trace = np.append(self.loss_trace, np.array([[time_sp, no_loss]]), axis=0)

    def write_waste(self, time_sp, no_waste):
        self.waste_trace = np.append(self.waste_trace, np.array([[time_sp, no_waste]]), axis=0)

    def write_decision(self, time_sp, decision):
        self.decision_trace = np.append(self.decision_trace, np.array([[time_sp, decision]]), axis=0)


    def process(self):
        keys = ['arrival_time', 'dead_time', 'departure_time', 'pilot']
        self.urllc = dict((key, []) for key in keys)
        event_type = self.Dict['event_type']
        arrivals = self.Dict[keys[0]]
        dead = self.Dict[keys[1]]
        departure = self.Dict[keys[2]]
        pilots = self.Dict[keys[3]]
        for i in range(np.size(event_type)):
            self.urllc[keys[0]] = np.append(self.urllc[keys[0]], arrivals[i])
            self.urllc[keys[1]] = np.append(self.urllc[keys[1]], dead[i])
            self.urllc[keys[2]] = np.append(self.urllc[keys[2]], departure[i])
            self.urllc[keys[3]] = np.append(self.urllc[keys[3]], pilots[i])


    def get_loss_rate(self):
        urllc_loss = self.__get_urllc_loss()
        return urllc_loss, 0

    def __get_urllc_loss(self):
        pilots = self.urllc['pilot']
        print(len(pilots))
        loss_counter = 0
        for ind in range(len(pilots)):
            if not pilots[ind]:
                loss_counter += 1
        return loss_counter/len(pilots)
