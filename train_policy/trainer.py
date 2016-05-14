#!/usr/bin/python3
#-*-coding:utf-8-*-
#$File: trainer.py
#$Date: Sat May  7 11:00:10 2016
#$Author: Like Ma <milkpku[at]gmail[dot]com>

from config import Config
from dataset import load_data
from model import get_model

import tensorflow as tf

import argparse

def train(load_path=None):

    # load data
    train_data = load_data('train')
    val_data = load_data('validation')

    # load model
    model = get_model('train')

    # trainer init
    optimizer = Config.optimizer
    train_step = optimizer.minimize(model.loss)

    # init session and server
    sess = tf.Session()
    saver = tf.train.Saver()
    if load_path==None:
        sess.run(tf.initialize_all_variables())
    else:
        saver.restore(sess, load_path)
        print("Model restored from %s" % load_path)

    # train steps
    for i in range(Config.n_epoch):
        # training step
        batch_data, batch_label = train_data.next_batch(Config.minibatch_size)
        sess.run(train_step, feed_dict={x:batch_data, y:batch_label})
        # evalue step
        if (i+1)%Config.evalue_point == 0:
            batch_data, batch_label = val_data.next_batch(Config.minibatch_size)
            score = acurracy.eval(feed_dict={x:batch_data, y:batch_label})
            print("epoch %d, acurracy is %.2f" % (i,score))
        # save step
        if (i+1)%Config.check_point == 0:
            save_path = saver.save(sess, Config.save_path)
            print("Model saved in file: %s" % save_path)

if __name__=='__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--load_path", default=None, help="load trained model")
    args = parser.parse_args()

    train(args.load_path)
