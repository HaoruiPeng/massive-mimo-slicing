import packet_generator as pg


class Node:
    def __init__(self, distribution, settings, buffer_size):
        self.arrival_process = pg.PacketGenerator(distribution, settings)
        self.num_in_system = 0
        self.pilot_no = 0
        self.buffer_size = buffer_size
        self.want_to_send = False

    def handle_arrival(self):
        if self.num_in_system < self.buffer_size + 1:
            self.num_in_system += self.arrival_process.number_of_packets()

    def try_to_depart(self):
        if self.num_in_system > 0:
            self.want_to_send = True
            return True

        return False

    def handle_departure(self):
        self.num_in_system -= 1
        self.want_to_send = False
