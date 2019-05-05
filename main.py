import json
import time

from stats import Stats
from logger import Logger
from simulation import Simulation

if __name__ == '__main__':
    with open('config.json') as f:
        config = json.load(f)

    time_string = time.strftime('%Y%m%d_%H%M%S')
    file_name = 'logs/' + time_string + '_mimo_simulation.csv'
    logger = Logger(file_name)

    stats = Stats()

    simulation = Simulation(config, logger, stats)
    simulation.run()

    stats.print()
    logger.close()