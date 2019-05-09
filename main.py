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

    # Initialize stats and logger
    stats = Stats(stats_file_path, log_file_path)

    custom_alarm_arrivals = None
    custom_control_arrivals = None

    # Declare custom arrival distributions
    # Length of the array need to match the number of nodes
    # Format of each should be dictionary with following keys, e.g.:
    # Note, below blocks can also be added in the multi_run loop
    # {
    #   'distribution': 'exponential',
    #   'settings': { 'mean_arrival_time': 1000 }
    #   'max_attempts': 10
    # }

    if config['custom_alarm_arrivals']:
        custom_alarm_arrivals = []

        # Just replicated what's in the config file
        for i in range(config.get('no_alarm_nodes')):
            entry = {'distribution': 'exponential', 'settings': {'mean_arrival_time': 1000}, 'max_attempts': 10}
            custom_alarm_arrivals.append(entry)

    if config['custom_control_arrivals']:
        custom_control_arrivals = []

        # Just replicating what's in the config file
        for i in range(config.get('no_control_nodes')):
            entry = {'distribution': 'exponential', 'settings': {'mean_arrival_time': 5}, 'max_attempts': 10}
            custom_control_arrivals.append(entry)

    # Override the default config and run multiple simulations
    if config.get("multi_run"):
        configurations = 10

        for i in range(configurations):
            # Update the run configuration number, should start with zero
            stats.stats['config_no'] = i

            # Set new config parameters here by overriding the config file
            # e.g. config['max_attempts'] = 2*(i+1)
            config['max_attempts'] = 10

            # Run the simulation with new parameters
            simulation = Simulation(config, stats, custom_alarm_arrivals, custom_control_arrivals)
            simulation.run()

            # Process, save and print the results
            stats.process_results()
            stats.save_stats()
            stats.print_stats()
            stats.clear_stats()  # remove this if aggregated base stats is needed

    else:
        # Run a single simulation with default parameters
        simulation = Simulation(config, stats, custom_alarm_arrivals, custom_control_arrivals)
        simulation.run()
        stats.process_results()
        stats.save_stats()
        stats.print_stats()

    # Close files
    stats.close()
