#!/usr/bin/python3
#-*-coding:utf-8-*-
#$File: dataset.py
#$Date: Sat May  7 10:59:24 2016
#$Author: Like Ma <milkpku[at]gmail[dot]com>

import copy
import random

import numpy as np

OUT_TYPE = np.float32

class Dataset(object):

    def __init__(self, path, _type):
        if _type == 'train':
            self.__file_object = open(path + '/train.fen', 'r')
        if _type == 'validation':
            self.__file_object = open(path + '/valid.fen', 'r')
        self.__chesslayer = {}

    def __init_clayer(self):
        # King(帅)*1, Advisor(仕)*2, Bishop(象)*2, kNight(马)*2
        # Rook(车)*2, Cannon(炮)*2, Pawn(兵)*5
        # Upper: red      Lower: black
        self.__chesslayer = {'K':0, 'A':1, 'B':3, 'N':5, 'R':7, 'C':9, 'P':11,
                             'k':0, 'a':1, 'b':3, 'n':5, 'r':7, 'c':9, 'p':11}

    def next_batch(self, batch_size):
        '''
        return [data, label] with batched size
        '''
        frdpos = np.zeros((batch_size, 9, 10, 16), dtype=OUT_TYPE)
        emypos = np.zeros((batch_size, 9, 10, 16), dtype=OUT_TYPE)
        frdmove = np.zeros((batch_size, 9, 10, 16), dtype=OUT_TYPE)
        emymove = np.zeros((batch_size, 9, 10, 16), dtype=OUT_TYPE)
        frdprot = np.zeros((batch_size, 9, 10, 16), dtype=OUT_TYPE)
        emyprot = np.zeros((batch_size, 9, 10, 16), dtype=OUT_TYPE)
        movelabel = np.zeros((batch_size, 9, 10, 16), dtype=OUT_TYPE)

        i = 0
        while(i < batch_size):
            line = self.__file_object.readline()
            if line != '':
                if line.split('\t')[2] == 'WIN!':
                    continue
            else:
                self.__file_object.seek(0, 0)
                line = self.__file_object.readline()
            frdpos[i], emypos[i], frdmove[i], emymove[i], frdprot[i], emyprot[i], movelabel[i] = self.__fen2tensor(line)
            i += 1
        # return [frdpos, frdmove, emypos, emymove], movelabel
        # return [frdpos, frdmove, emypos, emyprot], movelabel
        return [frdpos, emypos, frdmove, emymove, frdprot, emyprot], movelabel

    def __fen2tensor(self, fen):

        frdpos = np.zeros((9, 10, 16), dtype=OUT_TYPE)
        emypos = np.zeros((9, 10, 16), dtype=OUT_TYPE)
        frdmove = np.zeros((9, 10, 16), dtype=OUT_TYPE)
        emymove = np.zeros((9, 10, 16), dtype=OUT_TYPE)
        frdprot = np.zeros((9, 10, 16), dtype=OUT_TYPE)
        emyprot = np.zeros((9, 10, 16), dtype=OUT_TYPE)
        movelabel = np.zeros((9, 10, 16), dtype=OUT_TYPE)

        fenlist = fen.split('\t')
        frdpos, emypos = self.__f2tpos(fenlist[0], frdpos, emypos)
        frdmove = self.__f2tmove(fenlist[1], frdmove, frdpos)
        emymove = self.__f2tmove(fenlist[3], emymove, emypos)
        frdprot = self.__f2tmove(fenlist[4], frdprot, frdpos)
        emyprot = self.__f2tmove(fenlist[5], emyprot, emypos)

        label = fenlist[2].strip().split('-')
        layer = np.argmax(frdpos[self.__loca2i(label[0][0])][self.__loca2i(label[0][1])])
        movelabel[self.__loca2i(label[1][0])][self.__loca2i(label[1][1])][layer] = 1


        if fenlist[0].split()[1] == 'b':
            self.__switch_round(frdpos)
            self.__switch_round(frdmove)
            self.__switch_round(emypos)
            self.__switch_round(emymove)
            self.__switch_round(movelabel)
            self.__switch_round(frdprot)
            self.__switch_round(emyprot)

        # shuffle   random
        self.__shuffle([frdpos, frdmove, movelabel], self.__shuffle_args())
        self.__shuffle([emypos], self.__shuffle_args())

        return frdpos, emypos, frdmove, emymove, frdprot, emyprot, movelabel

    def __f2tpos(self, fen, frdpos, emypos):
        self.__init_clayer()
        poslist = fen.split()[0].split('/')
        player = fen.split()[1]
        for i in range(len(poslist)):
            item = poslist[9 - i]
            index = 0
            for j in range(len(item)):
                if item[j].isupper():
                    if player == 'w':
                        frdpos[index][i][self.__chesslayer[item[j]]] = 1
                    else:
                        emypos[index][i][self.__chesslayer[item[j]]] = 1
                    self.__chesslayer[item[j]] += 1
                    index += 1
                elif item[j].islower():
                    if player == 'w':
                        emypos[index][i][self.__chesslayer[item[j]]] = 1
                    else:
                        frdpos[index][i][self.__chesslayer[item[j]]] = 1
                    self.__chesslayer[item[j]] += 1
                    index += 1
                else:
                    index += int(item[j])
        return frdpos, emypos

    def __f2tmove(self, movelist, move, pos):
        movelist = movelist.split()
        for item in movelist:
            src = item.split('-')[0]
            des = item.split('-')[1]
            layer = np.argmax(pos[self.__loca2i(src[0])][self.__loca2i(src[1])])
            move[self.__loca2i(des[0])][self.__loca2i(des[1])][layer] = 1
        return move

    def __loca2i(self, loc):
        if loc.isupper():
            return ord(loc)-ord('A')
        else:
            return int(loc)

    def __switch_round(self, mat):
        mat = mat[:,::-1,:]

    def __shuffle(self, mat, args):
        index = [[1,2],[3,4],[5,6],[7,8],[9,10],[11,12,13,14,15]]
        for item in mat:
            for i in range(len(index)):
                item[:,:,index[i]] = self.__switch_layer(item[:,:,index[i]], args[i])

    def __switch_layer(self, mat, args):
        mat_temp = copy.deepcopy(mat)
        assert len(args) == mat.shape[2]
        for k in range(len(args)):
            mat[:,:,k] = mat_temp[:,:,args[k]]
        return mat

    def __shuffle_args(self):
        args = []
        for i in range(5):
            a = [0,1]
            random.shuffle(a)
            args.append(a)
        seq = [0,1,2,3,4]
        random.shuffle(seq)
        args.append(seq)
        return args

def load_data(_type):
    '''
    return dataset which yeild minibatch data
    '''
    data = Dataset('/home/mlk/BetaElephant/data', _type)
    return data

def visualdata(data):
    print('------------------------')
    for i in range(data.shape[2]):
        print(i)
        for j in range(data.shape[1]):
            for k in range(data.shape[0]):
                print(int(data[k][9 - j][i])),
            print('\n'),
        print('\n')
    print('------------------------\n')


if __name__ == '__main__':
    traindata = load_data('validation')

    for i in range(10):
        [frdpos, emypos, frdmov, emymove, frdprot, emyprot], movelabel = traindata.next_batch(10)
        if 0:
            visualdata(frdpos[0])
            visualdata(frdmove[0])
            visualdata(emypos[0])

    for i in range(10):
        [frdpos, emypos, frdmove, emymove, frdprot, emyprot], movelabel = traindata.next_batch(100)
        # from IPython import embed; embed()
        # assert all protected pieces are selfpieces
        assert all((frdprot.sum(axis=3)*frdpos.sum(axis=3)==frdprot.sum(axis=3)).reshape(-1))
        assert all((emyprot.sum(axis=3)*emypos.sum(axis=3)==emyprot.sum(axis=3)).reshape(-1))

        # assert no empty moves
        frdmove = frdmove.reshape(frdmove.shape[0], -1)
        frdmove = frdmove.sum(axis=1)
        assert all(frdmove!=0), print(i, np.argwhere(frdmove==0))
        # assert no piece in the same layer
        frdpos = frdpos.reshape(frdpos.shape[0]*90, -1)
        frdpos = frdpos.sum(axis=1)
        assert all(frdpos < 2), print(i, np.argwhere(frdpos>1))
        emypos = emypos.reshape(emypos.shape[0]*90, -1)
        emypos = emypos.sum(axis=1)
        assert all(emypos < 2), print(i, np.argwhere(emypos>1))

