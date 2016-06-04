#!/usr/bin/python3
#-*-coding:utf-8-*-
#$File: export_policy.py
#$Date: Fri Jun  3 14:54:41 2016
#$Author: Like Ma <milkpku[at]gmail[dot]com>

import tensorflow as tf
#from tensorflow.python.tools import freeze_graph

import sys
import argparse

def export_input_graph(model_folder):
    sys.path.append(model_folder)
    from model import get_model

    with tf.Session() as sess:
        model = get_model('train')

        saver = tf.train.Saver()

        tf.train.write_graph(sess.graph_def, model_folder, 'input_graph.pb', as_text=True)


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('model_folder', help='Folder where model.py exists.')
    # parser.add_argument('ckpt_path', help='Path of checkpoint file.')
    args = parser.parse_args()

    export_input_graph(args.model_folder)
