#!/bin/bash

python3 main.py \
                --urllc_node 180 --mu 2.1 \
                --ratio 5.0 --deadline_var 0.02 \
                --period_var 0.04 --variance_var 0.08\
                --seed 1025
