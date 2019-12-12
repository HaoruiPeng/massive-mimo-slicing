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
        if self.log is True:
            try:
                self.__stats_file = open(stats_file_path, 'a')
            except FileNotFoundError:
                self.__stats_file = open(stats_file_path, 'w+')

        # Write the headers to the csv files

        self.stats = {'config_no': 0, 'no_urllc_arrivals': 0, 'no_mmtc_arrivals': 0,
                      'no_missed_urllc': 0, 'no_missed_mmtc': 0,
                      'no_pilots': 0, 'no_waste_pilots': 0}

    def print_stats(self):
        """ Print the results to the terminal """
        print('URLLC arrivals: ' + str(self.stats['no_urllc_arrivals']))
        print('mMTC arrivals: ' + str(self.stats['no_mmtc_arrivals']))
        print('Missed URLLC: ' + str(self.stats['no_missed_urllc']))
        print('Missed mMTC: ' + str(self.stats['no_missed_mmtc']))
        print('Total pilots: ' + str(self.stats['no_pilots']))
        print('Waste pilots: ' + str(self.stats['no_waste_pilots']))


    def save_stats(self):
        """ Save the results to file """
        if self.log is True:
            stats_str = ''

            for key in self.stats:
                stats_str += str(self.stats[key]) + ','

            stats_str = stats_str[:-1]
            stats_str += '\n'

            self.__stats_file.write(stats_str)
        else:
            pass
            

    def clear_stats(self):
        """ Clear the stats for the current simulation """

        for key in self.stats:
            if not key == 'config_no':
                self.stats[key] = 0

    def close(self):
        """ Close stats and log file """
        if self.log is True:
            self.__stats_file.close()
        else:
            pass
    

