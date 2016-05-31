#!/usr/bin/python3
#-*-coding:utf-8-*-
#$File: tools.py
#$Date: Tue May 31 16:48:43 2016
#$Author: Like Ma <milkpku[at]gmail[dot]com>

import numpy as np


def batch_max_to_onehot(tensor):
    shape = tensor.shape
    index = np.argmax(tensor.reshape(shape[0], -1), axis=1)
    oht = np.zeros([shape[0], np.prod(shape[1:])])
    oht[np.arange(shape[0]), index] = 1
    oht = oht.reshape(shape)
    return oht

def batch_flatten(ndarry):
    return ndarry.reshape(ndarry.shape[0], -1)

if __name__=="__main__":

    # assert batch_max_to_onehot
    shape = [10,10,30,5]
    a = np.random.random(shape)
    b = batch_max_to_onehot(a)
    assert all(b.reshape(b.shape[0], -1).sum(axis=1)==1)
    print('batch_max_to_onehot OK')
