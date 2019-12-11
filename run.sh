#!/bin/bash

python3 main.py \
                --s1 FCFS --s2 FCFS --period_var 0.001 --variance_var 0.05 \
                --urllc_node 320 --mmtc_node 0 --mu 2.06 \
                --seed 77777
