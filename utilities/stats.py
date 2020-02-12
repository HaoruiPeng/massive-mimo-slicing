import csv

class Stats:
    """
    Statistics object to keep track of simulation measurements

    Methods
    -------

    """

    def __init__(self, stats_file_path, log=False):
        """
        Initialize a new statistics and logging object

        Parameters
        ----------
        stats_file_path : str
            Path to stats file
        log_file_path : str
            Path to logging file
        """

        self.log = log
        headers = ['no_arrivals', 'no_missed',
                   'no_pilots', 'no_waste_pilots']
        self.stats = dict((key, 0) for key in headers)
        self.writer =  None

        if self.log is True:
            try:
                self.__stats_file = open(stats_file_path, 'a')
            except FileNotFoundError:
                self.__stats_file = open(stats_file_path, 'w+')

            # Write the headers to the csv files
            self.writer = csv.DictWriter(self.__stats_file, fieldnames=headers)
            self.writer.writeheader()


    def save_stats(self):
        if self.log is True:
            self.writer.writerow(self.stats)

    def clear_stats(self):
        """ Clear the stats for the current simulation """

        for key in self.stats:
            self.stats[key] = 0

    def close(self):
        """ Close stats and log file """
        if self.log is True:
            self.__stats_file.close()
        else:
            pass
