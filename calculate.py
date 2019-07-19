import csv
import numpy as np
import scipy.stats as st
import argparse
import sys

result_path = "results/"
result_file = "statistics.csv"
try:
    statistics = open(result_path + result_file, "a")
except FileNotFoundError:
    statistics = open(result_path + result_file, "w+")
    statistics.write("No.URLLC,No.mMTC,"
                     "Uw_mean,Uw_var,Uw_con_low,Uw_con_high,"
                     "Mw_mean,Mw_var,Mw_con_low,Mw_con_high,"
                     "Ul_mean,Ul_var,Ul_con_low,Mw_con_high,"
                     "Ml_mean,Ml_var,Ml_con_low,Mw_con_high\n")

line_counter = 0
keys = ['No.URLLC', 'No.mMTC', 'URLLC_wait_time', 'mMTC_wait_time', 'URLLC_loss_rate', 'mMTC_loss_rate']


parser = argparse.ArgumentParser()
parser.add_argument('--scheduler', action="store", default=None)
parser.add_argument('--reliability', action="store", default=None)
parser.add_argument('--deadline', action="store", default=None)

args = parser.parse_args()
strategy = args.scheduler
traffic = args.reliability + "_" + args.deadline

file_path = result_path + strategy + "/" + traffic + ".csv"
Dict = dict((key, []) for key in keys)
with open(file_path) as file:
    csv_reader = csv.reader(file, delimiter=',')
    for line in reversed(list(csv_reader)):
        line_counter += 1
        for i in range(len(line)):
            value = float(line[i])
            Dict[keys[i]] = np.append(Dict[keys[i]], value)
        if line_counter == 10:
            break

uniq = 0
if len(Dict[keys[0]]) > 0:
    uniq = np.unique(Dict[keys[0]])
    if len(uniq) > 1:
        statistics.write("Received wrong URLLC data for current parameter configuration\n")
        print(uniq)
        sys.exit(0)
    else:
        uniq = np.unique(Dict[keys[1]])
        if len(uniq) > 1:
            statistics.write("Received wrong mMTC data for current parameter configuration\n")
            sys.exit(0)
        else:
            statistics.write(str(Dict[keys[0]][0]) + ',' +
                             str(Dict[keys[1]][0]) + ',')
else:
    statistics.write("Received no data for current parameter configuration\n")
    sys.exit(0)

for i in range(2, 6):
    value_list = Dict[keys[i]]
    mean_val = np.mean(value_list)
    var_val = np.var(value_list)
    if var_val > 0.0:
        con_interval = st.t.interval(0.95, len(value_list)-1, loc=mean_val, scale=st.sem(value_list))
    else:
        con_interval = (mean_val, mean_val)
    if i is not 5:
        statistics.write(str(mean_val) + ',' +
                         str(var_val) + ',' +
                         str(con_interval[0]) + ',' +
                         str(con_interval[1]) + ',')
    else:
        statistics.write(str(mean_val) + ',' +
                         str(var_val) + ',' +
                         str(con_interval[0]) + ',' +
                         str(con_interval[1]) + '\n')




