import numpy as np
import math

__author__ = "Jon Stålhammar, Christian Lejdström, Emma Fitzgerald"


class Stats:
    """
    Statistics object to keep track of simulation measurements

    Methods
    -------

    """

    def __init__(self, stats_file_path, log_file_path):
        """
        Initialize a new statistics and logging object

        Parameters
        ----------
        stats_file_path : str
            Path to stats file
        log_file_path : str
            Path to logging file
        """

        self.__stats_file = open(stats_file_path, 'w')
        self.__log_file = open(log_file_path, 'w+')

        # Write the headers to the csv file
        self.__stats_file.write(
            'Config No,Measurements,Alarm arrivals,Control arrivals,Departures,Missed alarms,Missed controls,Collisions,'
            'Avg. alarm queue,Alarm queue delta,Avg. control queue,Control queue delta,Avg. alarm wait,Alarm wait delta,'
            'Avg. control wait,Control wait delta,Max alarm wait,Max control wait\n')

        self.__log_file.write(
            'Config No.,Alarm events,Control events,Avg. alarm wait,Avg. control wait,Max alarm wait,Max control wait\n')

        self.stats = {'config_no': 0, 'no_measurements': 0, 'no_alarm_arrivals': 0, 'no_control_arrivals': 0,
                      'no_departures': 0, 'no_missed_alarms': 0, 'no_missed_controls': 0, 'no_collisions': 0,
                      'avg_alarm_queue': 0, 'alarm_queue_delta': 0, 'avg_control_queue': 0, 'control_queue_delta': 0,
                      'avg_alarm_wait': 0, 'alarm_wait_delta': 0, 'avg_control_wait': 0, 'control_wait_delta': 0,
                      'max_alarm_wait': 0, 'max_control_wait': 0}

    def print_stats(self):
        """ Print the results to the terminal """

        print('Config: ' + str(self.stats['config_no']))
        print('Measurements: ' + str(self.stats['no_measurements']))
        print('Alarm arrivals: ' + str(self.stats['no_alarm_arrivals']))
        print('Control arrivals: ' + str(self.stats['no_control_arrivals']))
        print('Departures: ' + str(self.stats['no_departures']))
        print('Missed alarms: ' + str(self.stats['no_missed_alarms']))
        print('Missed controls: ' + str(self.stats['no_missed_controls']))
        print('Collisions: ' + str(self.stats['no_collisions']))
        print('Alarm queue: ' + str(self.stats['avg_alarm_queue']) + ' +- ' + str(self.stats['alarm_queue_delta']))
        print('Control queue: ' + str(self.stats['avg_control_queue']) + ' +- ' + str(
            self.stats['control_queue_delta']))
        print('Alarm wait if queue: ' + str(self.stats['avg_alarm_wait']) + ' +- ' + str(
            self.stats['alarm_wait_delta']))
        print('Control wait if queue: ' + str(self.stats['avg_control_wait']) + ' +- ' + str(
            self.stats['control_wait_delta']))
        print('Max alarm wait: ' + str(self.stats['max_alarm_wait']))
        print('Max control wait: ' + str(self.stats['max_control_wait']))

    def save_stats(self):
        """ Save the results to file """

        stats_str = ''

        for key in self.stats:
            stats_str += str(self.stats[key]) + ','

        stats_str = stats_str[:-1]
        stats_str += '\n'

        self.__stats_file.write(stats_str)

    def clear_stats(self):
        for key in self.stats:
            if not key == 'config_no':
                self.stats[key] = 0

    def process_results(self):
        """ Process the simulations results, calculating confidence 95% intervals for relevant parameters """

        self.__log_file.seek(0)

        # noinspection PyTypeChecker
        results = np.loadtxt(self.__log_file, delimiter=',', skiprows=1)

        alarm_queue = []
        control_queue = []
        alarm_wait = []
        control_wait = []
        max_alarm_wait = 0
        max_control_wait = 0

        for row in results:
            if row[0] == self.stats['config_no']:
                alarm_queue.append(row[1])
                control_queue.append(row[2])

                if not row[3] == 0:
                    alarm_wait.append(row[3])

                if not row[4] == 0:
                    control_wait.append(row[4])

                max_alarm_wait = max(max_alarm_wait, row[5])
                max_control_wait = max(max_control_wait, row[6])

        self.stats['avg_alarm_queue'], self.stats['alarm_queue_delta'] = self.__calc_confidence_interval(
            alarm_queue)
        self.stats['avg_control_queue'], self.stats['control_queue_delta'] = self.__calc_confidence_interval(
            control_queue)
        self.stats['avg_alarm_wait'], self.stats['alarm_wait_delta'] = self.__calc_confidence_interval(alarm_wait)
        self.stats['avg_control_wait'], self.stats['control_wait_delta'] = self.__calc_confidence_interval(
            control_wait)
        self.stats['max_alarm_wait'] = max_alarm_wait
        self.stats['max_control_wait'] = max_control_wait

    def close(self):
        """ Close stats and log file """

        self.__stats_file.close()
        self.__log_file.close()

    def write_log(self, message):
        """
        Write to the file

        Parameters
        ----------
        message : str
            Message to write to the file
        """

        self.__log_file.write(str(self.stats['config_no']) + ',' + message)

    @staticmethod
    def __calc_confidence_interval(v):
        # Calculate confidence interval

        if len(v) == 0:
            print('Empty vector')
            return -1, -1

        avg = np.mean(v)
        stddev = np.std(v)
        n = len(v)
        delta = 1.96 * (stddev / math.sqrt(n))
        return round(avg.item(), 2), round(delta.item(), 2)
