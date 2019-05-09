"""
Massive MIMO factory simulation

This library provides a network simulator for a factory floor with a number of machines with control traffic and a
number of alarm nodes with alarm traffic. The library is built to be highly configurable.
"""

import json
import time

from stats import Stats
from logger import Logger
from simulation import Simulation

__author__ = "Jon Stålhammar, Christian Lejdström, Emma Fitzgerald"

if __name__ == '__main__':
    # Load simulation parameters
    with open('default_config.json') as f:
        config = json.load(f)

    time_string = time.strftime('%Y%m%d_%H%M%S')
    simulation_name = config.get('simulation_name')

    # Initialize a new logger
    log_file_path = 'logs/' + time_string + '_' + simulation_name + '_queue_log.csv'
    logger = Logger(log_file_path)

    # Initialize a new statistics object
    stats_file_path = 'stats/' + simulation_name + '_stats.csv'
    stats = Stats(stats_file_path)

    # Run the simulation
    simulation = Simulation(config, logger, stats)
    simulation.run()

    # Close files and save results
    logger.close()
    stats.print()
    stats.save_and_close()
