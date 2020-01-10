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

    parser = argparse.ArgumentParser()

    parser.add_argument('--variance_var', action="store", type=float, default=None)
    parser.add_argument('--period_var', action="store", type=float, default=None)
    parser.add_argument('--deadline_var', action="store", type=float, default=None)
    parser.add_argument('--ratio', action="store", type=float, default=None)
    parser.add_argument('--urllc_nodes', action="store", type=int, default=None)
    parser.add_argument('--mu', action="store", type=float, default=None)
    parser.add_argument('--seed', action="store", type=int, default=None)

    args = parser.parse_args()
    # print(args.scheduler)

    stats_file_path = 'stats/simulation_stats.csv'
    # Initialize stats and logger
    stats = Stats(stats_file_path, log= False)

    seed = args.seed
    mu = args.mu

    s1 = "FCFS"
    s2 = "FCFS"

    if args.ratio is not None:
        ratio = args.ratio

    if args.deadline_var is not None:
        deadline_var = args.deadline_var

    if args.period_var is not None:
        period_var = args.period_var

    if args.variance_var is not None:
        variance_var = args.variance_var

    np.random.seed(seed)

    no_urllc = args.urllc_nodes
    no_mmtc = 0

    trace_file_path = 'trace/' + 'Trace_' + str(args.period_var) + '_' + str(args.variance_var) + '-' + str(args.mu) + '_' + str(args.urllc_nodes) + '_' + str(round(time.time())) + '_event_trace.csv'

    trace = Trace(trace_file_path, log=True)
    simulation = Simulation(config, stats, trace, no_urllc, no_mmtc, mu, s1, s2, (ratio, period_var, deadline_var, variance_var), seed)

    simulation.run()
    stats.save_stats()

    # Close files
    stats.close()
    trace.close()

    simulation.write_result()
