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

    try:
        assert args.urllc_nodes is None or args.mmtc_nodes is None
    except AssertionError as msg:
        print(msg)

    total_pilots = config.get("no_pilots")
    slot_time = config.get("frame_length")
    mmtc_period = 50
    mmtc_pilot = 1
    period = {"long": 10,
              "short": 1}
    pilots = {"high": 3,
              "low": 1}
    urllc_period = period[args.deadline]
    urllc_pilot = pilots[args.reliability]

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

    if args.urllc_nodes is None and args.mmtc_nodes is None:
        with open('slices/slice_config.json') as config_file:
            node = json.load(config_file)
        no_urllc_list = [node.get("no_urllc_nodes")]
        no_mmtc_list = [node.get("no_mmtc_nodes")]
    elif args.urllc_nodes is not None:
        no_urllc_list = [args.urllc_nodes]
        rho2_list = np.linspace(0.1, 1.5, 15)
        no_mmtc_list = [round(rho * total_pilots * mmtc_period / (mmtc_pilot * slot_time)) for rho in rho2_list]
    elif args.mmtc_nodes is not None:
        no_mmtc_list = [args.mmtc_nodes]
        rho1_list = np.linspace(0.1, 1., 10)
        no_urllc_list = [round(rho * total_pilots * urllc_period / (urllc_pilot * slot_time)) for rho in rho1_list]

    for no_urllc in no_urllc_list:
        for no_mmtc in no_mmtc_list:
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
