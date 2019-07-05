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

        # Write the headers to the csv files
        self.__stats_file.write(
            'Config No,Measurements,URLLC arrivals,mMTC arrivals,Departures,'
            'Missed URLLC,Missed mMTC,Collisions,'
            'Avg. URLLC queue,URLLC queue delta,'
            'Avg. mMTC queue,mMTC queue delta,'
            'Avg. URLLC wait,URLLC wait delta,'
            'Avg. mMTC wait,mMTC wait delta,'
            'Max URLLC wait,Max mMTC wait\n')

        self.__log_file.write(
            'Config No.,URLLC events,mMTC events,'
            'Avg. URLLC wait,Avg. mMTC wait,'
            'Max URLLC wait,Max mMTC wait\n')

        self.stats = {'config_no': 0, 'no_measurements': 0, 'no_urllc_arrivals': 0, 'no_mmtc_arrivals': 0,
                      'no_departures': 0, 'no_missed_urllc': 0, 'no_missed_mmtc': 0, 'no_collisions': 0,
                      'avg_urllc_queue': 0, 'urllc_queue_delta': 0, 'avg_mmtc_queue': 0, 'mmtc_queue_delta': 0,
                      'avg_urllc_wait': 0, 'urllc_wait_delta': 0, 'avg_mmtc_wait': 0, 'mmtc_wait_delta': 0,
                      'max_urllc_wait': 0, 'max_mmtc_wait': 0}

    def print_stats(self):
        """ Print the results to the terminal """

        print('Config: ' + str(self.stats['config_no']))
        print('Measurements: ' + str(self.stats['no_measurements']))
        print('URLLC arrivals: ' + str(self.stats['no_urllc_arrivals']))
        print('mMTC arrivals: ' + str(self.stats['no_mmtc_arrivals']))
        print('Departures: ' + str(self.stats['no_departures']))
        print('Missed URLLC: ' + str(self.stats['no_missed_urllc']))
        print('Missed mMTC: ' + str(self.stats['no_missed_mmtc']))
        print('Collisions: ' + str(self.stats['no_collisions']))
        print('URLLC queue: ' + str(self.stats['avg_urllc_queue']) + ' +- ' + str(self.stats['urllc_queue_delta']))
        print('mMTC queue: ' + str(self.stats['avg_mmtc_queue']) + ' +- ' + str(
            self.stats['mmtc_queue_delta']))
        print('URLLC wait if queue: ' + str(self.stats['avg_urllc_wait']) + ' +- ' + str(
            self.stats['urllc_wait_delta']))
        print('mMTC wait if queue: ' + str(self.stats['avg_mmtc_wait']) + ' +- ' + str(
            self.stats['mmtc_wait_delta']))
        print('Max URLLC wait: ' + str(self.stats['max_urllc_wait']))
        print('Max mMTC wait: ' + str(self.stats['max_mmtc_wait']))

    def save_stats(self):
        """ Save the results to file """

        stats_str = ''

        for key in self.stats:
            stats_str += str(self.stats[key]) + ','

        stats_str = stats_str[:-1]
        stats_str += '\n'

        self.__stats_file.write(stats_str)

    def clear_stats(self):
        """ Clear the stats for the current simulation """

        for key in self.stats:
            if not key == 'config_no':
                self.stats[key] = 0

    def process_results(self):
        """ Process the simulations results, calculating 95% confidence intervals for relevant parameters """

        self.__log_file.seek(0)

        # noinspection PyTypeChecker
        results = np.loadtxt(self.__log_file, delimiter=',', skiprows=1)

        urllc_queue = []
        mmtc_queue = []
        urllc_wait = []
        mmtc_wait = []
        max_urllc_wait = 0
        max_mmtc_wait = 0

        for row in results:
            if row[0] == self.stats['config_no']:
                urllc_queue.append(row[1])
                mmtc_queue.append(row[2])

                if not row[3] == 0:
                    urllc_wait.append(row[3])

                if not row[4] == 0:
                    mmtc_wait.append(row[4])

                max_urllc_wait = max(max_urllc_wait, row[5])
                max_mmtc_wait = max(max_mmtc_wait, row[6])

        self.stats['avg_urllc_queue'], self.stats['urllc_queue_delta'] = self.__calc_confidence_interval(
            urllc_queue)
        self.stats['avg_mmtc_queue'], self.stats['mmtc_queue_delta'] = self.__calc_confidence_interval(
            mmtc_queue)
        self.stats['avg_urllc_wait'], self.stats['urllc_wait_delta'] = self.__calc_confidence_interval(urllc_wait)
        self.stats['avg_control_wait'], self.stats['control_wait_delta'] = self.__calc_confidence_interval(
            mmtc_wait)
        self.stats['max_urllc_wait'] = max_urllc_wait
        self.stats['max_mmtc_wait'] = max_mmtc_wait

    def close(self):
        """ Close stats and log file """

        self.__stats_file.close()
        self.__log_file.close()

    def write_log(self, message):
        """
        Write to the log file (used for queue stats)

        Parameters
        ----------
        message : str
            Message to write to the file
        """

        self.__log_file.write(message)

    @staticmethod
    def __calc_confidence_interval(v):
        # Calculate 95% confidence interval

        if len(v) == 0:
            print('Empty vector')
            return -1, -1

        avg = np.mean(v)
        stddev = np.std(v)
        n = len(v)
        delta = 1.96 * (stddev / math.sqrt(n))
        return round(avg.item(), 2), round(delta.item(), 2)

