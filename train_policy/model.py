#!/usr/bin/python3
#-*-coding:utf-8-*-
#$File: model.py
#$Date: Sat May  7 10:59:45 2016
#$Author: Like Ma <milkpku[at]gmail[dot]com>

from config import Config

import tensorflow as tf
import functools


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

def get_model(name):
    name = functools.partial('{}-{}'.format, name)

    input_data = tf.placeholder(Config.dtype, Config.data_shape, name='input_data')
    input_label = tf.placeholder(Config.dtype, Config.label_shape, name='input_label')

    x = input_data
    y = input_label

    nl = tf.nn.elu

    def conv_pip(name, x):
        name = functools.partial('{}_{}'.format, name)

        x = conv2d(name('0'), x, Config.data_shape[3]*2, kernel=3, stride=1, nl=nl)
        x = conv2d(name('1'), x, Config.data_shape[3], kernel=3, stride=1, nl=nl)
        return x

    x_ori = x
    for layer in range(5):
        x_branch = conv_pip(name('conv%d'%layer), x)
        x = tf.concat(3, [x,x_branch], name=name('concate%d'%layer))

    x = conv_pip(name('conv5'), x)
    z = tf.mul(tf.exp(x), x_ori)
    z_sum = tf.reduce_sum(z, reduction_indices=[1,2,3], name=name('partitial_function')) # partition function

    # another formula of y*logy
    loss = -tf.reduce_sum(tf.mul(x, y), reduction_indices=[1,2,3]) + tf.log(z_sum)
    pred = tf.div(z, z_sum, name=name('predict'))
    return input_data, input_label, loss, pred

if __name__=='__main__':

    x, y, loss, pred = get_model('test')
    sess = tf.InteractiveSession()
    sess.run(tf.initialize_all_variables())

    import numpy as np
    x_data = np.random.randint(1, size=[100,9,10,32]).astype('float32')

    k = np.random.randint(9*10*32, size=100)
    y_data = np.zeros([100, 9*10*32])
    for i in range(100):
        y_data[i,k[i]]=1
    y_data =  np.reshape(y_data, [100, 9, 10, 32])

    loss_val = loss.eval(feed_dict={x: x_data, y: y_data})
    pred_val = pred.eval(feed_dict={x: x_data, y: y_data})
    print(loss_val)
    print(pred_val)

    from IPython import embed;embed()
