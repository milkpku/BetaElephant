#!/usr/bin/python3
#-*-coding:utf-8-*-
#$File: trainer.py
#$Date: Fri May 27 11:30:23 2016
#$Author: Like Ma <milkpku[at]gmail[dot]com>

import tensorflow as tf

from value_dataset import Reactor
from value_model import get_value_model
from policy_dataset import load_data
from policy_model import get_model

def train_value():
    policy_model = get_model('policy')
    value_model = get_value_model('value')

    environ = Reactor(policy_model, 'train_log/policy.ckpt')
    sess = tf.Session()

    target_y = tf.placeholder(Config.dtype, shape=[None], name='target_y')

    trian_step = Config.optimizer.minimize(value_model.loss - target_y)
    value_pred = value_model.pred

    # for loop, choose move and react, then train
    while True:
        # get state transfer
        state = None
        pred = sess.run(value_pred, feed_dict={state})
        move =
        reward, next_state, if_terminated, next_move = environ.react(state, move)
        # train value_nets

def train_policy(load_path):
    policy_model = get_model('policy')
    value_model = get_value_model('value')
    train_data = load_data(value_model, 'train_log/value.ckpt')

    # trainer init
    optimizer = Config.optimizer
    train_step = optimizer.minimize(policy_model.loss)

    # init session and server
    sess = tf.InteractiveSession()
    saver = tf.train.Saver()
    if load_path==None:
        sess.run(tf.initialize_all_variables())
    else:
        saver.restore(sess, load_path)
        print("Model restored from %s" % load_path)

    # accuracy
    pred = tf.reshape(model.pred, [-1, 9*10*16])
    label = tf.reshape(model.label, [-1, 9*10*16])
    correct_prediction = tf.equal(tf.argmax(pred, 1), tf.argmax(label,1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    # train steps
    for i in range(Config.n_epoch):

        # training step
        batch_data, batch_label = train_data.next_batch(Config.minibatch_size)

        input_dict = {model.label:batch_label}
        for var, data in zip(model.inputs, batch_data):
            input_dict[var]=data

        sess.run(train_step, feed_dict=input_dict)

        # evalue step
        if (i+1)%Config.evalue_point == 0:
            batch_data, batch_label = train_data.next_batch(Config.minibatch_size)
            val_dict = {model.label:batch_label}
            for var, data in zip(model.inputs, batch_data):
                val_dict[var]=data
            score = accuracy.eval(feed_dict=val_dict)
            print("epoch %d, accuracy is %.2f" % (i,score))

        # save step
        if (i+1)%Config.check_point == 0:
            save_path = saver.save(sess, "%s/epoch-%d" %(Config.save_path, i))
            print("Model saved in file: %s" % save_path)

