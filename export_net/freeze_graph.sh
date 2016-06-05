#!/bin/bash

ckpt=$1
python3 ~/Documents/BetaElephant/export_net/export_policy.py .
python3 ~/Documents/tensorflow/tensorflow/python/tools/freeze_graph.py --input_graph=input_graph.pb --input_checkpoint=$ckpt --output_node_names=train-predict --output_graph=output_graph.pb
