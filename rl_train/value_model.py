#!/usr/bin/python3
#-*-coding:utf-8-*-
#$File: value_model.py
#$Date: Fri May 27 12:03:55 2016
#$Author: Like Ma <milkpku[at]gmail[dot]com>

import tensorflow as tf
import functools

from util.model import Model, conv2d
from config import Config

def get_model(name):
    name = functools.partial('{}-{}'.format, name)

    self_pos = tf.placeholder(Config.dtype, Config.data_shape, name='self_pos')
    self_ability = tf.placeholder(Config.dtype, Config.data_shape, name='self_ability')
    enemy_pos = tf.placeholder(Config.dtype, Config.data_shape, name='enemy_pos')

    x = tf.concat(3, [self_pos, self_ability, enemy_pos], name=name('input_concat'))

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
    pred = tf.sigmoid(x, name=name('control_sigmoid'))
    pred = tf.mul(pred, self_ability, name=name('valid_moves'))

    # another formula of y*logy
    return Model([self_pos, self_ability, enemy_pos], None, None, pred)


if __name__=="__main__":
    model = get_model('test')
    sess = tf.InteractiveSession()
    sess.run(tf.initialize_all_variables())

    import numpy as np
    x_data = np.random.randint(2, size=[3,100,9,10,16]).astype('float32')

    input_dict = {}
    for var, data in zip(model.inputs, x_data):
        input_dict[var] = data

    pred_val = model.pred.eval(feed_dict=input_dict)

    print(pred_val)
    print('model test OK')
