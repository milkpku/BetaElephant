#!/usr/bin/python3
#-*-coding:utf-8-*-
#$File: trainer.py
#$Date: Fri May 27 11:30:23 2016
#$Author: Like Ma <milkpku[at]gmail[dot]com>

import tensorflow as tf
import numpy as np

from util.dataset import load_data
from util.tools import batch_max_to_onehot

from config import config
from value_dataset import Reactor
from value_model import get_value_model
from policy_model import get_model

def train_value():
    policy_model = get_model('policy')

    environ = Reactor(policy_model, 'train_log/epoch-399')
    value_model = get_value_model('value')
    sess = tf.Session()

    target_y = tf.placeholder(config.dtype, shape=[None], name='target_y')
    q_loss = tf.nn.l2_loss(value_model.loss - target_y)
    trian_step = config.optimizer.minimize(q_loss)

    value_pred = value_model.pred

    dataset = load_data('train')
    info, label = dataset.next_batch(config.minibatch_size)
    state = info[:2]
    move = info[2]
    params = info[3:]
    # for loop, choose move and react, then train
    while True:
        # get state transfer
        input_dict = {}
        for var, data in zip(value_model.inputs, state +[move]+params):
            input_dict[var] = data
        from IPython import embed; embed()
        pred = sess.run(value_pred, feed_dict=input_dict)
        if np.random.random() > config.randplay:
            choose_move = batch_max_to_onehot(pred)
        else:
            choose_move = batch_max_to_onehot(np.random.random(pred.shape))

        reward, next_state, if_terminated, next_move, next_params = environ.react(state, choose_move)

        # calculate reward
        next_dict = {}
        for var, data in zip(value_model.inputs, next_state + [next_move]+next_params):
            next_dict[var] = data[np.logic_not(if_terminated)]
        next_pred = sess.run(value_pred, feed_dict=next_dict)
        next_max = next_pred.reshape(next_pred.shape[0]).max(axis=1)
        reward[if_terminated] += config.gamma * next_max

        # train value_nets
        input_dict[value_model.label] = choose_move
        input_dict[target_y] = reward
        sess.run(train_step, feed_dict=input_dict)

        # refresh data
        state = next_state
        move = next_move
        params = next_params
        if any(if_terminated):
            info, label = dataset.next_batch(if_terminated.sum())
            for i in range(len(state)):
                state[i][if_terminated] = info[i]
            move[if_terminated] = info[2]
            for i in range(len(params)):
                params[i][if_terminated] = info[3+i]

        # save step
        if (i+1)%config.check_point == 0:
            save_path = saver.save(sess, "%s/value-epoch-%d" %(config.save_path, i))
            print("Model saved in file: %s" % save_path)

def train_policy(load_path):
    policy_model = get_model('policy')
    value_model = get_value_model('value')
    train_data = load_data(value_model, 'train_log/value.ckpt')

    # trainer init
    optimizer = config.optimizer
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
    for i in range(config.n_policy_epoch):

        # training step
        batch_data, batch_label = train_data.next_batch(config.minibatch_size)

        input_dict = {model.label:batch_label}
        for var, data in zip(model.inputs, batch_data):
            input_dict[var]=data

        sess.run(train_step, feed_dict=input_dict)

        # evalue step
        if (i+1)%config.evalue_point == 0:
            batch_data, batch_label = train_data.next_batch(config.minibatch_size)
            val_dict = {model.label:batch_label}
            for var, data in zip(model.inputs, batch_data):
                val_dict[var]=data
            score = accuracy.eval(feed_dict=val_dict)
            print("epoch %d, accuracy is %.2f" % (i,score))

        # save step
        if (i+1)%config.check_point == 0:
            save_path = saver.save(sess, "%s/policy-epoch-%d" %(config.save_path, i))
            print("Model saved in file: %s" % save_path)


if __name__=='__main__':
    train_value()
