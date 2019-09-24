#!/bin/bash

rm logs/seed_log.csv
rm stats/simulation_stats.csv

for i in `seq 101`
do
    python3 main.py --scheduler "RR_Q" --reliability "high" --deadline "short"
    jq ' if .no_mmtc_nodes == 5000
        then .no_mmtc_nodes = 0
        else .no_mmtc_nodes += 50
        end ' slices/tmp.json > slices/tmp2.json
    cp slices/tmp2.json slices/tmp.json
    cp slices/tmp2.json slices/slice_config.json
done

