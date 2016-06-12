#!/usr/bin/python3
#-*-coding:utf-8-*-

import pickle
import copy
import random
import numpy as np
from tensor2fen import tensor2fen
import genmove

OUT_TYPE = np.float32
chesslayer = {'K':0, 'A':1, 'B':3, 'N':5, 'R':7, 'C':9, 'P':11,
              'k':0, 'a':1, 'b':3, 'n':5, 'r':7, 'c':9, 'p':11}


def gentensor(selfpos, emypos):
    '''
    selfpos, emypos: ndarray [9,10,16]
    return:
        selfmove, emymove, selfprot, selfprot: ndarray [9,10,16]
    '''
    _fen = tensor2fen(selfpos, emypos)
    fen = tensor2fen(selfpos, emypos)
    move = genmove.gen(_fen)
    fen = fen + '\t' + move.replace('\n','\t')
    selfpos, emypos, selfmove, emymove, selfprot, emyprot, movelabel = fen2tensor(fen)
    return [selfmove, emymove, selfprot, emyprot]


def fen2tensor(fen):

    frdpos = np.zeros((9, 10, 16), dtype=OUT_TYPE)
    emypos = np.zeros((9, 10, 16), dtype=OUT_TYPE)
    frdmove = np.zeros((9, 10, 16), dtype=OUT_TYPE)
    emymove = np.zeros((9, 10, 16), dtype=OUT_TYPE)
    frdprot = np.zeros((9, 10, 16), dtype=OUT_TYPE)
    emyprot = np.zeros((9, 10, 16), dtype=OUT_TYPE)
    movelabel = np.zeros((9, 10, 16), dtype=OUT_TYPE)

    fenlist = fen.split('\t')
    frdpos, emypos = f2tpos(fenlist[0], frdpos, emypos)
    frdmove = f2tmove(fenlist[1], frdmove, frdpos)
    emymove = f2tmove(fenlist[3], emymove, emypos)
    frdprot = f2tmove(fenlist[4], frdprot, frdpos)
    emyprot = f2tmove(fenlist[5], emyprot, emypos)

    label = fenlist[2].strip().split('-')
    layer = np.argmax(frdpos[loca2i(label[0][0])][loca2i(label[0][1])])
    movelabel[loca2i(label[1][0])][loca2i(label[1][1])][layer] = 1


    if fenlist[0].split()[1] == 'b':
        switch_round(frdpos)
        switch_round(frdmove)
        switch_round(emypos)
        switch_round(emymove)
        switch_round(movelabel)
        switch_round(frdprot)
        switch_round(emyprot)

    # shuffle random
    shuffle([frdpos, frdmove, frdprot, movelabel], shuffle_args())
    shuffle([emypos, emymove, emyprot], shuffle_args())

    return frdpos, emypos, frdmove, emymove, frdprot, emyprot, movelabel

def f2tpos(fen, frdpos, emypos):
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

def f2tmove(movelist, move, pos):
    movelist = movelist.split()
    for item in movelist:
        src = item.split('-')[0]
        des = item.split('-')[1]
        layer = np.argmax(pos[loca2i(src[0])][loca2i(src[1])])
        move[loca2i(des[0])][loca2i(des[1])][layer] = 1
    return move

def loca2i(loc):
    if loc.isupper():
        return ord(loc)-ord('A')
    else:
        return int(loc)

def switch_round(mat):
    mat = mat[:,::-1,:]

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
        from IPython import embed; embed()
        assert all( (selfmove.sum(axis=2) == new_selfmove.sum(axis=2)).reshape(-1))
        assert all( (emymove.sum(axis=2) == new_emymove.sum(axis=2))).reshape(-1)
        assert all( (selfprot.sum(axis=2) == new_selfport.sum(axis=2))).reshape(-1)
        assert all( (emyprot.sum(axis=2) == new_emyprot.sum(axis=2))).reshape(-1)
