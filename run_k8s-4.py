import os
import numpy as np
from multiprocessing import Pool
import json
import time

PROCESSES = 4

with open('default_config.json') as config_file:
    config = json.load(config_file)

total_pilots = config.get("no_pilots")
slot_time = config.get("frame_length")

mmtc_period = 50
mmtc_pilot = 1

period = {"long": 10,
          "short": 1}
pilots = {"high": 3,
          "low": 1}

reliability = "high"
deadline = "short"

urllc_period = period[deadline]
urllc_pilot = pilots[reliability]

SEED = round(time.time() / 10)

simulations = []


def rho2urllc(rho, period, pilot):
    urllc = rho * total_pilots * period / (pilot * slot_time)
    return int(round(urllc))


def rho2mmtc(rho):
    mmtc = rho * total_pilots * mmtc_period / (mmtc_pilot * slot_time)
    return int(round(mmtc))


urllc_load = 0.5
# no_urllc = rho2urllc(urllc_load, urllc_period, urllc_pilot)
# mmtc_loads = np.linspace(0.1, 1.5, 15)
# no_mmtc_list = [rho2mmtc(rho) for rho in mmtc_loads]

# mmtc_load = 0.5
# no_mmtc = rho2mmtc(mmtc_load)
# urllc_loads = np.linspace(0.05, 1.05, 21)
# no_urllc_list = [rho2urllc(rho, urllc_period, urllc_pilot) for rho in urllc_loads]
# no_urllc_list = list(set(no_urllc_list))  # remove duplicates

s2 = "FCFS"

# s1 = "FCFS"
# for no_mmtc in no_mmtc_list:
#     SEED += np.random.randint(100)
#     simulations.append("python3 main.py \
#                         --s1 {} --s2 {} --reliability {} --deadline {} \
#                         --urllc_node {} --mmtc_node {} \
#                         --seed {}".format(
#         s1, s2 , reliability, deadline, no_urllc, no_mmtc, SEED))
#
# s1 = "RR_Q"
# for no_mmtc in no_mmtc_list:
#     SEED += np.random.randint(100)
#     simulations.append("python3 main.py \
#                         --s1 {} --s2 {} --reliability {} --deadline {} \
#                         --urllc_node {} --mmtc_node {} \
#                         --seed {}".format(
#         s1, s2, reliability, deadline, no_urllc, no_mmtc, SEED))
#
# s1 = "RR_NQ"
# for no_mmtc in no_mmtc_list:
#     SEED += np.random.randint(100)
#     simulations.append("python3 main.py \
#                         --s1 {} --s2 {} --reliability {} --deadline {} \
#                         --urllc_node {} --mmtc_node {} \
#                         --seed {}".format(
#         s1, s2, reliability, deadline, no_urllc, no_mmtc, SEED))

deadline = "short"
urllc_period = period[deadline]
no_urllc = rho2urllc(urllc_load, urllc_period, urllc_pilot)
mmtc_loads = np.linspace(0.4, 1.5, 12)
no_mmtc_list = [rho2mmtc(rho) for rho in mmtc_loads]

s1 = "FCFS"
for no_mmtc in no_mmtc_list:
    SEED += np.random.randint(100)
    simulations.append("python3 main.py \
                        --s1 {} --s2 {} --reliability {} --deadline {} \
                        --urllc_node {} --mmtc_node {} \
                        --seed {}".format(
        s1, s2 , reliability, deadline, no_urllc, no_mmtc, SEED))

s1 = "RR_Q"
for no_mmtc in no_mmtc_list:
    SEED += np.random.randint(100)
    simulations.append("python3 main.py \
                        --s1 {} --s2 {} --reliability {} --deadline {} \
                        --urllc_node {} --mmtc_node {} \
                        --seed {}".format(
        s1, s2, reliability, deadline, no_urllc, no_mmtc, SEED))

s1 = "RR_NQ"
for no_mmtc in no_mmtc_list:
    SEED += np.random.randint(100)
    simulations.append("python3 main.py \
                        --s1 {} --s2 {} --reliability {} --deadline {} \
                        --urllc_node {} --mmtc_node {} \
                        --seed {}".format(
        s1, s2, reliability, deadline, no_urllc, no_mmtc, SEED))

pool = Pool(processes=PROCESSES)
for k, simulation in enumerate(simulations):
    pool.apply_async(os.system, (simulation,))

pool.close()
pool.join()
print("All simulations completed")
