#!/usr/bin/python3
#-*-coding:utf-8-*-
#$File: model.py
#$Date: Sat May  7 10:59:45 2016
#$Author: Like Ma <milkpku[at]gmail[dot]com>

from config import Config

import tensorflow as tf
import functools

from util.model import Model, conv2d

def get_model(name):
    name = functools.partial('{}-{}'.format, name)

    self_pos = tf.placeholder(Config.dtype, Config.data_shape, name='self_pos')
    enemy_pos = tf.placeholder(Config.dtype, Config.data_shape, name='enemy_pos')
    self_ability = tf.placeholder(Config.dtype, Config.data_shape, name='self_ability')
    enemy_protect = tf.placeholder(Config.dtype, Config.data_shape, name='enemy_protect')

    input_label = tf.placeholder(Config.dtype, Config.label_shape, name='input_label')

    x = tf.concat(3, [self_pos, self_ability, enemy_pos, enemy_protect], name=name('input_concat'))
    y = input_label

    nl = tf.nn.tanh

    def conv_pip(name, x):
        name = functools.partial('{}_{}'.format, name)

        x = conv2d(name('0'), x, Config.data_shape[3]*2, kernel=3, stride=1, nl=nl)
        x = conv2d(name('1'), x, Config.data_shape[3], kernel=3, stride=1, nl=nl)
        return x

    for layer in range(5):
        x_branch = conv_pip(name('conv%d'%layer), x)
        x = tf.concat(3, [x,x_branch], name=name('concate%d'%layer))

    x = conv_pip(name('conv5'), x)
    x = tf.tanh(x, name=name('control_tanh'))
    z = tf.mul(tf.exp(x), self_ability)
    z_sum = tf.reduce_sum(z, reduction_indices=[1,2,3], name=name('partition_function')) # partition function

    # another formula of y*logy
    loss = -tf.reduce_sum(tf.mul(x, y), reduction_indices=[1,2,3]) + tf.log(z_sum)
    z_sum = tf.reshape(z_sum, [-1, 1, 1, 1])
    pred = tf.div(z, z_sum, name=name('predict'))
    return Model([self_pos, enemy_pos, self_ability, enemy_protect], input_label, loss, pred, debug=z)

if __name__=='__main__':

    model = get_model('test')
    sess = tf.InteractiveSession()
    sess.run(tf.initialize_all_variables())

    import numpy as np
    x_data = np.random.randint(2, size=[4,100,9,10,16]).astype('float32')
    y_data = np.random.randint(2, size=[100,9,10,16]).astype('float32')

    input_dict = {}
    for var, data in zip(model.inputs, x_data):
        input_dict[var] = data
    input_dict[model.label] = y_data

    loss_val = model.loss.eval(feed_dict=input_dict)
    pred_val = model.pred.eval(feed_dict=input_dict)
    print(loss_val)
    # print(pred_val)

    pred_val = pred_val.reshape(pred_val.shape[0], -1)
    assert all(abs(pred_val.sum(axis=1)-1.0<1e-6))
    print('model test OK')
