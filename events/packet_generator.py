import numpy as np
import time


class PacketGenerator:
    """
        Generates event times given a certain distribution

        Attributes
        ----------
        distribution : str
            A specified and valid distribution. Currently supports:
                - Exponential
                - Constant
        settings : dict
            Dictionary of parameters for the specified distribution. Needed parameters are:
                - Exponential: mean_arrival_time (mean arrival time)
                - Constant: arrival_time (arrival time)

    """

    def __init__(self, distribution, settings):
        """
        Initializes a new event generator. See class documentation for parameters explanation.

        Parameters
        ----------
        distribution : str
            See class documentation
        settings : dict
            See class documentation
        """

        self.__distribution = distribution
        self.__settings = settings

        self.mapping = {
            'exponential': self.__exponential,
            'uniform': self.__uniform,
            'constant': self.__constant
        }

        self.init_mapping = {
            'exponential': self.__exponential,
            'uniform': self.__uniform,
            'constant': self.__constant_init
        }

        self.seed_counter = None

    def get_next(self):
        """
        Generates a new event time given specified distribution

        Returns
        -------
        float
            A float with the next event time
        """

        return self.mapping[self.__distribution]()

    def get_init(self):
        return self.init_mapping[self.__distribution]()

    def __exponential(self):
        # Returns float from an exponential distribution

        return np.random.exponential(self.__settings[0])

    def __uniform(self):
        # Return float from a uniform distribution

        return np.random.uniform(0, self.__settings.get('max_arrival_time'))

    def __constant(self):
        # Returns a float from a constant distribution with noise
        period = self.__settings[0]
        var_std = np.sqrt(abs(self.__settings[1]))
        # Case when has variance in the period
        if var_std > 0:
            return period + np.random.normal(0, var_std)
        else:
        # Deterministic case
            return period

    def __constant_init(self):
    # TODO: Maybe change the initial
        return abs(np.random.normal(6.5, 10))
