"""
Massive MIMO factory simulation

This library provides a network simulator for a factory floor with a number of machines with control traffic and a
number of alarm nodes with alarm traffic. The library is built to be highly configurable.
"""

import json
import time
import sys
import os
from utilities.stats import Stats
from utilities.trace import Trace
from simulation import Simulation
sys.path.append(os.path.abspath('../'))

__author__ = "Jon Stålhammar, Christian Lejdström, Emma Fitzgerald"

if __name__ == '__main__':
    # Load simulation parameters
    with open('default_config.json') as config_file:
        config = json.load(config_file)

    time_string = time.strftime('%Y%m%d_%H%M%S')
    simulation_name = config.get('simulation_name')

    log_file_path = 'logs/' + time_string + '_' + simulation_name + '_queue_log.csv'
    stats_file_path = 'stats/' + time_string + '_' + simulation_name + '_stats.csv'
    trace_file_path = 'trace/' + time_string + '_' + simulation_name + '_event_trace.csv'
    # Initialize stats and logger
    stats = Stats(stats_file_path, log_file_path)
    trace = Trace(trace_file_path)

    # Run a single simulation with default parameters
    simulation = Simulation(config, stats, trace)
    simulation.run()
    # stats.process_results()
    # stats.save_stats()
    # stats.print_stats()

    # Close files
    stats.close()
    trace.close()
    trace.process()
    simulation.write_result()
    # trace.write_trace()
