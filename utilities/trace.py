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


    def get_loss_rate(self, time):
        urllc_loss = self.__get_urllc_loss()
        return urllc_loss, 0


    def __get_urllc_loss(self. time):
        inds = np.where(self.Dict['departure_time'] <= time)
        pilots = np.delete(self.Dict['pilot'], inds)
        loss_counter = 0
        for ind in range(len(pilots)):
            if not pilots[ind]:
                loss_counter += 1
        return loss_counter/len(pilots)
