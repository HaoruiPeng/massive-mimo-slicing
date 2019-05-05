class Stats:
    """
    Statistics object to keep track of simulation measurements

    Attributes
    ----------
    file : File
        File to append stats to
    no_measurements : int
        Number of measurements
    no_alarm_arrivals : int
        Number of alarm event arrivals
    no_control_arrivals : int
        Number of control event arrivals
    no_departures : int
        Number of departures
    no_missed_alarms : int
        Number of alarm events with missed deadlines
    no_missed_controls : int
        Number of control events with missed deadlines
    no_collisions : int
        Number of collisions due to pilot contamination
    """

    def __init__(self, file_path, first_run=False):
        """
        Initialize a new statistics object

        Parameters
        ----------
        file_path : str
            File path for stats file (should be .csv)
        """

        self.file = open(file_path, 'a')

        # Write the headers to the csv file
        if first_run:
            self.file.write(
                'Measurements,Alarm arrivals,Control arrivals,Departures,Missed alarms,Missed controls,Collisions\n')

        self.no_measurements = 0
        self.no_alarm_arrivals = 0
        self.no_control_arrivals = 0
        self.no_departures = 0
        self.no_missed_alarms = 0
        self.no_missed_controls = 0
        self.no_collisions = 0

    def print(self):
        """ Print the results to the terminal """
        print('Measurements: ' + str(self.no_measurements))
        print('Alarm arrivals: ' + str(self.no_alarm_arrivals))
        print('Control arrivals: ' + str(self.no_control_arrivals))
        print('Departures: ' + str(self.no_departures))
        print('Missed alarms: ' + str(self.no_missed_alarms))
        print('Missed controls: ' + str(self.no_missed_controls))
        print('Collisions: ' + str(self.no_collisions))

    def save_and_close(self):
        """ Save the results to file """

        stats_str = str(self.no_measurements) + ','
        stats_str += str(self.no_alarm_arrivals) + ','
        stats_str += str(self.no_control_arrivals) + ','
        stats_str += str(self.no_departures) + ','
        stats_str += str(self.no_missed_alarms) + ','
        stats_str += str(self.no_missed_controls) + ','
        stats_str += str(self.no_collisions) + '\n'

        self.file.write(stats_str)
        self.file.close()
