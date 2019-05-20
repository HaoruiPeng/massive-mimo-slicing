"""
Massive MIMO factory simulation

This library provides a network simulator for a factory floor with a number of machines with control traffic and a
number of alarm nodes with alarm traffic. The library is built to be highly configurable.
"""

import json
import time
import numpy as np

from stats import Stats
from huffman.huffman_simulation import Simulation

__author__ = "Jon Stålhammar, Christian Lejdström, Emma Fitzgerald"

if __name__ == '__main__':
    # Load simulation parameters
    with open('default_config.json') as config_file:
        config = json.load(config_file)

    time_string = time.strftime('%Y%m%d_%H%M%S')
    simulation_name = config.get('simulation_name')

    log_file_path = 'logs/' + time_string + '_' + simulation_name + '_queue_log.csv'
    stats_file_path = 'stats/' + time_string + '_' + simulation_name + '_stats.csv'

    # Initialize stats and logger
    stats = Stats(stats_file_path, log_file_path)

    # Override the default config and run multiple simulations
    if config.get("multi_run"):
        stopping_criteria = 10
        base_no_nodes = config.get('no_control_nodes')
        i = 1

        while i < stopping_criteria:
            stats.clear_stats()

            # Update the run configuration number, should start with zero
            stats.stats['config_no'] = i - 1

            # Set new config parameters here by overriding the config file
            # e.g. config['max_attempts'] = 2*(i+1)

            # Run the simulation with new parameters
            simulation = Simulation(config, stats)
            simulation.run()

            print('Seed: {}'.format(simulation.base_seed))

            # Process, save and print the results
            stats.process_results()
            stats.save_stats()
            stats.print_stats()
            i += 1
    else:
        # Run a single simulation with default parameters
        simulation = Simulation(config, stats)
        simulation.run()
        stats.process_results()
        stats.save_stats()
        stats.print_stats()

    # Close files
    stats.close()
