import os
import matplotlib.pyplot as plt
import csv
import numpy as np


result_path = "results/"
figure_path = "plots/"
strategy_name = "RR_NQ"
file_name = "high_short"
path = result_path + strategy_name + "/" +file_name + ".csv"
keys = ['No.URLLC', 'No.mMTC', 'URLLC_wait_time', 'mMTC_wait_time', 'URLLC_loss_rate', 'mMTC_loss_rate']
Dict = dict((key, []) for key in keys)

with open(path) as file:
    csv_reader = csv.reader(file, delimiter=',')
    for line in csv_reader:
        for i in range(len(line)):
            value = float(line[i])
            Dict[keys[i]] = np.append(Dict[keys[i]], value)

try:
    os.makedirs(figure_path + strategy_name + '/' + file_name)
except OSError:
    print("Failed to create figure directory " + strategy_name + '/' + file_name + "/")
    print("Directory exists")


u_no = np.array(range(int(np.min(Dict[keys[0]])), int(np.max(Dict[keys[0]]))+1))
m_no = np.array(range(int(np.min(Dict[keys[1]])), int(np.max(Dict[keys[1]])+1), 500))

new_keys = keys[2:6]
figs = {}
print(new_keys)

for k in new_keys:
    figs[k], axs = plt.subplots(1, 2, sharey='all', figsize=(20, 8))
    figs[k].suptitle(k)
    for u in u_no:
        ind_list = np.where(Dict[keys[0]] == u)
        m = Dict[keys[1]][ind_list]
        result_1 = Dict[k][ind_list]
        axs[0].plot(m, result_1, label=str(u))
    axs[0].legend(loc='upper right')
    for m in m_no:
        ind_list = np.where(Dict[keys[1]] == m)
        u = Dict[keys[0]][ind_list]
        result_2 = Dict[k][ind_list]
        axs[1].plot(u, result_2, label=str(m))
    axs[1].legend(loc='upper right')
    plt.savefig(figure_path + strategy_name + '/' + file_name + "/" + k + ".png")

plt.show()

