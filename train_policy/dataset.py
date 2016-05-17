#!/usr/bin/python3
#-*-coding:utf-8-*-
#$File: dataset.py
#$Date: Sat May  7 10:59:24 2016
#$Author: Like Ma <milkpku[at]gmail[dot]com>

import numpy as np

OUT_TYPE = np.float32

class Dataset(object):

    def __init__(self, datafile_path):
        self.file_object = open(datafile_path, 'r')    
        self.chesslayer = {}

    def init_clayer(self):
        # king(帅)*1, advisor(仕)*2, bishop(象)*2, knight(马)*2
        # rook(车)*2, cannon(炮)*2, pawn(兵)*5
        # Upper: red      Lower: black
        self.chesslayer = {'K':0, 'A':1, 'B':3, 'N':5, 'R':7, 'C':9, 'P':11,
                           'k':0, 'a':1, 'b':3, 'n':5, 'r':7, 'c':9, 'p':11}

    def loca2i(self, loc):
        if (loc >= 'A' and loc <= 'Z'):
            return ord(loc)-ord('A')
        else:
            return int(loc)

    def f2tpos(self, fen, frdpos, emypos):
        self.init_clayer()
        poslist = fen.split()[0].split('/')
        for i in range(len(poslist)):
            item = poslist[9 - i]
            index = 0
            for j in range(len(item)):
                if item[j].isupper():
                    frdpos[index][i][self.chesslayer[item[j]]] = 1
                    self.chesslayer[item[j]] += 1
                    index += 1
                elif item[j].islower():
                    emypos[index][i][self.chesslayer[item[j]]] = 1
                    self.chesslayer[item[j]] += 1
                    index += 1
                else:
                    index += int(item[j])
        return frdpos, emypos

    def f2tfrdmove(self, move, frdmove, frdpos):
        movelist = move.split()
        for item in movelist:
            src = item.split('-')[0]
            des = item.split('-')[1]
            layer = np.argmax(frdpos[self.loca2i(src[0])][self.loca2i(src[1])])
            frdmove[self.loca2i(des[0])][self.loca2i(des[1])][layer] = 1
        return frdmove

    def fen2tensor(self, fen):

        frdpos = np.zeros((9, 10, 16), dtype=OUT_TYPE)
        frdmove = np.zeros((9, 10, 16), dtype=OUT_TYPE)
        emypos = np.zeros((9, 10, 16), dtype=OUT_TYPE)
        emymove = np.zeros((9, 10, 16), dtype=OUT_TYPE)
        movelabel = np.zeros((9, 10, 16), dtype=OUT_TYPE)

        fenlist = fen.split('\t')
        frdpos, emypos = self.f2tpos(fenlist[0], frdpos, emypos)
        frdmove = self.f2tfrdmove(fenlist[1], frdmove, frdpos)

        label = fenlist[2].strip().split('-')
        layer = np.argmax(frdpos[self.loca2i(label[0][0])][self.loca2i(label[0][1])])
        movelabel[self.loca2i(label[1][0])][self.loca2i(label[1][1])][layer] = 1

        if fenlist[0][1] == 'b':
            # Rotate
            pass


        # shuffle   random

        return frdpos, frdmove, emypos, movelabel

    def next_batch(self, batch_size):
        '''
        return [data, label] with batched size
        '''
        frdpos = np.zeros((batch_size, 9, 10, 16), dtype=OUT_TYPE) 
        frdmove = np.zeros((batch_size, 9, 10, 16), dtype=OUT_TYPE)
        emypos = np.zeros((batch_size, 9, 10, 16), dtype=OUT_TYPE)
        emymove = np.zeros((batch_size, 9, 10, 16), dtype=OUT_TYPE)
        movelabel = np.zeros((batch_size, 9, 10, 16), dtype=OUT_TYPE)

        for i in range(batch_size):
            line = self.file_object.readline()
            if line != '':
                if line[-5:-1] == 'WIN!':
                    i -= 1
                    continue
            else:
                self.file_object.seek(0, 0)
                line = self.file_object.readline()
            frdpos[i], frdmove[i], emypos[i], movelabel[i] = self.fen2tensor(line)
        return [frdpos, frdmove, emypos], movelabel

def load_data(data_name):
    '''
    return dataset which yeild minibatch data
    '''
    data = Dataset(data_name)
    return data

def visualdata(data):
    print '------------------------'
    for i in range(data.shape[2]):
        print i
        for j in range(data.shape[1]):
            for k in range(data.shape[0]):
                print int(data[k][9 - j][i]),
            print '\n',
        print '\n'
    print '------------------------\n'


if __name__ == '__main__':
    traindata = load_data('../data/out.temp')
    for i in range(1):
        [frdpos, frdmove, emypos], movelabel = traindata.next_batch(1)
        visualdata(frdpos[0])
        visualdata(frdmove[0])
        visualdata(emypos[0])
