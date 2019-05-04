class Stats:
    def __init__(self):
        self.no_measurements = 0
        self.no_alarm_arrivals = 0
        self.no_control_arrivals = 0
        self.no_departures = 0
        self.alarm_in_queue = 0
        self.control_in_queue = 0
        self.missed_alarms = 0
        self.missed_controls = 0
        self.no_collisions = 0

    def print(self):
        print('Measurement: ' + str(self.no_measurements))
        print('Alarm arrivals: ' + str(self.no_alarm_arrivals))
        print('Control arrivals: ' + str(self.no_control_arrivals))
        print('Departures: ' + str(self.no_departures))
        print('Missed alarms: ' + str(self.missed_alarms))
        print('Missed controls: ' + str(self.missed_controls))
        print('No collisions: ' + str(self.no_collisions))
