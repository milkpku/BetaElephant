#!/usr/bin/python3
#-*-coding:utf-8-*-
#$File: trainer.py
#$Date: Sat May  7 11:00:10 2016
#$Author: Like Ma <milkpku[at]gmail[dot]com>

from config import Config
from dataset import load_data
from model import load_model

import tensorflow as tf
import tensorflow.train

def train():

    # load data
    train_data = load_data('train')
    val_data = load_data('validation')

    # load model
    model = load_model()

    # trainer init
    optimizer = Config.optimizer
    train_step = optimizer.minimize()

    sess = tf.Session()
    sess.run(model.init)

    # train steps
    for i in range(Config.n_epoch):
        batch_data, batch_label = train_data.next_batch(Config.minibatch_size)
        sess.run(train_step, feed_dict={x:batch_data, y:batch_label})
        if i%Config.check_point == 0:
            batch_data, batch_label = val_data.next_batch(Config.minibatch_size)
            acurracy.eval(feed_dict={x:batch_data, y:batch_label})


