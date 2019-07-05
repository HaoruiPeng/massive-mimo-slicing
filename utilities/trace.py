import matplotlib as plt
import numpy as np
import os
import time


class Trace:
    def __init__(self, trace_file_path):
        self.__trace_file = open(trace_file_path, 'w+')
        self.__trace_file.write('Event,Node,Counter,Arrival,Dead,Departure,Pilot\n')
        self.keys = ['event_type', 'node_id', 'counter', 'arrival_time', 'dead_time', 'departure_time', 'pilot']
        self.Dict = dict((key, []) for key in self.keys)
        self.plot_path = None

    def close(self):
        self.__trace_file.close()

    def write_trace(self, entry):
        # print(entry['event_type'])
        self.__trace_file.write(str(entry[self.keys[0]]) + ',' + str(entry[self.keys[1]]) + ','
                                + str(entry[self.keys[2]]) + ',' + str(entry[self.keys[3]]) + ','
                                + str(entry[self.keys[4]]) + ',' + str(entry[self.keys[5]]) + ','
                                + str(entry[self.keys[6]]) + '\n')
        for i in range(len(entry)):
            k = self.keys[i]
            self.Dict[k] = np.append(self.Dict[k], entry[k])

    def process(self):
        pass

    def create_plots(self):
        time_string = time.strftime('%Y%m%d_%H%M%S')
        self.plot_path = "/plots/" + time_string
        try:
            os.mkdir(self.plot_path)
        except OSError:
            print("Plots directory {} creation fails".format(self.plot_path))
            return False
        else:
            print("Plots directory {} created".format(self.plot_path))
            return True
        pass
