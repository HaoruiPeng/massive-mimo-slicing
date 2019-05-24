"""
Massive MIMO factory simulation

This library provides a network simulator for a factory floor with a number of machines with control traffic and a
number of alarm nodes with alarm traffic. The library is built to be highly configurable.
"""

import json
import time
import numpy as np

from utilities.stats import Stats
from huffman.huffman_simulation import HuffmanSimulation as Simulation
from huffman.huffman_tree import HuffmanTree
from huffman.huffman_node import HuffmanNode

__author__ = "Jon Stålhammar, Christian Lejdström, Emma Fitzgerald"

if __name__ == '__main__':
    # Load simulation parameters
    with open('../default_config.json') as config_file:
        config = json.load(config_file)

    time_string = time.strftime('%Y%m%d_%H%M%S')
    simulation_name = config.get('simulation_name')

    log_file_path = '../logs/' + time_string + '_' + simulation_name + '_queue_log.csv'
    stats_file_path = '../stats/' + time_string + '_' + simulation_name + '_stats.csv'

    # Initialize stats and logger
    stats = Stats(stats_file_path, log_file_path)

    # Only use multi run
    if config.get("multi_run"):
        stopping_criteria = 0
        iteration = 1

        while stats.stats['no_missed_alarms'] == stopping_criteria:
            stats.clear_stats()

            print('{} alarm nodes'.format(config.get('no_alarm_nodes')))

            # Generate random alarm probabilities
            seed = int(time.time())
            np.random.seed(seed)
            seed += 1
            alarm_node_probabilities = np.random.rand(config.get('no_alarm_nodes'), 1) * 0.5

            # Change to per frame probabilities
            alarm_node_probabilities = alarm_node_probabilities / (
                    config.get('simulation_length') * 1000 / config.get('frame_length'))

            # Generate pilot sequences based on huffman tree
            huffman_tree = HuffmanTree(alarm_node_probabilities)
            alarm_node_pilot_sequences = huffman_tree.pilot_sequences

            huffman_alarm_arrivals = []

            # Create Huffman nodes
            for i in range(len(alarm_node_probabilities)):
                huffman_alarm_arrivals.append(
                    HuffmanNode(i, alarm_node_probabilities[i], alarm_node_pilot_sequences[i]))

            # Update the run configuration number, should start with zero
            stats.stats['config_no'] = iteration - 1

            # Set new config parameters here by overriding the config file
            # e.g. config['max_attempts'] =R 2*(i+1)
            config['no_alarm_nodes'] = iteration * 500

            # Run the simulation with new parameters
            simulation = Simulation(config, stats, huffman_alarm_arrivals, seed=seed)
            simulation.run()

            print('Seed: {}'.format(simulation.base_seed))

            # Process, save and print the results
            stats.process_results()
            stats.save_stats()
            stats.print_stats()
            iteration += 1

    # Close files
    stats.close()
