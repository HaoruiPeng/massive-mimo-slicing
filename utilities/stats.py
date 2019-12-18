class Stats:
    """
    Statistics object to keep track of simulation measurements

    Methods
    -------

    """

    def __init__(self):
        """
        Initialize a new statistics and logging object
        """

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


    def clear_stats(self):
        """ Clear the stats for the current simulation """
        for key in self.stats:
            if not key == 'config_no':
                self.stats[key] = 0
