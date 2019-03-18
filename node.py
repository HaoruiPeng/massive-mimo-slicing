import packet_generator as pg


class Node:
    def __init__(self, distribution, settings):
        self.arrival_process = pg.PacketGenerator(distribution, settings)

        self.t_control_arr = 0
        self.t_alarm_arr = 0
        self.num_in_system = 0
        self.pilotNo = 0

    def handle_arrival_event(self):
        self.num_in_system += self.arrival_process.number_of_packets()

    def handle_departure_event(self):
        self.num_in_system -= 1
