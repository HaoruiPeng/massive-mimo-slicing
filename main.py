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

    parser.add_argument('--variance', action="store", type=float, default=None)
    parser.add_argument('--period', action="store", type=float, default=None)
    parser.add_argument('--d_on', action="store", type=float, default=None)
    parser.add_argument('--d_off', action="store", type=float, default=None)
    parser.add_argument('--no_periodic', action="store", type=int, default=None)
    parser.add_argument('--no_file', action="store", type=int, default=None)
    parser.add_argument('--seed', action="store", type=int, default=None)
    parser.add_argument('--mu', action="store", type=float, default=None)


    args = parser.parse_args()
    # print(args.scheduler)

    stats_file_path = 'stats/simulation_stats.csv'
    # Initialize stats and logger
    stats = Stats(stats_file_path, log= False)

    seed = args.seed
    mu = args.mu
    inner_periods = args.period
    inner_variance = args.variance
    t_on = args.d_on
    t_off = args.d_off

    np.random.seed(seed)

    no_file = args.no_file
    no_periodic = args.no_periodic

    trace_file_path = 'trace/' + 'Trace_' + str(inner_periods) + '_' + str(inner_variance) + '-' + str(no_file) + '_' + str(no_periodic) + '_' + str(round(time.time())) + '_event_trace.csv'

    trace = Trace(trace_file_path, log=True)
    simulation = Simulation(config, stats, trace, no_file, no_periodic, mu, (inner_periods, inner_variance, t_on, t_off), periodic_traffic=None, seed=seed)

    simulation.run()
    stats.save_stats()

    # Close files
    stats.close()
    trace.close()

    simulation.write_result()
