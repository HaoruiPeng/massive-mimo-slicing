import packet_generator as pg


class Node:
    def __init__(self, distribution, settings, buffer_size):
        self.arrival_process = pg.PacketGenerator(distribution, settings)

        self.t_control_arr = 0
        self.t_alarm_arr = 0
        self.num_in_system = 0
        self.pilot_no = 0
        self.buffer_size = buffer_size

    def handle_arrival_event(self):
        if self.num_in_system < self.buffer_size + 1:
            self.num_in_system += self.arrival_process.number_of_packets()

    def handle_departure_event(self):
        self.num_in_system -= 1
