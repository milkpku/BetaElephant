#!/usr/bin/python3
#-*-coding:utf-8-*-
#$File: model_eval.py
#$Date: Sat Jun  4 09:59:32 2016
#$Author: Like Ma <milkpku[at]gmail[dot]com>

import tensorflow as tf
import numpy as np
import sys
import argparse


class Evaluer(object):

    def __init__(self, model_folder, checkpoint_file):
        sys.path.append(model_folder)

        from model import get_model
        from dataset import load_data

        self.dataset = load_data('validation')

        self.sess = tf.InteractiveSession()
        self.model = get_model('train')

        saver = tf.train.Saver()
        saver.restore(self.sess, checkpoint_file)

    def evalue_topN(self, batch, N=5):
        data, label = self.dataset.next_batch(batch)

        input_dict = {}
        for var, subdata in zip(self.model.inputs, data):
            input_dict[var] = subdata

        pred = self.model.pred.eval(feed_dict=input_dict)

        # accuracy
        pred = pred.reshape([-1, 9*10*16])
        label = label.reshape([-1, 9*10*16])

        accuracy = np.mean(pred.argmax(axis=1)==label.argmax(axis=1))

        # topN
        topN = 0
        for prob, ind in zip(pred, label.argmax(axis=1)):
            v = prob[ind]
            prob.sort()
            if v >= prob[-N]:
                topN += 1

        topN /= len(pred)

        print('accuracy %.2f, top%d %.2f' % (accuracy, N, topN))

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('model_folder', help='Foler for model')
    parser.add_argument('checkpoint_file', help='File path of checkpoint')
    args = parser.parse_args()

    evaluer = Evaluer(args.model_folder, args.checkpoint_file)

    for i in range(10):
        evaluer.evalue_topN(100, 3)

