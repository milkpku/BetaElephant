
cktp=$1
python3 ~/BetaElephant/export_net/export_policy.py .
python3 ~/tensorflow/tensorflow/python/tools/freeze_graph.py input_graph=input_graph.pb --input_checkpoint=$ckpt --output_node_names=train-predict --output_graph=output_graph
