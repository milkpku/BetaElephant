#!/usr/bin/python3
#-*-coding:utf-8-*-
#$File: dataset.py
#$Date: Sat May  7 10:59:24 2016
#$Author: Like Ma <milkpku[at]gmail[dot]com>

import numpy as np

class Dataset(object):

    def __init__(self, datafile_path):
        self.file_object = open(datafile_path, 'r')    
        # map chess piece to location, from left to right, from down to up, red is below
        self.piecehash = ['A0','B0','C0','D0','E0','F0','G0','H0','I0','B2','H2','A3',
                          'C3','E3','G3','I3','A6','C6','E6','G6','I6','B7','H7','A9',
                          'B9','C9','D9','E9','F9','G9','H9','I9']

    def initphash(self):
        self.piecehash = ['A0','B0','C0','D0','E0','F0','G0','H0','I0','B2','H2','A3',
                          'C3','E3','G3','I3','A6','C6','E6','G6','I6','B7','H7','A9',
                          'B9','C9','D9','E9','F9','G9','H9','I9']

    def loc2piece(self, location):
        return self.piecehash.index(location)

    def loca2i(self, loc):
        if (loc >= 'A' and loc <= 'Z'):
            return ord(loc)-ord('A')
        else:
            return int(loc)

    def confen2mat(self, fen):
        batchdata = np.zeros((9, 10, 32), dtype=float)
        batchlabel = np.zeros((9, 10, 32), dtype=float)
        fenlist = fen.split('\t')
        movelist = fenlist[1].split()
        for move in movelist:
            src = move.split('-')[0]
            des = move.split('-')[1]
            batchdata[self.loca2i(des[0])][self.loca2i(des[1])] \
                     [self.loc2piece(src)]= 1
        label = fenlist[2].strip().split('-')
        # print label
        batchlabel[self.loca2i(label[1][0])][self.loca2i(label[1][1])]\
                  [self.loc2piece(label[0])]= 1
        if label[1] in self.piecehash:
            self.piecehash[self.piecehash.index(label[1])] = '00'
        self.piecehash[self.loc2piece(label[0])] = label[1]
        return batchdata, batchlabel

    def next_batch(self, batch_size):
        '''
        return [data, label] with batched size
        '''
        batchdata = np.zeros((batch_size, 9, 10, 32), dtype=float) 
        batchlabel = np.zeros((batch_size, 9, 10, 32), dtype=float)
        for i in range(batch_size):
            line = self.file_object.readline()
            if line != '':
                if line[-5:-1] == 'WIN!':
                    self.initphash()
                    i -= 1
                    continue
            else:
                self.file_object.seek(0, 0)
                self.initphash()
                line = self.file_object.readline()
            batchdata[i], batchlabel[i] = self.confen2mat(line)
        return batchdata, batchlabel

def load_data(data_name):
    '''
    return dataset which yeild minibatch data
    '''
    data = Dataset(data_name)
    return data

def visualdata(data):
    for i in range(data.shape[2]):
        print "%d :" % (i)
        for j in range(data.shape[1]):
            for k in range(data.shape[0]):
                print int(data[k][j][i]),
            print '\n',
        print '\n'
    print '\n'


if __name__ == '__main__':
    traindata = load_data('../data/out.temp')
    for i in range(1):
        batch_data, batch_label = traindata.next_batch(10)
        visualdata(batch_data[0])
        visualdata(batch_data[2])

