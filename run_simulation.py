import os
import numpy as np
from multiprocessing import Pool
import json
import time

PROCESSES = 4


simulations = []


mu = 2.26

SEED = round(time.time() / 10)

s2 = "FCFS"
s1 = "FCFS"

period_vars = np.linspace(0.01, 0.15, 15)
variance_vars = np.linspace(0.05, 0.5, 15)

no_urllc_list = [60, 90, 150]

for no_urllc in no_urllc_list:
    for period_var in period_vars:
        for variance_var in variance_vars:
            SEED += np.random.randint(100)
            simulations.append("python3 main.py  --period_var {} --variance_var {} \
                                --urllc_node {} \
                                --mu {} --seed {}".format(period_var, variance_var, no_urllc, mu, SEED))


pool = Pool(processes=PROCESSES)
for k, simulation in enumerate(simulations):
    pool.apply_async(os.system, (simulation,))

pool.close()
pool.join()
print("All simulations completed!")
