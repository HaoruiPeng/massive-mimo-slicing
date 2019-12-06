#!/bin/bash

python3 main.py \
                --s1 FCFS --s2 FCFS --reliability low --deadline long \
                --urllc_node 120 --mmtc_node 600 --mu 2.06 \
                --seed 5000
