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
    parser.add_argument('--variance_var', action="store", type=float, default=None)
    parser.add_argument('--period_var', action="store", type=float, default=None)
    parser.add_argument('--urllc_nodes', action="store", type=int, default=None)
    parser.add_argument('--mmtc_nodes', action="store", type=int, default=None)
    parser.add_argument('--mu', action="store", type=float, default=None)
    parser.add_argument('--seed', action="store", type=int, default=None)

    args = parser.parse_args()
    # print(args.scheduler)

    stats_file_path = 'stats/simulation_stats.csv'
    # Initialize stats and logger
    stats = Stats(stats_file_path, log= False)
    
    seed = int(args.seed)
    mu = float(args.mu)
    
    period_var = float(args.period_var)
    variance_var = float(args.variance_var)
    
    if seed is None:
        seed = round(time.time() / 10)

    np.random.seed(seed)

    no_urllc = int(args.urllc_nodes)
    no_mmtc = 0
    sampling=no_urllc

    while True:
        if isprime(sampling):
            break
        else:
            sampling += 1
    
    # print(sampling)
    trace_file_path = 'trace/' + 'Trace_' + str(args.period_var) + '_' + str(args.variance_var) + '-' + str(args.mu) + '_' + str(args.urllc_nodes) + '_' + str(round(time.time())) + '_event_trace.csv'
    
    trace = Trace(trace_file_path, sampling, log=True)
    simulation = Simulation(config, stats, trace, no_urllc, no_mmtc, mu, args.s1, args.s2, (period_var, variance_var), seed)
    
    simulation.run()
    stats.save_stats()

    # Close files
    stats.close()
    trace.close()

    trace.process()
    simulation.write_result()
