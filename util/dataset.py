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
            frdpos[i], emypos[i], frdmove[i], emymove[i], frdprot[i], emyprot[i], movelabel[i] = fen2tensor(line)
            #print(line)
            frdpos[i+1] = lrturn(frdpos[i])
            emypos[i+1] = lrturn(emypos[i])
            frdmove[i+1] = lrturn(frdmove[i])
            emymove[i+1] = lrturn(emymove[i])
            frdprot[i+1] = lrturn(frdprot[i])
            emyprot[i+1] = lrturn(emyprot[i])
            movelabel[i+1] = lrturn(movelabel[i-1])
            i += 2
        return [frdpos, emypos, frdmove, emymove, frdprot, emyprot], movelabel

def fen2tensor(fen):

    movelabel = np.zeros((9, 10, 16), dtype=OUT_TYPE)

    fenlist = fen.split('\t')
    frdpos, emypos = f2tpos(fenlist[0])
    frdmove = f2tmove(fenlist[1], frdpos)
    emymove = f2tmove(fenlist[3], emypos)
    frdprot = f2tmove(fenlist[4], frdpos)
    emyprot = f2tmove(fenlist[5], emypos)

    #print(fenlist[1])

    label = fenlist[2].strip().split('-')
    layer = np.argmax(frdpos[loca2i(label[0][0])][loca2i(label[0][1])])
    movelabel[loca2i(label[1][0])][loca2i(label[1][1])][layer] = 1

    if fenlist[0].split()[1] == 'b':
        frdpos = switch_round(frdpos)
        frdmove = switch_round(frdmove)
        emypos = switch_round(emypos)
        emymove = switch_round(emymove)
        movelabel = switch_round(movelabel)
        frdprot = switch_round(frdprot)
        emyprot = switch_round(emyprot)

    # shuffle random
    shuffle([frdpos, frdmove, frdprot, movelabel], shuffle_args())
    shuffle([emypos, emymove, emyprot], shuffle_args())

    return frdpos, emypos, frdmove, emymove, frdprot, emyprot, movelabel

def f2tpos(fen):

    # King(帅)*1, Advisor(仕)*2, Bishop(象)*2, kNight(马)*2
    # Rook(车)*2, Cannon(炮)*2, Pawn(兵)*5
    # Upper: red      Lower: black
    chesslayer = {'K':0, 'A':1, 'B':3, 'N':5, 'R':7, 'C':9, 'P':11,
                  'k':0, 'a':1, 'b':3, 'n':5, 'r':7, 'c':9, 'p':11}

    frdpos = np.zeros((9, 10, 16), dtype=OUT_TYPE)
    emypos = np.zeros((9, 10, 16), dtype=OUT_TYPE)

    poslist = fen.split()[0].split('/')
    player = fen.split()[1]
    for i in range(len(poslist)):
        item = poslist[i]
        index = 0
        for j in range(len(item)):
            if item[j].isupper():
                if player == 'w':
                    frdpos[index][i][chesslayer[item[j]]] = 1
                else:
                    emypos[index][i][chesslayer[item[j]]] = 1
                chesslayer[item[j]] += 1
                index += 1
            elif item[j].islower():
                if player == 'w':
                    emypos[index][i][chesslayer[item[j]]] = 1
                else:
                    frdpos[index][i][chesslayer[item[j]]] = 1
                chesslayer[item[j]] += 1
                index += 1
            else:
                index += int(item[j])
    return frdpos, emypos

def f2tmove(movelist, pos):
    move = np.zeros((9, 10, 16), dtype=OUT_TYPE)
    movelist = movelist.split()
    layer = np.argmax(pos, axis=2)
    for item in movelist:
        src = item.split('-')[0]
        des = item.split('-')[1]
        layerindex = layer[loca2i(src[0])][loca2i(src[1])]
        move[loca2i(des[0])][loca2i(des[1])][layerindex] = 1
    return move

def loca2i(loc):
    if loc.isupper():
        return ord(loc)-ord('A')
    else:
        return (9 - int(loc))

def switch_round(mat):
    mat = mat[:,::-1,:]
    return mat

def shuffle(mat, args):
    index = [[1,2],[3,4],[5,6],[7,8],[9,10],[11,12,13,14,15]]
    for item in mat:
        for i in range(len(index)):
            item[:,:,index[i]] = switch_layer(item[:,:,index[i]], args[i])

def switch_layer(mat, args):
    mat_temp = copy.deepcopy(mat)
    assert len(args) == mat.shape[2]
    for k in range(len(args)):
        mat[:,:,k] = mat_temp[:,:,args[k]]
    return mat

def shuffle_args():
    args = []
    for i in range(5):
        a = [0,1]
        random.shuffle(a)
        args.append(a)
    seq = [0,1,2,3,4]
    random.shuffle(seq)
    args.append(seq)
    return args

def lrturn(tensor):
    new = tensor[::-1,:,:]
    return new


def load_data(_type):
    '''
    return dataset which yeild minibatch data
    '''
    data = Dataset('../data', _type)
    return data

def visualdata(data):
    print('------------------------')
    for i in range(data.shape[2]):
        print(i)
        for j in range(data.shape[1]):
            for k in range(data.shape[0]):
                print(int(data[k][j][i]),end='')
            print('\n',end='')
    print('------------------------\n')


if __name__ == '__main__':
    traindata = load_data('validation')
    #traindata = load_data('train')

    for i in range(1):
        [frdpos, emypos, frdmove, emymove, frdprot, emyprot], movelabel = traindata.next_batch(20)

        visualdata(frdpos[0])
        visualdata(frdmove[0])
        visualdata(frdprot[0])

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

