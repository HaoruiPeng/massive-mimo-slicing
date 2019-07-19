#!/bin/bash

schs=('FCFS' 'RR_NQ' 'RR_Q')
rels=('high' 'low')
deads=('short' 'long')

rm logs/seed_log.csv
rm stats/simulation_stats.csv

for sch in "${schs[@]}"; do
    for rel in "${rels[@]}"; do
        for dead in "${deads[@]}"; do
        jq '.no_urllc_nodes = 4 | .no_mmtc_nodes = 0' slices/slice_config.json > slices/tmp.json
        cp slices/tmp.json slices/slice_config.json
        for U in 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19
        do
            jq '.no_urllc_nodes += 1' slices/slice_config.json > slices/tmp.json
            for VALUE in 1 2 3 4 5 6 7 8 9 10
            do
                jq ' if .no_mmtc_nodes == 5000
                   then .no_mmtc_nodes = 500
                   else .no_mmtc_nodes += 500
                   end ' slices/tmp.json > slices/tmp2.json
                cp slices/tmp2.json slices/tmp.json
                cp slices/tmp2.json slices/slice_config.json
                for i in `seq 10`
                do
                python3 main.py --scheduler "$sch" --reliability "$rel" --deadline "$dead"
                done
                python3 calculate.py --scheduler "$sch" --reliability "$rel" --deadline "$dead"
            done
            done
        done
    done
done
