"""
Massive MIMO Network slicing on MAC layer simulation

"""

import json
import time
import sys
import os
import numpy as np
from flask import request
from utilities.stats import Stats
from utilities.trace import Trace
from simulation import Simulation

# sys.path.append(os.path.abspath('../'))


def main():
    # Load simulation parameters
    keys = ["urllc_nodes","seed", "mu", "ratio" ,"period_var", "deadline_var", "variance_var"]

    data = request.get_json(force=True)
    if data is None:
        return "Bad Request"
    else:
        pass

    no_urllc = int(data["urllc_nodes"])
    no_mmtc = 0
    seed = int(data["seed"])
    mu = float(data["mu"])
    ratio = float(data["ratio"])
    period_var = float(data["period_var"])
    deadline_var = float(data["deadline_var"])
    variance_var = float(data["variance_var"])
    report_sampling = 0.5

    stats = Stats()
    trace = Trace()

    np.random.seed(seed)

    s1 = "FCFS"
    s2 = "FCFS"

    simulation = Simulation(report_sampling, stats, trace, no_urllc, no_mmtc, mu, s1, s2, (ratio, period_var, deadline_var, variance_var), seed)

    results = simulation.run()
    results_js = json.dumps(results).encode()

    # results_js = json.dumps(data).encode()

    return results_js
