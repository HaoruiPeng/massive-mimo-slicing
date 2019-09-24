import os
import matplotlib.pyplot as plt
import csv
import numpy as np


result_dir = "results/"
# figure_dir = "plots_2/"
strategy_names = ['FCFS', 'RR_NQ', 'RR_Q']
load = 'low_short'
meas = ['wait', 'loss']
statistics_med = ['mean', 'var', 'conf_inter']

file_name = "statistics.csv"

no_urllc = np.linspace(5, 20, 16)
no_mmtc = 1000.


def no2load(no_urllc):
    x = 0.5
    P = 1
    n = 1
    return (no_urllc * n * x) / (12 * P)


result_path = result_dir + file_name

# Dict = dict((strategy,
#              dict((profile, dict((mea, dict((statistics, [])
#                                             for statistics in statistics_med))
#                                  for mea in meas))
#                   for profile in profile_names))
#             for strategy in strategy_names)
# for strategy in strategy_names:
#         try:
#             os.makedirs(figure_dir + strategy + '/' + profile)
#         except OSError:
#             print("Dir " + figure_dir + strategy + '/' + profile + " create error")

fig_names = ['urllc_wait', 'urllc_loss', 'mmtcs_wait', 'mmtc_loss']
keys = ['No.URLLC', 'URLLC_wait_time', 'mMTC_wait_time', 'URLLC_loss_rate', 'mMTC_loss_rate']

fig_dict = dict((figure_name, plt.subplots(figsize=(10, 8))) for figure_name in fig_names)
for figure_name in fig_names:
    fig_dict[figure_name][0].suptitle(figure_name)


for strategy in strategy_names:
    with open(result_path) as file:
        csv_reader = csv.reader(file, delimiter=',')
        cat_list = (l for l in csv_reader if l[0] == strategy and l[1] == load and float(l[3]) == no_mmtc)
        u = []
        w_u = []
        w_m = []
        l_u = []
        l_m = []
        for line in cat_list:
            u.append(float(line[2]))
            w_u.append((float(line[4]), float(line[6]), float(line[7])))
            w_m.append((float(line[8]), float(line[10]), float(line[11])))
            l_u.append((float(line[12]), float(line[14]), float(line[15])))
            l_m.append((float(line[16]), float(line[18]), float(line[19])))
        m = np.array([no2load(n) for n in u])
        w_u = np.array(w_u)
        w_m = np.array(w_m)
        l_u = np.array(l_u)
        l_m = np.array(l_m)
        fig_dict[fig_names[0]][1].plot(m, w_u[:, 0], alpha=0.6, label=strategy)
        fig_dict[fig_names[0]][1].fill_between(m, w_u[:, 1], w_u[:, 2], alpha=0.2)
        fig_dict[fig_names[0]][1].legend(loc="upper right")
        fig_dict[fig_names[1]][1].plot(m, l_u[:, 0], alpha=0.6, label=strategy)
        fig_dict[fig_names[1]][1].fill_between(m, l_u[:, 1], l_u[:, 2], alpha=0.2)
        fig_dict[fig_names[1]][1].legend(loc="upper right")
        fig_dict[fig_names[2]][1].plot(m, w_m[:, 0], alpha=0.6, label=strategy)
        fig_dict[fig_names[2]][1].fill_between(m, w_m[:, 1], w_m[:, 2], alpha=0.2)
        fig_dict[fig_names[2]][1].legend(loc="upper right")
        fig_dict[fig_names[3]][1].plot(m, l_m[:, 0], alpha=0.6, label=strategy)
        fig_dict[fig_names[3]][1].fill_between(m, l_m[:, 1], l_m[:, 2], alpha=0.2)
        fig_dict[fig_names[3]][1].legend(loc="upper right")

plt.show()

        # for m in no_mmtc:
        #     with open(result_path) as file:
        #         csv_reader = csv.reader(file, delimiter=',')
        #         cat_list = (l for l in csv_reader if l[0] == strategy and l[1] == profile and float(l[3]) == m)
        #         u = []
        #         w_u = []
        #         w_m = []
        #         l_u = []
        #         l_m = []
        #         for line in cat_list:
        #             u.append(float(line[2]))
        #             w_u.append((float(line[4]), float(line[6]), float(line[7])))
        #             w_m.append((float(line[8]), float(line[10]), float(line[11])))
        #             l_u.append((float(line[12]), float(line[14]), float(line[15])))
        #             l_m.append((float(line[16]), float(line[18]), float(line[19])))
        #         w_u = np.array(w_u)
        #         w_m = np.array(w_m)
        #         l_u = np.array(l_u)
        #         l_m = np.array(l_m)
        #         axs[fig_names[0]][1].plot(u, w_u[:, 0], alpha=0.6, label=str(m))
        #         axs[fig_names[0]][1].fill_between(u, w_u[:, 1], w_u[:, 2], alpha=0.2)
        #         axs[fig_names[0]][1].legend(loc="upper right")
        #         axs[fig_names[1]][1].plot(u, l_u[:, 0], alpha=0.6, label=str(m))
        #         axs[fig_names[1]][1].fill_between(u, l_u[:, 1], l_u[:, 2], alpha=0.2)
        #         axs[fig_names[1]][1].legend(loc="upper right")
        #         axs[fig_names[2]][1].plot(u, w_m[:, 0], alpha=0.6, label=str(m))
        #         axs[fig_names[2]][1].fill_between(u, w_m[:, 1], w_m[:, 2], alpha=0.2)
        #         axs[fig_names[2]][1].legend(loc="upper right")
        #         axs[fig_names[3]][1].plot(u, l_m[:, 0], alpha=0.6,label=str(m))
        #         axs[fig_names[3]][1].fill_between(u, l_m[:, 1], l_m[:, 2], alpha=0.2)
        #         axs[fig_names[3]][1].legend(loc="upper right")



            # axs[line[0]][line[1]][fig_names[0]][0].plot(float(line[2]), float(line[4]), 'o-', label=str(line[3]))
            # axs[line[0]][line[1]][fig_names[0]][1].plot(float(line[3]), float(line[8]), 'o-', label=str(line[2]))

            # for u in no_urllc:
            #     ref_list = (l for l in cat_list if l[2] == u)
            #     print(l[4] for l in ref_list)

            #axs[line[0]][line[1]][fig_names[0]][0].plot(float(line[2]), float(line[4]), 'o-', label=str(line[3]))
            #axs[line[0]][line[1]][fig_names[0]][1].plot(float(line[3]), float(line[8]), 'o-', label=str(line[2]))

# plt.show()

# for strategy in strategy_names:
#     for profile in profile_names:
#         for fig_name in fig_names:
#             figs[fig_name].savefig(figure_dir + strategy + '/' + profile + '/' + fig_name + '.png')

# new_keys = keys[2:6]
#
# print(new_keys)
#
# for k in new_keys:
#     figs[k], axs = plt.subplots(1, 2, sharey='all', figsize=(20, 8))
#     figs[k].suptitle(k)
#     for u in u_no:
#         ind_list = np.where(Dict[keys[0]] == u)
#         m = Dict[keys[1]][ind_list]
#         result_1 = Dict[k][ind_list]
#         axs[0].plot(m, result_1, label=strategy)
#     axs[0].legend(loc='upper right')
#     for m in m_no:
#         ind_list = np.where(Dict[keys[1]] == m)
#         u = Dict[keys[0]][ind_list]
#         result_2 = Dict[k][ind_list]
#         axs[1].plot(u, result_2, label=str(m))
#     axs[1].legend(loc='upper right')
#     plt.savefig(figure_path + strategy_name + '/' + file_name + "/" + k + ".png")
#
# plt.show()
#
