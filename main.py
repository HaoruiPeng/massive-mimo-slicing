"""
Massive MIMO Network slicing on MAC layer simulation

"""

import json
import time
import sys
import os
import numpy as np
from utilities.stats import Stats
from utilities.trace import Trace
from simulation import Simulation
import argparse
sys.path.append(os.path.abspath('../'))

if __name__ == '__main__':
    # Load simulation parameters
    with open('default_config.json') as config_file:
        config = json.load(config_file)

    time_string = time.strftime('%Y%m%d_%H%M%S')
    simulation_name = config.get('simulation_name')

    parser = argparse.ArgumentParser()
    parser.add_argument('--scheduler', action="store", default=None)
    parser.add_argument('--reliability', action="store", default=None)
    parser.add_argument('--deadline', action="store", default=None)

    args = parser.parse_args()

    log_file_path = 'logs/seed_log.csv'
    stats_file_path = 'stats/simulation_stats.csv'
    trace_file_path = 'trace/' + time_string + '_' + simulation_name + '_event_trace.csv'
    # Initialize stats and logger
    stats = Stats(stats_file_path)
    trace = Trace(trace_file_path)

    seed = round(time.time())
    try:
        file = open(log_file_path, 'a')
        file.write(str(seed) + '\n')
    except FileNotFoundError:
        print("No log file found, create the file first")
        file = open(log_file_path, 'w+')

    np.random.seed(seed)
    # Run a single simulation with default parameters
    if args.scheduler is not None:
        if args.reliability is not None and args.deadline is not None:
            simulation = Simulation(config, stats, trace, args.scheduler, (args.reliability, args.deadline))
        else:
            simulation = Simulation(config, stats, trace, args.scheduler)
    else:
        simulation = Simulation(config, stats, trace)

    simulation.run()
    stats.save_stats()
    # Close files
    stats.close()
    trace.close()

    trace.process()
    simulation.write_result()
    # trace.write_trace()
