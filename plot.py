import os
import matplotlib.pyplot as plt
import csv
import numpy as np


result_path = "results/"
figure_path = "plots/"
# strategy_names = ['FCFS', "RR_Q", 'RR_NQ']
strategy_names = ['FCFS', 'RR_NQ']
file_name = "high_short"
load = "mid_load"

keys = ['No.URLLC', 'No.mMTC', 'URLLC_wait_time', 'mMTC_wait_time', 'URLLC_loss_rate', 'mMTC_loss_rate']
figure_names = ['URLLC_wait_time', 'mMTC_wait_time', 'URLLC_loss_rate', 'mMTC_loss_rate']

def no2load(no_mmtc):
    x = 0.5
    P = 100
    return (no_mmtc * x) / (12 * P)


try:
    os.makedirs(figure_path)
except OSError:
    print("Failed to create figure directory " +  figure_path)
    print("Directory exists")

figure_name = figure_path + load
fig_dict = dict((figure_name, plt.subplots(figsize=(10, 8))) for figure_name in figure_names)
for figure_name in figure_names:
    fig_dict[figure_name][0].suptitle(figure_name)

for strategy in strategy_names:
    path = result_path + strategy + "/" + file_name + ".csv"
    Dict = dict((key, []) for key in keys)
    with open(path) as file:
        csv_reader = csv.reader(file, delimiter=',')
        for line in csv_reader:
            for i in range(len(line)):
                value = float(line[i])
                Dict[keys[i]] = np.append(Dict[keys[i]], value)
    m_ro = np.array([no2load(n) for n in Dict[keys[1]]])
    u_wt = np.array(Dict[keys[2]])
    m_wt = np.array(Dict[keys[3]])
    u_lr = np.array(Dict[keys[4]])
    m_lr = np.array(Dict[keys[5]])
    fig_dict[figure_names[0]][1].plot(m_ro, u_wt, label=strategy)
    fig_dict[figure_names[0]][1].legend(loc='upper right')
    fig_dict[figure_names[1]][1].plot(m_ro, m_wt, label=strategy)
    fig_dict[figure_names[1]][1].legend(loc='upper right')
    fig_dict[figure_names[2]][1].plot(m_ro, u_lr, label=strategy)
    fig_dict[figure_names[2]][1].legend(loc='upper right')
    fig_dict[figure_names[3]][1].plot(m_ro, m_lr, label=strategy)
    fig_dict[figure_names[3]][1].legend(loc='upper right')

plt.savefig(file_name + ".png")
plt.show()

