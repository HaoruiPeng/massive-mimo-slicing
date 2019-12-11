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


def isprime(N):
    if N<=1 or N==4:
        return False
    else:
        for i in range(2, N//2):
            if N%i == 0:
                return False
        return True


if __name__ == '__main__':
    # Load simulation parameters
    time_string = time.strftime('%Y%m%d_%H%M%S')
    simulation_name = config.get('simulation_name')

    parser = argparse.ArgumentParser()
    parser.add_argument('--s1', action="store", default=None)
    parser.add_argument('--s2', action="store", default=None)
    parser.add_argument('--variance_var', action="store", default=None)
    parser.add_argument('--period_var', action="store", default=None)
    parser.add_argument('--urllc_nodes', action="store", type=int, default=None)
    parser.add_argument('--mmtc_nodes', action="store", type=int, default=None)
    parser.add_argument('--mu', action="store", type=float, default=None)
    parser.add_argument('--seed', action="store", type=int, default=1)

    args = parser.parse_args()
    # print(args.scheduler)

    log_file_path = 'logs/seed_log.csv'
    stats_file_path = 'stats/simulation_stats.csv'
    # Initialize stats and logger
    stats = Stats(stats_file_path)
    seed = args.seed
    mu = float(args.mu)
    
    period_var = float(args.period_var)
    variance_var = float(args.variance_var)
    
    try:
        file = open(log_file_path, 'a')
    except FileNotFoundError:
        print("No log file found, create the file first")
        file = open(log_file_path, 'w+')

    np.random.seed(seed)

    if args.urllc_nodes is None:
        with open('slices/slice_config.json') as config_file:
            node = json.load(config_file)
        no_urllc = node.get("no_urllc_nodes")
    else:
        no_urllc = args.urllc_nodes

    if args.mmtc_nodes is None:
        with open('slices/slice_config.json') as config_file:
            node = json.load(config_file)
        no_mmtc = node.get("no_mmtc_nodes")
    else:
        no_mmtc = args.mmtc_nodes
        
    sampling=no_urllc

    while True:
        if isprime(sampling):
            break
        else:
            sampling += 1
    
    # print(sampling)
    trace_file_path = 'trace/' + args.period_var + '_' + args.variance_var + '-' + args.s1 + '_' +args.s2 + '_' +str(no_urllc) + '_' + str(no_mmtc) + '_' + str(round(time.time())) + '_event_trace.csv'
    trace = Trace(trace_file_path, sampling, log=True)

    if args.s1 is not None:
        if args.period_var is not None and args.variance_var is not None:
            simulation = Simulation(config, stats, trace, no_urllc, no_mmtc, mu,
                                    args.s1, args.s2,
                                    (period_var, variance_var))
            file.write(args.s1 + '-' + args.s2 + ',' + args.period_var + ',' + args.variance_var + ','
                       + str(no_urllc) + ',' + str(no_mmtc) + ',' + str(seed) + '\n')
        else:
            simulation = Simulation(config, stats, trace,  no_urllc, no_mmtc, mu,
                                    args.s1, args.s2)
            file.write(args.s1 + '-' + args.s2 + ',' + str(no_urllc) + ',' + str(no_mmtc) + ',' + str(seed) + '\n')
    else:
        simulation = Simulation(config, stats, trace, no_urllc, no_mmtc, mu)
        file.write(str(no_urllc) + ',' + str(no_mmtc) + ',' + str(seed) + '\n')

    simulation.run()
    stats.save_stats()

    # Close files
    stats.close()
    trace.close()

    trace.process()
    simulation.write_result()
