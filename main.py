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

with open('default_config.json') as config_file:
    config = json.load(config_file)

if __name__ == '__main__':
    # Load simulation parameters
    time_string = time.strftime('%Y%m%d_%H%M%S')
    simulation_name = config.get('simulation_name')

    parser = argparse.ArgumentParser()
    parser.add_argument('--scheduler', action="store", default=None)
    parser.add_argument('--reliability', action="store", default=None)
    parser.add_argument('--deadline', action="store", default=None)
    parser.add_argument('--urllc_nodes', action="store", default=None)
    parser.add_argument('--mmtc_nodes', action="store", default=None)

    args = parser.parse_args()
    # print(args.scheduler)

    log_file_path = 'logs/seed_log.csv'
    stats_file_path = 'stats/simulation_stats.csv'
    trace_file_path = 'trace/' + time_string + '_' + simulation_name + '_event_trace.csv'
    # Initialize stats and logger
    stats = Stats(stats_file_path)
    trace = Trace(trace_file_path)

    seed = round(time.time())
    try:
        file = open(log_file_path, 'a')
    except FileNotFoundError:
        print("No log file found, create the file first")
        file = open(log_file_path, 'w+')

    np.random.seed(seed)

    if args.urllc_nodes is None:
        with open('slices/slice_config.json') as config_file:
            node = json.load(config_file)
        no_urllc = [node.get("no_urllc_nodes")]
    else:
        no_urllc = args.urllc_nodes

    if args.mmtc_nodes is None:
        with open('slices/slice_config.json') as config_file:
            node = json.load(config_file)
        no_mmtc = [node.get("no_mmtc_nodes")]
    else:
        no_mmtc = args.mmtc_nodes

    print(no_urllc, no_mmtc)

    if args.scheduler is not None:
        if args.reliability is not None and args.deadline is not None:
            simulation = Simulation(config, stats, trace, no_urllc, no_mmtc,
                                    args.scheduler,
                                    (args.reliability, args.deadline))
            file.write(args.scheduler + ',' + args.reliability + ',' + args.deadline + ','
                       + str(no_urllc) + ',' + str(no_mmtc) + ',' + str(seed) + '\n')
        else:
            simulation = Simulation(config, stats, trace,  no_urllc, no_mmtc,
                                    args.scheduler)
            file.write(args.scheduler + ',' + str(no_urllc) + ',' + str(no_mmtc) + ',' + str(seed) + '\n')
    else:
        simulation = Simulation(config, stats, trace, no_urllc, no_mmtc)
        file.write(str(no_urllc) + ',' + str(no_mmtc) + ',' + str(seed) + '\n')

    simulation.run()
    stats.save_stats()

    # Close files
    stats.close()
    trace.close()

    trace.process()
    simulation.write_result()
