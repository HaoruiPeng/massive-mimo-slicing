"""
Massive MIMO factory simulation

This library provides a network simulator for a factory floor with a number of machines with control traffic and a
number of alarm nodes with alarm traffic. The library is built to be highly configurable.
"""

import json
import time

from stats import Stats
from simulation import Simulation

__author__ = "Jon Stålhammar, Christian Lejdström, Emma Fitzgerald"

if __name__ == '__main__':
    # Load simulation parameters
    with open('default_config.json') as config_file:
        config = json.load(config_file)

    time_string = time.strftime('%Y%m%d_%H%M%S')
    simulation_name = config.get('simulation_name')

    log_file_path = 'logs/' + time_string + '_' + simulation_name + '_queue_log.csv'
    stats_file_path = 'stats/' + time_string + '_' + simulation_name + '_stats.csv'

    # Initialize stats
    stats = Stats(stats_file_path, log_file_path)

    # Override the default config and run multiple simulations
    if not config.get("use_default_config"):
        configurations = 10

        for i in range(configurations):
            # Update the run configuration number, should start with zero
            stats.stats['config_no'] = i

            # Set new config parameters here

            # Run the simulation with new parameters
            simulation = Simulation(config, stats)
            simulation.run()

            # Process, save and print the results
            stats.process_results()
            stats.save_stats()
            stats.print_stats()
            stats.clear_stats()

    else:
        # Run a single simulation with default parameters
        simulation = Simulation(config, stats)
        simulation.run()
        stats.process_results()
        stats.save_stats()
        stats.print_stats()

    # Close files
    stats.close()
