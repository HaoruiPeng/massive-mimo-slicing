import numpy as np


class Trace:
    _URLLC_ARRIVAL = 7
    _mMTC_ARRIVAL = 8

    def __init__(self):
        self.keys = ['event_type', 'node_id', 'counter', 'arrival_time', 'dead_time', 'departure_time', 'pilot']
        self.Dict = dict((key, []) for key in self.keys)
        self.plot_path = None
        self.urllc = {}


    def write_trace(self, entry):
        for i in range(len(entry)):
            k = self.keys[i]
            self.Dict[k] = np.append(self.Dict[k], entry[k])



    def process(self):
        keys = ['arrival_time', 'dead_time', 'departure_time', 'pilot']
        self.urllc = dict((key, []) for key in keys)
        self.mmtc = dict((key, []) for key in keys)
        event_type = self.Dict['event_type']
        arrivals = self.Dict[keys[0]]
        dead = self.Dict[keys[1]]
        departure = self.Dict[keys[2]]
        pilots = self.Dict[keys[3]]
        for i in range(np.size(event_type)):
            if event_type[i] == self._URLLC_ARRIVAL:
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
