
#!/usr/bin/python3
#-*-coding:utf-8-*-
#$File: config.py
#$Date: Sat May  7 11:00:28 2016
#$Author: Like Ma <milkpku[at]gmail[dot]com>

import tensorflow as tf

class Config(object):

    # dataset
    data_shape = [None, 9, 10, 32]
    label_shape = [None, 9, 10, 32]

    # model
    dtype=tf.float32

    # training

