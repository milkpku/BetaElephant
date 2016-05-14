#!/usr/bin/python3
#-*-coding:utf-8-*-
#$File: dataset.py
#$Date: Sat May  7 10:59:24 2016
#$Author: Like Ma <milkpku[at]gmail[dot]com>

Class Dataset(object):

    def __init__(self, datafile_path):
        pass


    def next_batch(self, batch_size):
        '''
        return [data, label] with batched size
        '''
        pass

def load_data(data_name):
    '''
    return dataset which yeild minibatch data
    '''
    pass

