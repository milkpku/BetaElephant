#!/usr/bin/python3
#-*-coding:utf-8-*-
#$File: model.py
#$Date: Sat May  7 10:59:45 2016
#$Author: Like Ma <milkpku[at]gmail[dot]com>

import tensorflow as tf
import functools

class Model(object):
    def __init__(self, inputs, label, loss, pred):
        self.inputs = inputs
        self.label = label
        self.loss = loss
        self.pred = pred

def weight_variable(name, shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial, name=name)

def bias_variable(name, shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial, name=name)

def conv2d(name, x, out_channel, kernel, stride, nl=None):
    name = functools.partial('{}-{}'.format, name)
    # W
    shape = [kernel, kernel, x.get_shape()[3].value, out_channel]
    W = weight_variable(name('W'), shape)
    # b
    b = bias_variable(name('b'), [out_channel])
    # conv
    y = tf.nn.conv2d(x, W, strides=[1,stride,stride,1], padding='SAME', name=name('op'))
    y = y + b
    # nonlinearty
    return nl(y) if nl else y
