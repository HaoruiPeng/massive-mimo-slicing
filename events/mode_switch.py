import numpy as np
import time


class ModeSwitch:
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
    _OFF = 0
    _ON = 1

    def __init__(self, init_mode, d_on, d_off):
        """
        Initializes a new event generator. See class documentation for parameters explanation.

        Parameters
        ----------
        cuurent_mode : str
            See class documentation
        alpha : [1, 2], the smaller alpha, the larger bursts
        d: minimum period
        distribution: pareto or constant
        """
        self.alpha = 1.5
        self.d_on = d_on
        self.d_off = d_off
        self.init_mode = init_mode
        self.distribution = "constant"

    def get_next(self, current_mode):
        """
        Generates a new event time given specified distribution

        Returns
        -------
        time of firt turn on, next_mode

        """
        if current_mode == self._OFF:
            d = self.d_off
        if current_mode == self._ON:
            d = self.d_on

        if self.distribution == "pareto":
            s = (np.random.pareto(self.alpha, 1) + 1) * d
        if self.distribution == "constant":
            s = [d]
        return s[0], 1 - current_mode

    def get_init(self):
        """
        The init mode is always off, get the time when first turn on

        Returns
        -------
        time of firt turn on, mode_on
        """
        s = (np.random.pareto(self.alpha - 0.5, 1) + 1) * self.d_off
        return s[0], self._ON
