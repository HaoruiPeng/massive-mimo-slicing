import os
import matplotlib.pyplot as plt
import csv
import numpy as np


result_path = "results/"
figure_path = "plots/"
file_name = "result_high_short"
path = result_path + file_name + ".csv"
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
                value = float(line[i])
                Dict[keys[i]] = np.append(Dict[keys[i]], value)
            line_count += 1

# URLLC = {Dict[keys[0]], Dict[keys[2]], Dict[keys[4]]}
# mMTC = {Dict[keys[1]], Dict[keys[3]], Dict[keys[5]]}

try:
    os.mkdir(figure_path + file_name)
except OSError:
    print("Failed to create figure directory " + file_name + "/")
    print("Directory exists")

# print(Dict[keys[0]])

u_no = np.array(range(int(np.min(Dict[keys[0]])), int(np.max(Dict[keys[0]]))+1))
m_no = np.array(range(int(np.min(Dict[keys[1]])), int(np.max(Dict[keys[1]])+1), 500))

_u_wait = Dict[keys[2]].reshape(len(u_no), len(m_no))
_m_wait = Dict[keys[3]].reshape(len(u_no), len(m_no))
_u_loss = Dict[keys[4]].reshape(len(u_no), len(m_no))
_m_loss = Dict[keys[5]].reshape(len(u_no), len(m_no))

_m_no, _u_no = np.meshgrid(m_no, u_no)

cmap = plt.get_cmap('magma_r')

fig_u_wait = plt.figure(file_name + "_urllc_wait")
plt.contourf(_u_no, _m_no, _u_wait, levels=np.linspace(0, 1, 100), cmap=cmap)
plt.colorbar()
plt.xlabel("No. of URLLC nodes")
plt.ylabel("No. of mMTC nodes")
plt.savefig(figure_path + file_name + "/URLLC_wait.png")

fig_m_wait = plt.figure(file_name + "_mmtc_wait")
plt.contourf(_u_no, _m_no, _m_wait, levels=np.linspace(0, 101, 100), cmap=cmap)
plt.colorbar()
plt.xlabel("No. of URLLC nodes")
plt.ylabel("No. of mMTC nodes")
plt.savefig(figure_path + file_name + "/mMTC_wait.png")

fig_u_loss = plt.figure(file_name + "_urllc_loss")
plt.contourf(_u_no, _m_no, _u_loss, levels=np.linspace(0, 1, 100), cmap=cmap)
plt.colorbar()
plt.xlabel("No. of URLLC nodes")
plt.ylabel("No. of mMTC nodes")
plt.savefig(figure_path + file_name + "/URLLC_loss.png")

fig_m_loss = plt.figure(file_name + "_mmtc_loss")
plt.contourf(_u_no, _m_no, _m_loss, levels=np.linspace(0, 1, 100), cmap=cmap)
plt.colorbar()
plt.xlabel("No. of URLLC nodes")
plt.ylabel("No. of mMTC nodes")
plt.savefig(figure_path + file_name + "/mMTC_loss.png")

plt.show()

