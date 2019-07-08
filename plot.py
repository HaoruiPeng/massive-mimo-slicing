import os
import matplotlib as plt
import csv
import numpy as np


path = "results/result_high_long.csv"
Dict = {}
keys = []
with open(path) as file:
    csv_reader = csv.reader(file, delimiter=',')
    line_count = 0
    for line in csv_reader:
        if line_count == 0:
            keys = line.copy()
            Dict = dict((key, []) for key in line)
            line_count += 1
        else:
            for i in range(len(line)):
                Dict[keys[i]] = np.append(Dict[keys[i]], line[i])
            line_count += 1

print(Dict[keys[0]])