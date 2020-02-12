import numpy as np
import scipy.stats as st


class Trace:
    _URLLC_ARRIVAL = 7
    _mMTC_ARRIVAL = 8

    def __init__(self, trace_file_path, log=False):
        self.log = log
        if log is True:
            self.__trace_file = open(trace_file_path, 'w+')
            self.__trace_file.write('Event,Node,Arrival,Dead,Departure,Mode,Pilot\n')
        else:
            self.__trace_file = None
        self.keys = ['event_type', 'node_id', 'arrival_time', 'dead_time', 'departure_time', 'pilot', 'mode']
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

    def get_arrivals(self):
        request_array = self.Dict["arrival_time"]
        arrivals = np.sort(request_array)
        return arrivals

    def get_departures(self):
        departures = np.column_stack((self.Dict['departure_time'], self.Dict['pilot']))
        return departures

    def get_loss_rate(self, time):
        inds = np.where(self.Dict['departure_time'] <= time)
        pilots = np.delete(self.Dict['pilot'], inds)
        # print(len(pilots), len(self.Dict['pilot']))
        loss_counter = 0
        for ind in range(len(pilots)):
            if not pilots[ind]:
                loss_counter += 1
        return loss_counter/len(pilots)
