#!/usr/bin/python3
#-*-coding:utf-8-*-
#$File: gentensor.py

import pickle
import copy
import random
import numpy as np
from tensor2fen import tensor2fen
import genmove
from dataset import visualdata

OUT_TYPE = np.float32


def gentensor(selfpos, emypos):
    '''
    selfpos, emypos: ndarray [9,10,16]
    return:
        selfmove, emymove, selfprot, selfprot: ndarray [9,10,16]
    '''
    fen = tensor2fen(selfpos, emypos)
    move = genmove.gen(fen)
    fen = fen + '\t' + move.replace('\n','\t')
    selfpos, emypos, selfmove, emymove, selfprot, emyprot = fen2tensor(fen)
    return [selfmove, emymove, selfprot, emyprot]


def fen2tensor(fen):

    fenlist = fen.split('\t')
    frdpos, emypos = f2tpos(fenlist[0])
    frdmove = f2tmove(fenlist[1], frdpos)
    emymove = f2tmove(fenlist[2], emypos)
    frdprot = f2tmove(fenlist[3], frdpos)
    emyprot = f2tmove(fenlist[4], emypos)

    turn = fenlist[0].split()[1]
    if turn == 'b':
        frdpos = switch_round(frdpos)
        frdmove = switch_round(frdmove)
        emypos = switch_round(emypos)
        emymove = switch_round(emymove)
        frdprot = switch_round(frdprot)
        emyprot = switch_round(emyprot)

    # shuffle random
    shuffle([frdpos, frdmove, frdprot], shuffle_args())
    shuffle([emypos, emymove, emyprot], shuffle_args())

    #from IPython import embed; embed()
    return frdpos, emypos, frdmove, emymove, frdprot, emyprot


def f2tpos(fen):
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


if __name__ == '__main__':

    from dataset import load_data
    dataset = load_data('validation')
    data, label= dataset.next_batch(1000)

    for selfpos, emypos, selfmove, emymove, selfprot, emyprot in zip(*data):
        new_selfmove, new_emymove, new_selfprot, new_emyprot = gentensor(selfpos, emypos)
        #from IPython import embed; embed()
        assert all( (selfmove.sum(axis=2) == new_selfmove.sum(axis=2)).reshape(-1))
        assert all( (emymove.sum(axis=2) == new_emymove.sum(axis=2)).reshape(-1))
        assert all( (selfprot.sum(axis=2) == new_selfprot.sum(axis=2)).reshape(-1))
        assert all( (emyprot.sum(axis=2) == new_emyprot.sum(axis=2)).reshape(-1))

