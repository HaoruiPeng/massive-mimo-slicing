import numpy as np


# Packet generator class for different distributions
class EventGenerator:
    def __init__(self, distribution, settings):
        self.distribution = distribution
        self.settings = settings

        self.mapping = {
            'exponential': self.exponential(),
            'deterministic': self.deterministic()
        }

    def get_next(self):
        return self.mapping[self.distribution]

    # Poisson process
    def exponential(self):
        return np.random.exponential(self.settings.get('mean_time'))

    # Deterministic process
    def deterministic(self):
        return self.settings.get('mean_time')
